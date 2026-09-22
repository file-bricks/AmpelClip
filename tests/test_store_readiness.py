import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import check_store_readiness  # noqa: E402
import Ampel6  # noqa: E402


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

    msix_exists = any((ROOT / "releases" / "windowsstore").glob("*.msix"))
    expected_blockers = {"wack_report"} if msix_exists else {"msix_artifact", "wack_report"}
    assert blockers == expected_blockers
    ok_keys = {result.key for result in results if result.status == "ok"}
    assert ok_keys >= {
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
    if msix_exists:
        assert "msix_content" in ok_keys


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
    assert "WACK-XML-Report fehlt noch" in strict.stdout
    assert allowed.returncode == 0


def test_frozen_build_config_path_uses_local_appdata(monkeypatch, tmp_path):
    monkeypatch.setattr(Ampel6.sys, "frozen", True, raising=False)
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.delenv("AMPELCLIP_CONFIG_PATH", raising=False)

    assert Ampel6.resolve_config_path() == tmp_path / "AmpelClip" / "config.json"


def _create_mock_msix(
    target_path: Path,
    manifest_xml: str | None = None,
    include_files: list[str] | None = None,
    executable: str = "AmpelClip.exe",
) -> Path:
    if manifest_xml is None:
        manifest_xml = f"""<?xml version="1.0" encoding="utf-8"?>
<Package xmlns="http://schemas.microsoft.com/appx/manifest/foundation/windows10">
  <Identity Name="{check_store_readiness.EXPECTED_IDENTITY}"
            Publisher="{check_store_readiness.EXPECTED_PUBLISHER}"
            Version="6.0.0.0" />
  <Capabilities>
    <Capability Name="runFullTrust" />
  </Capabilities>
  <Applications>
    <Application Id="AmpelClipApp" Executable="{executable}" EntryPoint="Windows.FullTrustApplication" />
  </Applications>
</Package>"""

    if include_files is None:
        include_files = [
            "AppxBlockMap.xml",
            "[Content_Types].xml",
            executable,
            "assets/Square44x44Logo.png",
            "assets/Square150x150Logo.png",
            "assets/Square50x50Logo.png",
        ]

    target_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target_path, "w") as zf:
        zf.writestr("AppxManifest.xml", manifest_xml.encode("utf-8"))
        for fname in include_files:
            zf.writestr(fname, b"DUMMY_BINARY_DATA_" * 50)
    return target_path


def test_validate_msix_archive_accepts_valid_mock(tmp_path):
    pkg_path = _create_mock_msix(tmp_path / "Test.msix")
    package_info = {
        "identity_name": check_store_readiness.EXPECTED_IDENTITY,
        "publisher": check_store_readiness.EXPECTED_PUBLISHER,
        "version": "6.0.0.0",
        "executable": "AmpelClip.exe",
    }
    results = check_store_readiness._validate_msix_archive(pkg_path, package_info)
    assert not any(r.status == "blocker" for r in results)
    assert any(r.key == "msix_content" and r.status == "ok" for r in results)


def test_validate_msix_archive_rejects_corrupted_file(tmp_path):
    corrupt_path = tmp_path / "Corrupt.msix"
    corrupt_path.write_bytes(b"NOT_A_VALID_ZIP_HEADER_DATA_12345" * 20)
    package_info = {"executable": "AmpelClip.exe"}
    results = check_store_readiness._validate_msix_archive(corrupt_path, package_info)
    blockers = [r for r in results if r.status == "blocker"]
    assert len(blockers) >= 1
    assert "nicht lesbares ZIP" in blockers[0].summary or "corrupt" in blockers[0].summary.lower()


def test_validate_msix_archive_rejects_missing_required_files(tmp_path):
    incomplete_path = tmp_path / "Incomplete.msix"
    with zipfile.ZipFile(incomplete_path, "w") as zf:
        zf.writestr("dummy.txt", b"x" * 600)
    package_info = {"executable": "AmpelClip.exe"}
    results = check_store_readiness._validate_msix_archive(incomplete_path, package_info)
    blockers = [r for r in results if r.status == "blocker"]
    assert any("Pflichtdateien fehlen" in b.summary for b in blockers)


