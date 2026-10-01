import builtins
from concurrent.futures import ThreadPoolExecutor
import io
import json
from pathlib import Path
import threading
from types import SimpleNamespace

import pytest
import Ampel6 as app


def tool():
    return SimpleNamespace(file_history=[], ampel_status='rot', case_sensitive=False,
                           whole_words=False, builtin_enabled={'email':True},
                           sensitive=['Müller', 'Ärztin'], whitelist=['Öffentlich'])


class PartialWriter:
    def __init__(self, wrapped):
        self.wrapped = wrapped
    def __getattr__(self, name):
        return getattr(self.wrapped, name)
    def __enter__(self):
        self.wrapped.__enter__()
        return self
    def __exit__(self, *args):
        return self.wrapped.__exit__(*args)
    def write(self, text):
        self.wrapped.write(text[:3])
        self.wrapped.flush()
        raise OSError('partial write failure')


def break_writes(monkeypatch):
    for module in (builtins, io):
        original = module.open
        def opener(file, mode='r', *args, _original=original, **kwargs):
            stream = _original(file, mode, *args, **kwargs)
            return PartialWriter(stream) if 'w' in mode else stream
        monkeypatch.setattr(module, 'open', opener)


def test_config_save_preserves_foreign_fixed_temp(tmp_path, monkeypatch):
    config = tmp_path/'config.json'
    other = config.with_suffix('.tmp')
    other.write_bytes(b'FOREIGN-TEMP')
    monkeypatch.setattr(app, 'CONFIG_PATH', config)
    app.AmpelTool._save_config(tool())
    assert other.read_bytes() == b'FOREIGN-TEMP'
    assert json.loads(config.read_text())['ampel_status'] == 'rot'


@pytest.mark.parametrize('kind', ['profile', 'list', 'config'])
def test_partial_writes_preserve_previous_file(tmp_path, monkeypatch, kind):
    target = tmp_path/(kind+'.json')
    target.write_bytes(b'ORIGINAL')
    monkeypatch.setattr(app, 'CONFIG_PATH', target)
    monkeypatch.setattr(app.QFileDialog, 'getSaveFileName', lambda *a: (str(target), ''))
    errors = []
    monkeypatch.setattr(app.QMessageBox, 'critical', lambda *a: errors.append(a))
    break_writes(monkeypatch)
    if kind == 'profile':
        with pytest.raises(OSError, match='partial write failure'):
            app.write_profile_payload(target, {'lists': {'sensibel':['Müller']}})
    elif kind == 'list':
        app.AmpelTool._export_list(tool(), 'sensibel')
        assert errors
    else:
        app.AmpelTool._save_config(tool())
    assert target.read_bytes() == b'ORIGINAL'
    assert sorted(p.name for p in tmp_path.iterdir()) == [target.name]


@pytest.mark.parametrize('kind', ['profile', 'config', 'list'])
def test_replace_failure_preserves_previous_file(tmp_path, monkeypatch, kind):
    target = tmp_path/(kind+'.json')
    target.write_bytes(b'ORIGINAL')
    monkeypatch.setattr(app, 'CONFIG_PATH', target)
    monkeypatch.setattr(app.QFileDialog, 'getSaveFileName', lambda *a: (str(target), ''))
    errors = []
    monkeypatch.setattr(app.QMessageBox, 'critical', lambda *a: errors.append(a))
    def denied(*args):
        raise PermissionError('publication denied')
    monkeypatch.setattr(Path, 'replace', denied)
    if kind == 'profile':
        with pytest.raises(PermissionError, match='publication denied'):
            app.write_profile_payload(target, {'value':'Müller'})
    elif kind == 'config':
        app.AmpelTool._save_config(tool())
    else:
        app.AmpelTool._export_list(tool(), 'sensibel')
        assert errors
    assert target.read_bytes() == b'ORIGINAL'
    assert sorted(p.name for p in tmp_path.iterdir()) == [target.name]


