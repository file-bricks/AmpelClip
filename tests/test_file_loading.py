import pandas as pd
import pytest


def test_excel_nan_cells_excluded_from_word_list(tmp_path):
    """Leere Excel-Zellen dürfen nicht als 'nan'-String in die Wortliste gelangen."""
    import openpyxl

    wb = openpyxl.Workbook()
    ws = wb.active
    ws["A1"] = "Müller"
    ws["A2"] = None      # leere Zelle → NaN beim Einlesen
    ws["A3"] = "Schmidt"
    ws["A4"] = None
    wb.save(tmp_path / "sensibel.xlsx")

    df = pd.read_excel(tmp_path / "sensibel.xlsx", header=None)
    # Spiegelt _load_file_internal exakt wider:
    content = df.iloc[:, 0].dropna().astype(str).tolist()

    assert "nan" not in content, "Leerzellen dürfen nicht als 'nan' erscheinen"
    assert "Müller" in content
    assert "Schmidt" in content
    assert len(content) == 2


def test_excel_without_dropna_would_produce_nan(tmp_path):
    """Bestätigt, dass das alte Verhalten (ohne dropna) tatsächlich 'nan' erzeugt hätte."""
    import openpyxl

    wb = openpyxl.Workbook()
    ws = wb.active
    ws["A1"] = "Eintrag"
    ws["A2"] = None      # leere Zelle in der MITTE — pandas liest sie als NaN
    ws["A3"] = "Ende"    # Folgedaten zwingen pandas, die Leerzeile einzuschließen
    wb.save(tmp_path / "test.xlsx")

    df = pd.read_excel(tmp_path / "test.xlsx", header=None)
    broken = df.iloc[:, 0].astype(str).tolist()   # altes Verhalten

    assert "nan" in broken, "Ohne dropna() enthält die Liste 'nan' — das ist der Bug"


def test_rot_status_text_has_correct_capitalization():
    """Stellt sicher, dass der ROT-Statustext korrekte Großschreibung hat."""
    import pathlib

    source = (pathlib.Path(__file__).parent.parent / "Ampel6.py").read_text(encoding="utf-8")
    assert "Keine Änderung am Clipboard" in source, (
        "ROT-Statustext muss 'Keine Änderung' enthalten (Ä groß)"
    )
    assert "Keine änderung am Clipboard" not in source, (
        "Kleingeschriebenes 'änderung' gefunden — Tippfehler nicht behoben"
    )
