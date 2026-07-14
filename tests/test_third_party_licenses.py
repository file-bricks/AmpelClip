"""Guard AmpelClip's license inventory against dependency drift."""

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def _runtime_dependency_names() -> list[str]:
    names: list[str] = []
    for raw_line in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        match = re.match(r"[A-Za-z0-9_.-]+", line)
        assert match, f"Unlesbare Requirement-Zeile: {raw_line!r}"
        names.append(match.group(0))
    return names


def test_third_party_inventory_covers_declared_runtime_dependencies():
    inventory = (ROOT / "THIRD_PARTY_LICENSES.txt").read_text(encoding="utf-8")

    assert "Checked: 2026-07-14" in inventory
    assert "licensed under MIT according to `LICENSE`" in inventory
    assert "not a frozen transitive SBOM" in inventory

    inventory_lower = inventory.lower()
    for package in _runtime_dependency_names():
        assert f"| {package.lower()} " in inventory_lower

    for package in (
        "PySide6_Addons",
        "PySide6_Essentials",
        "shiboken6",
        "numpy",
        "python-dateutil",
        "tzdata",
        "six",
    ):
        assert f"| {package}" in inventory


def test_web_companion_dependency_claim_matches_package_manifest():
    package = json.loads(
        (ROOT / "web_companion" / "package.json").read_text(encoding="utf-8")
    )
    assert not package.get("dependencies")
    assert not package.get("devDependencies")

    inventory = (ROOT / "THIRD_PARTY_LICENSES.txt").read_text(encoding="utf-8")
    assert "has no `dependencies` or `devDependencies`" in inventory
