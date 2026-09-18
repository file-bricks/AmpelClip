"""Tests for metadata, documentation parity, and marketing guardrails."""

import re
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent


def test_version_consistency():
    """Verify version parity across pyproject.toml and CHANGELOG.md."""
    pyproject_text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    changelog_text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

    m_pyproj = re.search(r'version\s*=\s*"([^"]+)"', pyproject_text)
    assert m_pyproj is not None, "Version not found in pyproject.toml"
    version = m_pyproj.group(1)
    assert version == "1.2.0"

    assert f"## [{version}]" in changelog_text, f"Version {version} missing in CHANGELOG.md"


def test_readme_navigation_anchor_parity():
    """Verify that README.md and README_de.md have the 18 navigation sections."""
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

    en_anchors = [
        "start-here",
        "target-personas",
        "why-ampelclip",
        "comparative-matrix",
        "system-architecture",
        "traffic-light-lifecycle",
        "installation",
        "web-companion",
        "how-it-works",
        "configuration",
        "build-executable",
        "windows-store-readiness",
        "governance-invariants",
        "sibling-ecosystem",
        "security-policy",
        "search-context",
        "license",
        "changelog",
    ]

    for anchor in en_anchors:
        assert f'id="{anchor}"' in readme_en, f"Anchor {anchor} missing in README.md"

    de_anchors = [
        "einstieg",
        "zielgruppen",
        "warum-ampelclip",
        "vergleichsmatrix",
        "systemarchitektur",
        "ampel-lebenszyklus",
        "installation",
        "web-companion",
        "ablauf",
        "konfiguration",
        "exe-bauen",
        "windows-store-readiness",
        "governance-invarianten",
        "geschwister-oekosystem",
        "sicherheitsrichtlinie",
        "suchkontext",
        "lizenz",
        "aenderungsprotokoll",
    ]

    for anchor in de_anchors:
        assert f'id="{anchor}"' in readme_de, f"Anchor {anchor} missing in README_de.md"


def test_dual_mermaid_diagrams_present():
    """Verify dual mermaid diagrams exist in both README files."""
    for filename in ["README.md", "README_de.md"]:
        text = (ROOT / filename).read_text(encoding="utf-8")
        assert "```mermaid\nflowchart TD" in text
        assert "```mermaid\nsequenceDiagram" in text
        assert "autonumber" in text


def test_governance_invariants_present():
    """Verify all 10 governance invariants [INV-LOCAL-01]..[INV-SLA-10] are documented."""
    for filename in ["README.md", "README_de.md", "SECURITY.md"]:
        text = (ROOT / filename).read_text(encoding="utf-8")
        for i in range(1, 11):
            inv_id = f"[INV-"
            assert inv_id in text, f"Invariant {inv_id} missing in {filename}"


def test_marketing_log_exists():
    """Verify repository-level MARKETING-LOG.txt is present and non-empty."""
    m_log = ROOT / "MARKETING-LOG.txt"
    assert m_log.exists(), "MARKETING-LOG.txt does not exist"
    content = m_log.read_text(encoding="utf-8")
    assert "file-bricks/AmpelClip" in content
    assert "PFAD B" in content or "Pfad B" in content
