r"""
Regressionstests für Bugsweep: Builtin-Pattern phone_de (+49-Vorwahl und Wortgrenzen).

Bug BUG-P1: BUILTIN_PATTERNS['phone_de'] verwendete führendes '\b(?:\+49|0049|0)',
was bei '+49' versagte, da '+' ein Nicht-Wort-Zeichen (\W) ist und nach
Leerzeichen/Zeilenanfang keine Wortgrenze (\b) vorliegt. Zudem führte '\b' vor '+'
zu Falsch-Positiven bei alphanumerischen Präfixen (z. B. 'abc+49...').
Behebung: Ersetzung des führenden '\b' durch negativen Lookbehind '(?<!\w)'.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from Ampel6 import AmpelTool, BUILTIN_PATTERNS


def test_phone_de_matches_international_plus49_format():
    """phone_de muss das im Beschreibungstext genannte Format '+49 170 1234567' erkennen."""
    regex = BUILTIN_PATTERNS["phone_de"]["regex"]
    pat = re.compile(regex)

    match = pat.search("+49 170 1234567")
    assert match is not None, "phone_de hat '+49 170 1234567' nicht erkannt"
    assert match.group(0) == "+49 170 1234567"


def test_phone_de_matches_in_context_and_parentheses():
    """phone_de muss Nummern nach Doppelpunkt, Satzzeichen und Klammern erkennen."""
    regex = BUILTIN_PATTERNS["phone_de"]["regex"]
    pat = re.compile(regex)

    m_colon = pat.search("Tel: +49 170 1234567")
    assert m_colon is not None, "phone_de nach 'Tel: ' nicht erkannt"
    assert m_colon.group(0) == "+49 170 1234567"

    m_paren = pat.search("Mobil (+49 151 12345678) erreichbar")
    assert m_paren is not None, "phone_de in Klammern nicht erkannt"
    assert m_paren.group(0) == "+49 151 12345678"


def test_phone_de_matches_national_and_double_zero_formats():
    """phone_de muss weiterhin '0170-1234567' und '0049 30 123456' erkennen."""
    regex = BUILTIN_PATTERNS["phone_de"]["regex"]
    pat = re.compile(regex)

    m_national = pat.search("0170-1234567")
    assert m_national is not None, "Nationales Format 0170-1234567 nicht erkannt"
    assert m_national.group(0) == "0170-1234567"

    m_zero = pat.search("0049 30 123456")
    assert m_zero is not None, "0049-Format nicht erkannt"
    assert m_zero.group(0) == "0049 30 123456"


def test_phone_de_negative_lookbehind_prevents_alphanumeric_prefix():
    """Alphanumerische Zeichen direkt vor +49 dürfen keinen Treffer auslösen (kein Falsch-Positiv)."""
    regex = BUILTIN_PATTERNS["phone_de"]["regex"]
    pat = re.compile(regex)

    assert pat.search("abc+49 170 1234567") is None
    assert pat.search("123+49 151 12345678") is None


def test_anonymize_with_phone_de_masks_plus49():
    """_anonymize muss bei aktivem phone_de '+49'-Telefonnummern durch [ANONYM] ersetzen."""
    tool = AmpelTool.__new__(AmpelTool)
    tool.sensitive = []
    tool.whitelist = []
    tool.case_sensitive = False
    tool.whole_words = False

    flags = re.IGNORECASE
    tool.patterns = [re.compile(BUILTIN_PATTERNS["phone_de"]["regex"], flags)]

    raw_text = "Bitte anrufen unter +49 170 1234567 oder 0170-1234567."
    anonymized = tool._anonymize(raw_text)

    assert "+49 170 1234567" not in anonymized, "+49-Nummer blieb unmaskiert (PII-Leak!)"
    assert "0170-1234567" not in anonymized, "Nationale Nummer blieb unmaskiert"
    assert anonymized == "Bitte anrufen unter [ANONYM] oder [ANONYM]."