def test_validate_msix_archive_rejects_mismatched_identity(tmp_path):
    bad_manifest = """<?xml version="1.0" encoding="utf-8"?>
<Package xmlns="http://schemas.microsoft.com/appx/manifest/foundation/windows10">
  <Identity Name="Wrong.Identity"
            Publisher="CN=WrongPublisher"
            Version="1.0.0.0" />
  <Capabilities><Capability Name="runFullTrust" /></Capabilities>
  <Applications><Application Id="App" Executable="AmpelClip.exe" /></Applications>
</Package>"""
    pkg_path = _create_mock_msix(tmp_path / "WrongId.msix", manifest_xml=bad_manifest)
    package_info = {
        "identity_name": check_store_readiness.EXPECTED_IDENTITY,
        "publisher": check_store_readiness.EXPECTED_PUBLISHER,
        "version": "6.0.0.0",
        "executable": "AmpelClip.exe",
    }
    results = check_store_readiness._validate_msix_archive(pkg_path, package_info)
    blockers = [r for r in results if r.status == "blocker"]
    assert any("Identity Name Mismatch" in b.summary for b in blockers)
    assert any("Publisher Mismatch" in b.summary for b in blockers)
    assert any("Version Mismatch" in b.summary for b in blockers)


def test_validate_msix_archive_rejects_missing_executable(tmp_path):
    pkg_path = _create_mock_msix(tmp_path / "NoExe.msix", include_files=["AppxBlockMap.xml", "[Content_Types].xml"])
    package_info = {
        "identity_name": check_store_readiness.EXPECTED_IDENTITY,
        "publisher": check_store_readiness.EXPECTED_PUBLISHER,
        "version": "6.0.0.0",
        "executable": "AmpelClip.exe",
    }
    results = check_store_readiness._validate_msix_archive(pkg_path, package_info)
    blockers = [r for r in results if r.status == "blocker"]
    assert any("Haupt-Executable 'AmpelClip.exe' fehlt" in b.summary for b in blockers)


def test_validate_msix_verifies_sha256_checksum(tmp_path):
    pkg_path = _create_mock_msix(tmp_path / "ValidChecksum.msix")
    package_info = {
        "identity_name": check_store_readiness.EXPECTED_IDENTITY,
        "publisher": check_store_readiness.EXPECTED_PUBLISHER,
        "version": "6.0.0.0",
        "executable": "AmpelClip.exe",
    }
    actual_hash = hashlib.sha256(pkg_path.read_bytes()).hexdigest()
    sha_file = tmp_path / "SHA256SUMS.txt"
    sha_file.write_text(f"{actual_hash}  ValidChecksum.msix\n", encoding="utf-8")

    results = check_store_readiness._validate_msix_archive(pkg_path, package_info)
    assert any(r.key == "msix_checksum" and r.status == "ok" for r in results)

    # Test mismatch
    sha_file.write_text(f"{'0' * 64}  ValidChecksum.msix\n", encoding="utf-8")
    results_bad = check_store_readiness._validate_msix_archive(pkg_path, package_info)
    assert any(r.key == "msix_content" and r.status == "blocker" and "SHA256 Mismatch" in r.summary for r in results_bad)


def test_collect_results_skip_msix():
    results = check_store_readiness.collect_results(ROOT, skip_msix=True)
    assert any(r.key == "msix_artifact" and r.status == "warn" for r in results)
    assert not any(r.key == "msix_content" for r in results)


def test_store_readiness_cli_skip_msix():
    res = subprocess.run(
        [sys.executable, "scripts/check_store_readiness.py", "--skip-msix", "--allow-blockers"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert res.returncode == 0
    assert "[WARN] msix_artifact" in res.stdout

