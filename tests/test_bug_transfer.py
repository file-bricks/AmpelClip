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


# ---------------------------------------------------------------------------
# Bugsweep 2026-06-23 (Desktop, /bugsweep-Loop Run 4/15)
# ---------------------------------------------------------------------------
from Ampel6 import read_first_column_values, BUILTIN_PATTERNS  # noqa: E402

_BS_SRC = (Path(__file__).parent.parent / "Ampel6.py").read_text(encoding="utf-8")


def test_bs_txt_cp1252_fallback(tmp_path):
    """read_first_column_values darf cp1252/Latin-1-Listen nicht still verwerfen
    (vorher: read_text(utf-8) -> UnicodeDecodeError -> Liste lautlos leer)."""
    p = tmp_path / "sens.txt"
    p.write_bytes("Müller\nStraße\n".encode("cp1252"))
    values = read_first_column_values(p)
    assert "Müller" in values and "Straße" in values


def test_bs_txt_strips_bom(tmp_path):
    """UTF-8-BOM darf nicht am ersten Begriff kleben (utf-8-sig)."""
    p = tmp_path / "bom.txt"
    p.write_bytes(b"\xef\xbb\xbfBegriff\n")
    values = read_first_column_values(p)
    assert values and values[0] == "Begriff"


def test_bs_xlsx_suffix_case_insensitive():
    """.XLSX (Grossschreibung) muss als Excel erkannt werden, nicht als Text."""
    assert 'path.suffix.lower() == ".xlsx"' in _BS_SRC


def test_bs_email_regex_no_literal_pipe():
    """E-Mail-TLD-Klasse darf kein literales '|' enthalten."""
    assert "[A-Z|a-z]" not in _BS_SRC
    assert BUILTIN_PATTERNS["email"]["regex"].endswith(r"[A-Za-z]{2,}\b")


def test_bs_save_config_atomic():
    """_save_config muss atomar schreiben (tmp + replace), nicht direkt aufs Ziel."""
    assert "tmp.replace(CONFIG_PATH)" in _BS_SRC
    assert 'open(CONFIG_PATH, "w"' not in _BS_SRC


def test_bs_config_load_per_entry_guard():
    """Ein fehlerhafter files-Eintrag darf nicht das ganze Config-Laden abbrechen."""
    assert "isinstance(entry, (list, tuple)) and len(entry) == 2" in _BS_SRC


def test_bs_ampel_status_validated_on_load():
    """ampel_status aus der Config muss validiert werden (_normalized_ampel_status)."""
    assert '_normalized_ampel_status(cfg.get("ampel_status"))' in _BS_SRC


def test_bs_tray_availability_checked():
    """_setup_tray muss isSystemTrayAvailable() pruefen und _tray_available setzen."""
    assert "isSystemTrayAvailable()" in _BS_SRC
    assert "_tray_available" in _BS_SRC
