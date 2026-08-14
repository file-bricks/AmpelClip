import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import check_store_readiness
import Ampel6


def test_store_package_and_settings_stay_in_sync():
    package = json.loads((ROOT / "store_package.json").read_text(encoding="utf-8"))
    settings = json.loads(
        (ROOT / "releases" / "windowsstore" / "store_settings.json").read_text(encoding="utf-8")
    )

    assert settings["app_name"] == package["display_name"]
    assert settings["identity_name"] == package["identity_name"]
    assert settings["version"] == package["version"]
    assert settings["exe_name"] == package["executable"]
    assert settings["privacy_url"] == package["privacy_url"]
    assert settings["support_url"] == package["support_url"]
    assert settings["capabilities"] == package["capabilities"]
    assert package["capabilities"] == "runFullTrust"
    assert "config.json" in package["forbidden_release_files"]
    assert package["publisher"] == "CN=52596601-BAB4-4F3F-B182-E8F3F273B202"
    assert settings["publisher"] == "CN=52596601-BAB4-4F3F-B182-E8F3F273B202"


def test_store_readiness_has_only_expected_external_blockers():
    results = check_store_readiness.collect_results(ROOT)
    blockers = {result.key for result in results if result.status == "blocker"}

    assert blockers == {
        "msix_artifact",
        "wack_report",
    }
    assert {result.key for result in results if result.status == "ok"} >= {
        "store_package.json",
        "store_package_fields",
        "partner_center_publisher",
        "public_urls",
        "store_settings.json",
        "store_settings_sync",
        "store_settings_publisher",
        "appx_manifest",
        "store_tile_assets",
        "store_screenshots",
        "store_docs",
        "runtime_materials",
        "desktop_config_path",
        "secret_ignores",
    }


def test_store_readiness_cli_reports_blocked_but_allows_known_gates():
    strict = subprocess.run(
        [sys.executable, "scripts/check_store_readiness.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    allowed = subprocess.run(
        [sys.executable, "scripts/check_store_readiness.py", "--allow-blockers"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert strict.returncode == 2
    assert "AmpelClip Store readiness: BLOCKED" in strict.stdout
    assert "MSIX-Artefakt fehlt noch" in strict.stdout
    assert allowed.returncode == 0


def test_frozen_build_config_path_uses_local_appdata(monkeypatch, tmp_path):
    monkeypatch.setattr(Ampel6.sys, "frozen", True, raising=False)
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.delenv("AMPELCLIP_CONFIG_PATH", raising=False)

    assert Ampel6.resolve_config_path() == tmp_path / "AmpelClip" / "config.json"
