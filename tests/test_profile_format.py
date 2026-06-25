import json
import re
from datetime import datetime, timezone

import pytest

from Ampel6 import (
    AmpelTool,
    BUILTIN_PATTERNS,
    PROFILE_SCHEMA_VERSION,
    build_profile_export_payload,
    normalize_profile_payload,
    read_profile_payload,
    write_profile_payload,
)


def test_profile_export_payload_contains_only_portable_rules():
    payload = build_profile_export_payload(
        sensitive=["Müller", "Müller", "", " IBAN-Test "],
        whitelist=["Öffentlich", "Öffentlich"],
        builtin_enabled={"iban": False, "email": True, "creditcard": True, "unknown": True},
        ampel_status="gruen",
        case_sensitive=True,
        whole_words=False,
        exported_at=datetime(2026, 6, 1, 8, 30, tzinfo=timezone.utc),
    )

    assert payload["schema_version"] == PROFILE_SCHEMA_VERSION
    assert payload["settings"] == {
        "ampel_status": "gruen",
        "case_sensitive": True,
        "whole_words": False,
    }
    assert payload["lists"]["sensibel"] == ["Müller", "IBAN-Test"]
    assert payload["lists"]["whitelist"] == ["Öffentlich"]
    assert set(payload["builtin_patterns"]) == set(BUILTIN_PATTERNS)
    assert payload["builtin_patterns"]["creditcard"] is True
    assert "unknown" not in payload["builtin_patterns"]

    serialized = json.dumps(payload, ensure_ascii=False)
    assert "Müller" in serialized
    assert "clip_history" not in serialized
    assert "file_history" not in serialized
    assert "C:\\Users" not in serialized


def test_profile_roundtrip_preserves_umlauts(tmp_path):
    path = tmp_path / "ampelclip-profile-v1.json"
    payload = build_profile_export_payload(
        sensitive=["Ärztin", "Konto"],
        whitelist=["Grünfreigabe"],
        builtin_enabled={"iban": True, "email": False},
        ampel_status="gelb",
        case_sensitive=False,
        whole_words=True,
        exported_at="2026-06-01T08:30:00+00:00",
    )

    write_profile_payload(path, payload)

    text = path.read_text(encoding="utf-8")
    assert "Ärztin" in text
    assert "\\u00c4" not in text
    assert read_profile_payload(path) == normalize_profile_payload(payload)


def test_profile_import_normalizes_old_pattern_aliases_and_ignores_history():
    payload = {
        "schema_version": PROFILE_SCHEMA_VERSION,
        "settings": {
            "ampel_status": "gelb",
            "case_sensitive": 1,
            "whole_words": 0,
        },
        "builtin_patterns": {
            "credit_card": True,
            "postal_code_de": True,
            "unknown": True,
        },
        "lists": {
            "sensibel": ["Kundennummer", "Kundennummer", ""],
            "whitelist": ["Freigabe"],
        },
        "clip_history": ["Rohtext darf nicht übernommen werden"],
    }

    normalized = normalize_profile_payload(payload)

    assert normalized["settings"] == {
        "ampel_status": "gelb",
        "case_sensitive": True,
        "whole_words": False,
    }
    assert normalized["builtin_patterns"]["creditcard"] is True
    assert normalized["builtin_patterns"]["postcode_de"] is True
    assert "unknown" not in normalized["builtin_patterns"]
    assert normalized["lists"]["sensibel"] == ["Kundennummer"]
    assert "clip_history" not in normalized


def test_profile_import_rejects_wrong_schema():
    with pytest.raises(ValueError, match="Nicht unterstütztes Profilformat"):
        normalize_profile_payload({"schema_version": "ampelclip-profile-v2"})


def test_whitelist_preserves_builtin_regex_matches():
    tool = AmpelTool.__new__(AmpelTool)
    tool.whitelist = ["kontakt@firma.de"]
    tool.case_sensitive = False
    tool.whole_words = False
    tool.patterns = [re.compile(BUILTIN_PATTERNS["email"]["regex"], re.IGNORECASE)]

    result = tool._anonymize("kontakt@firma.de und intern@firma.de")

    assert result == "kontakt@firma.de und [ANONYM]"


def test_whitelist_substring_does_not_split_sensitive_builtin_match():
    tool = AmpelTool.__new__(AmpelTool)
    tool.whitelist = ["3704"]
    tool.case_sensitive = False
    tool.whole_words = False
    tool.patterns = [re.compile(BUILTIN_PATTERNS["iban"]["regex"], re.IGNORECASE)]

    result = tool._anonymize("Konto DE89 3704 0044 0532 0130 00 prüfen")

    assert "[ANONYM]" in result
    assert "DE89" not in result
    assert "3704" not in result
    assert "0044" not in result


def test_stale_span_multi_pattern_regression():
    """Regression: protected_spans müssen nach jeder Pattern-Substitution neu berechnet
    werden, damit PLZ/andere Patterns nicht fälschlich von verschobenen Whitelist-Spans
    verdeckt werden (Privacy-Leak im GRÜN-Modus).
    """
    tool = AmpelTool.__new__(AmpelTool)
    tool.whitelist = ["foo@bar.de"]
    tool.case_sensitive = False
    tool.whole_words = False
    # Zwei Patterns: Email zuerst, dann Postleitzahl
    tool.patterns = [
        re.compile(BUILTIN_PATTERNS["email"]["regex"], re.IGNORECASE),
        re.compile(BUILTIN_PATTERNS["postcode_de"]["regex"], re.IGNORECASE),
    ]

    result = tool._anonymize("secret@evil.com foo@bar.de 12345")

    # foo@bar.de (whitelist) bleibt; secret@evil.com und 12345 werden anonymisiert
    assert "foo@bar.de" in result, "Whitelisted email muss erhalten bleiben"
    assert "[ANONYM]" in result, "Sensitive email muss anonymisiert werden"
    assert "12345" not in result, "PLZ darf nicht durch stale whitelist-span geschützt werden"
