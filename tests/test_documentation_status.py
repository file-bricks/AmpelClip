"""Contracts that keep public and control documentation on current evidence."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_contributing_uses_canonical_repository_and_current_checks():
    text = _read("CONTRIBUTING.md")

    assert "https://github.com/file-bricks/AmpelClip.git" in text
    assert "lukisch/AmpelClip" not in text
    assert "python -m pytest -q" in text
    assert "npm test" in text


def test_web_companion_is_documented_as_implemented_with_acceptance_boundary():
    text = _read("web_companion/README.md")

    assert "als lokale Progressive Web App implementiert" in text
    assert "npm test" in text
    assert "Browser-/Geräteversion" in text
    assert "#31" in text
    assert "Planungsplatzhalter" not in text


def test_english_and_german_readmes_share_store_and_pwa_boundaries():
    english = _read("README.md")
    german = _read("README_de.md")

    assert "publisher DN is configured" in english
    assert "Publisher-DN ist" in german and "gesetzt" in german
    assert "unsigned" in english and "nicht durch den Eigentümer freigegeben" in german
    assert "WACK" in english and "WACK" in german
    assert "real desktop or mobile browser" in english
    assert "realen Desktop- oder" in german and "Mobilbrowser" in german


def test_llms_and_store_notes_distinguish_presence_from_release_evidence():
    llms = _read("llms.txt")
    store = _read("releases/windowsstore/WINDOWS_STORE_PREP.md")

    assert "Last-checked: 2026-09-05" in llms
    assert "No signing, WACK acceptance" in llms
    assert "NotSigned" in store
    assert "Freigabe dieses Dirty Slice" in store
    assert "WACK" in store
    assert "Einreichung im Microsoft Partner Center" in store


def test_german_documents_use_real_umlauts_without_mojibake():
    text = "\n".join(
        _read(path)
        for path in (
            "README_de.md",
            "PORTIERUNGSPLAN.md",
            "AUFGABEN.txt",
            "releases/windowsstore/WINDOWS_STORE_PREP.md",
            "web_companion/README.md",
        )
    )

    assert all(character not in text for character in ("Ã", "�"))
    assert all(word in text for word in ("für", "prüfen", "können"))
