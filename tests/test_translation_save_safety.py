import json
from pathlib import Path
import subprocess
import sys

import pytest
import manage_translations as scanner
from test_save_safety import break_writes


def catalog(tmp_path):
    path = tmp_path/'locales'/'translations.json'
    path.parent.mkdir()
    path.write_text(json.dumps({'Bestehender Text':{'de':'Bestehender Text','en':'Existing text'}},
                               ensure_ascii=False), encoding='utf-8')
    return path


def test_success_keeps_manual_translation_and_adds_new_string(tmp_path):
    path = catalog(tmp_path)
    (tmp_path/'example.py').write_text('QLabel("Datei öffnen")', encoding='utf-8')
    assert scanner.manage_translations(str(tmp_path)) is True
    content = json.loads(path.read_text(encoding='utf-8'))
    assert content['Bestehender Text']['en'] == 'Existing text'
    assert content['Datei öffnen'] == {'de':'Datei öffnen','en':''}
    assert list(path.parent.iterdir()) == [path]


@pytest.mark.parametrize('exists', [False, True])
def test_partial_catalog_write_preserves_previous_state(tmp_path, monkeypatch, exists):
    path = catalog(tmp_path)
    previous = path.read_bytes()
    if not exists:
        path.unlink()
    break_writes(monkeypatch)
    assert scanner.manage_translations(str(tmp_path)) is False
    if exists:
        assert path.read_bytes() == previous
    else:
        assert not path.exists()
    assert list(path.parent.iterdir()) == ([path] if exists else [])


def test_catalog_replace_failure_preserves_manual_translations(tmp_path, monkeypatch):
    path = catalog(tmp_path)
    previous = path.read_bytes()
    def denied(*args):
        raise PermissionError('publication denied')
    monkeypatch.setattr(Path, 'replace', denied)
    assert scanner.manage_translations(str(tmp_path)) is False
    assert path.read_bytes() == previous
    assert list(path.parent.iterdir()) == [path]


@pytest.mark.parametrize('invalid', ['[]', '{"bad":null}', '{broken'])
def test_invalid_catalog_is_preserved_and_cli_reports_failure(tmp_path, invalid):
    path = catalog(tmp_path)
    path.write_text(invalid, encoding='utf-8')
    process = subprocess.run([sys.executable, scanner.__file__, str(tmp_path)],
                             capture_output=True, text=True, encoding='utf-8')
    assert process.returncode == 1
    assert 'bleibt erhalten' in process.stderr
    assert path.read_text(encoding='utf-8') == invalid
    assert list(path.parent.iterdir()) == [path]


def test_cli_success_reports_zero_and_writes_valid_catalog(tmp_path):
    path = catalog(tmp_path)
    process = subprocess.run([sys.executable, scanner.__file__, str(tmp_path)],
                             capture_output=True, text=True, encoding='utf-8')
    assert process.returncode == 0
    assert json.loads(path.read_text(encoding='utf-8'))['Bestehender Text']['en'] == 'Existing text'


@pytest.mark.parametrize('content', [b'\xff\xfe\x80', b'{"Text":{"en":"\\ud800"}}'])
def test_catalog_encoding_errors_return_false_without_changing_bytes(tmp_path, content):
    path = catalog(tmp_path)
    path.write_bytes(content)
    assert scanner.manage_translations(str(tmp_path)) is False
    assert path.read_bytes() == content
    assert list(path.parent.iterdir()) == [path]
