import json
from datetime import datetime, timezone

import pytest

from Ampel6 import (
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
