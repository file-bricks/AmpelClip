"""Tests für TranslationSystem._is_german Umlaut-Erkennung."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from translator import TranslationSystem


def _make_ts(tmp_path):
    return TranslationSystem("de", app_dir=tmp_path)


def test_is_german_detects_umlauts(tmp_path):
    """Strings mit echten Umlauten werden als deutsch erkannt."""
    ts = _make_ts(tmp_path)
    assert ts._is_german("Ärztin")
    assert ts._is_german("Öffentlich")
    assert ts._is_german("Grünfreigabe")
    assert ts._is_german("straße")
    assert ts._is_german("Müller")


def test_is_german_does_not_flag_english(tmp_path):
    """Regression: ASCII-Umlaut-Mangling ('aeoeueAeOeUess') flaggt fast jeden
    englischen String fälschlich als deutsch — jetzt wird die echte Umlaut-Zeichenkette
    'äöüÄÖÜß' geprüft, sodass reine ASCII-Englisch-Strings nicht mehr matchen.
    """
    ts = _make_ts(tmp_path)
    # Diese Wörter enthalten a/e/o/u/s (alle wären von der alten Logik getroffen)
    # aber keine deutschen Umlaute und keinen deutschen Hint-Begriff
    assert not ts._is_german("hello")
    assert not ts._is_german("yes")
    assert not ts._is_german("open")
    assert not ts._is_german("test")
    assert not ts._is_german("file")
    assert not ts._is_german("close")
    assert not ts._is_german("reset")
    assert not ts._is_german("data")


def test_is_german_hint_words_still_work(tmp_path):
    """Bekannte deutsche Schlüsselwörter (Hints) werden weiterhin erkannt."""
    ts = _make_ts(tmp_path)
    assert ts._is_german("Datei öffnen")
    assert ts._is_german("Filter")
    assert ts._is_german("Import")