def test_concurrent_config_saves_use_separate_staging_files(tmp_path, monkeypatch, caplog):
    target = tmp_path/'config.json'
    monkeypatch.setattr(app, 'CONFIG_PATH', target)
    gate = threading.Barrier(2)
    per_thread = threading.local()
    class StagedWriter(PartialWriter):
        def write(self, text):
            result = self.wrapped.write(text)
            if not getattr(per_thread, 'synced', False):
                per_thread.synced = True
                gate.wait(timeout=10)
            return result
    for module in (builtins, io):
        original = module.open
        def opener(file, mode='r', *args, _original=original, **kwargs):
            stream = _original(file, mode, *args, **kwargs)
            return StagedWriter(stream) if 'w' in mode else stream
        monkeypatch.setattr(module, 'open', opener)
    original_replace = Path.replace
    staged = []
    def publish(path, destination):
        staged.append(path)
        return original_replace(path, destination)
    monkeypatch.setattr(Path, 'replace', publish)
    with ThreadPoolExecutor(max_workers=2) as pool:
        first, second = tool(), tool()
        second.ampel_status = 'gelb'
        list(pool.map(app.AmpelTool._save_config, [first,second]))
    assert len(set(staged)) == 2
    assert not [record for record in caplog.records if 'Config Save Error' in record.message]
    assert json.loads(target.read_text())['ampel_status'] in ('rot','gelb')
    assert sorted(p.name for p in tmp_path.iterdir()) == [target.name]


def test_list_export_preserves_utf8(tmp_path, monkeypatch):
    target = tmp_path/'sensibel.txt'
    monkeypatch.setattr(app.QFileDialog, 'getSaveFileName', lambda *a: (str(target), ''))
    app.AmpelTool._export_list(tool(), 'sensibel')
    assert target.read_text(encoding='utf-8') == 'Müller\nÄrztin'


def test_serialization_failure_preserves_profile(tmp_path):
    target = tmp_path/'profile.json'
    target.write_bytes(b'ORIGINAL')
    with pytest.raises(TypeError):
        app.write_profile_payload(target, {'bad':object()})
    assert target.read_bytes() == b'ORIGINAL'
    assert sorted(p.name for p in tmp_path.iterdir()) == [target.name]


def test_cleanup_failure_preserves_primary_error(tmp_path, monkeypatch, caplog):
    target = tmp_path/'profile.json'
    target.write_bytes(b'ORIGINAL')
    primary = PermissionError('publication denied')
    def deny_replace(*args):
        raise primary
    def deny_unlink(*args, **kwargs):
        raise OSError('cleanup denied')
    with monkeypatch.context() as patch:
        patch.setattr(Path, 'replace', deny_replace)
        patch.setattr(Path, 'unlink', deny_unlink)
        with pytest.raises(PermissionError) as raised:
            app.write_profile_payload(target, {'value':'Müller'})
    assert raised.value is primary
    assert target.read_bytes() == b'ORIGINAL'
    assert any('temporäre Datei' in r.message for r in caplog.records)


def test_foreign_replacement_of_staging_file_is_preserved(tmp_path, monkeypatch):
    target = tmp_path/'profile.json'
    target.write_bytes(b'ORIGINAL')
    primary = PermissionError('publication denied')
    replacements=[]
    def replace_stage(path, destination):
        # Keep the original inode alive to avoid inode reuse in this fixture.
        path.rename(tmp_path/'owned-stage-detached')
        path.write_bytes(b'FOREIGN')
        replacements.append(path)
        raise primary
    monkeypatch.setattr(Path, 'replace', replace_stage)
    with pytest.raises(PermissionError) as raised:
        app.write_profile_payload(target, {'value':'Müller'})
    assert raised.value is primary
    assert target.read_bytes() == b'ORIGINAL'
    assert replacements[0].read_bytes() == b'FOREIGN'


def test_cleanup_and_logging_failure_keep_primary_error(tmp_path, monkeypatch):
    target = tmp_path/'profile.json'
    target.write_bytes(b'ORIGINAL')
    primary = PermissionError('publication denied')
    def deny_replace(*args):
        raise primary
    def deny_cleanup(*args, **kwargs):
        raise OSError('cleanup denied')
    def fail_logger(*args, **kwargs):
        raise RuntimeError('logger failed')
    with monkeypatch.context() as patch:
        patch.setattr(Path, 'replace', deny_replace)
        patch.setattr(Path, 'unlink', deny_cleanup)
        patch.setattr(app.logging, 'warning', fail_logger)
        with pytest.raises(PermissionError) as raised:
            app.write_profile_payload(target, {'value':'Müller'})
    assert raised.value is primary
    assert target.read_bytes() == b'ORIGINAL'


def test_profile_permission_failure_keeps_readonly_target(tmp_path):
    import os
    import stat
    if os.name != 'nt':
        pytest.skip('Windows replacement semantics')
    target = tmp_path/'profile.json'
    target.write_bytes(b'ORIGINAL')
    target.chmod(stat.S_IREAD)
    try:
        with pytest.raises(PermissionError):
            app.write_profile_payload(target, {'value':'Müller'})
        assert target.read_bytes() == b'ORIGINAL'
        assert sorted(p.name for p in tmp_path.iterdir()) == [target.name]
    finally:
        target.chmod(stat.S_IREAD | stat.S_IWRITE)
