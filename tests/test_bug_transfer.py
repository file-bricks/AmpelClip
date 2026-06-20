"""
Regressionstests für bugfix-library-transfer Batch #2 (2026-06-20).

BUG-D1: QMenu ohne Parent-Widget → GC-Crash
BUG-U2: json.load in manage_translations ohne JSONDecodeError/OSError-Handler
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


# ---------------------------------------------------------------------------
# BUG-D1: QMenu muss als self._tray_menu mit Parent angelegt werden
# ---------------------------------------------------------------------------

def test_d1_tray_menu_uses_instance_attribute():
    """_setup_tray darf kein QMenu() ohne Parent als lokale Variable erzeugen."""
    source = (Path(__file__).parent.parent / "Ampel6.py").read_text(encoding="utf-8")
    assert "tray_menu = QMenu()" not in source, (
        "BUG-D1: QMenu() ohne Parent gefunden — GC-Crash möglich"
    )


def test_d1_tray_menu_stored_as_self():
    """_setup_tray muss self._tray_menu = QMenu(self) verwenden."""
    source = (Path(__file__).parent.parent / "Ampel6.py").read_text(encoding="utf-8")
    assert "self._tray_menu = QMenu(self)" in source, (
        "BUG-D1: self._tray_menu = QMenu(self) nicht gefunden"
    )


def test_d1_set_context_menu_uses_self_attribute():
    """setContextMenu muss self._tray_menu übergeben bekommen."""
    source = (Path(__file__).parent.parent / "Ampel6.py").read_text(encoding="utf-8")
    assert "self.tray_icon.setContextMenu(self._tray_menu)" in source, (
        "BUG-D1: setContextMenu referenziert nicht self._tray_menu"
    )


# ---------------------------------------------------------------------------
# BUG-U2: manage_translations.py — json.load ohne JSONDecodeError/OSError
# ---------------------------------------------------------------------------

def test_u2_manage_translations_handles_json_decode_error(tmp_path):
    """manage_translations() darf bei korrupter JSON-Datei nicht abstürzen."""
    import manage_translations as mt

    corrupt_json = tmp_path / "locales" / "translations.json"
    corrupt_json.parent.mkdir(parents=True)
    corrupt_json.write_text("{nicht: valides json", encoding="utf-8")

    # Muss ohne Exception durchlaufen — korrupte Datei → leeres Dict
    try:
        mt.manage_translations(str(tmp_path))
    except (json.JSONDecodeError, OSError) as exc:
        pytest.fail(f"BUG-U2: manage_translations wirft unbehandelte Exception: {exc}")


def test_u2_manage_translations_handles_oserror(tmp_path, monkeypatch):
    """manage_translations() darf bei OSError auf der JSON-Datei nicht abstürzen."""
    import manage_translations as mt

    trans_file = tmp_path / "locales" / "translations.json"
    trans_file.parent.mkdir(parents=True)
    trans_file.write_text("{}", encoding="utf-8")

    original_open = open

    def patched_open(path, *args, **kwargs):
        if str(path) == str(trans_file):
            raise OSError("simulierter Lesefehler")
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr("builtins.open", patched_open)

    try:
        mt.manage_translations(str(tmp_path))
    except OSError as exc:
        pytest.fail(f"BUG-U2: manage_translations wirft unbehandelte OSError: {exc}")
