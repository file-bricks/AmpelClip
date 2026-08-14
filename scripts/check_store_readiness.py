"""Windows Store readiness preflight for AmpelClip."""
from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from pathlib import Path
from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[1]
STATUSES = {"ok", "warn", "blocker"}
EXPECTED_PUBLISHER = "CN=52596601-BAB4-4F3F-B182-E8F3F273B202"
EXPECTED_IDENTITY = "Geiger.AmpelClip"


@dataclass(frozen=True)
class CheckResult:
    key: str
    status: str
    summary: str

    def __post_init__(self) -> None:
        if self.status not in STATUSES:
            raise ValueError(f"invalid status: {self.status}")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_json(path: Path) -> tuple[dict, CheckResult]:
    if not path.exists():
        return {}, CheckResult(path.name, "blocker", f"{path.name} fehlt")
    try:
        payload = json.loads(_read_text(path))
    except (OSError, json.JSONDecodeError) as exc:
        return {}, CheckResult(path.name, "blocker", f"{path.name} unlesbar: {exc}")
    return payload, CheckResult(path.name, "ok", f"{path.name} vorhanden")


def _is_placeholder(value: object) -> bool:
    text = str(value or "").strip().lower()
    return not text or "todo" in text or "placeholder" in text or "example." in text


def _check_store_package(root: Path) -> tuple[dict, list[CheckResult]]:
    payload, base_result = _load_json(root / "store_package.json")
    results = [base_result]
    if not payload:
        return payload, results

    required = [
        "app_id",
        "display_name",
        "identity_name",
        "version",
        "publisher",
        "executable",
        "privacy_url",
        "support_url",
        "category",
        "age_rating",
        "capabilities",
    ]
    missing = [key for key in required if not payload.get(key)]
    if missing:
        results.append(
            CheckResult("store_package_fields", "blocker", "Pflichtfelder fehlen: " + ", ".join(missing))
        )
    else:
        results.append(CheckResult("store_package_fields", "ok", "Store-Pflichtfelder gesetzt"))

    if _is_placeholder(payload.get("publisher")) or payload.get("publisher") != EXPECTED_PUBLISHER:
        results.append(
            CheckResult("partner_center_publisher", "blocker", f"Publisher-DN muss '{EXPECTED_PUBLISHER}' sein")
        )
    else:
        results.append(CheckResult("partner_center_publisher", "ok", "Publisher-DN gesetzt"))

    urls = [str(payload.get("privacy_url", "")), str(payload.get("support_url", ""))]
    if all(url.startswith("https://github.com/file-bricks/AmpelClip") for url in urls):
        results.append(CheckResult("public_urls", "ok", "Privacy- und Support-URLs zeigen auf das Projekt"))
    else:
        results.append(CheckResult("public_urls", "blocker", "Privacy-/Support-URLs sind nicht gesetzt"))

    return payload, results


def _check_store_settings(root: Path, store_package: dict) -> list[CheckResult]:
    settings, base_result = _load_json(root / "releases" / "windowsstore" / "store_settings.json")
    results = [base_result]
    if not settings:
        return results

    pairs = {
        "app_name": "display_name",
        "identity_name": "identity_name",
        "version": "version",
        "exe_name": "executable",
        "privacy_url": "privacy_url",
        "support_url": "support_url",
        "category": "category",
        "age_rating": "age_rating",
        "capabilities": "capabilities",
    }
    drift = [
        f"{settings_key}!={package_key}"
        for settings_key, package_key in pairs.items()
        if settings.get(settings_key) != store_package.get(package_key)
    ]
    if drift:
        results.append(CheckResult("store_settings_sync", "blocker", "Drift zu store_package.json: " + ", ".join(drift)))
    else:
        results.append(CheckResult("store_settings_sync", "ok", "Store-Settings sind mit store_package.json synchron"))

    if _is_placeholder(settings.get("publisher")) or settings.get("publisher") != EXPECTED_PUBLISHER:
        results.append(CheckResult("store_settings_publisher", "blocker", f"Store-Settings-Publisher muss '{EXPECTED_PUBLISHER}' sein"))
    else:
        results.append(CheckResult("store_settings_publisher", "ok", "Store-Settings-Publisher gesetzt"))
    return results


def _check_appx_manifest(root: Path) -> list[CheckResult]:
    manifest_path = root / "store_package" / "AmpelClip" / "AppxManifest.xml"
    if not manifest_path.exists():
        return [CheckResult("appx_manifest", "blocker", "store_package/AmpelClip/AppxManifest.xml fehlt")]
    try:
        tree = ET.parse(manifest_path)
        manifest_root = tree.getroot()
        identity = None
        for elem in manifest_root.iter():
            if elem.tag.endswith("Identity"):
                identity = elem
                break
        if identity is None:
            return [CheckResult("appx_manifest", "blocker", "<Identity> in AppxManifest.xml fehlt")]
        if identity.get("Name") != EXPECTED_IDENTITY:
            return [CheckResult("appx_manifest", "blocker", f"Identity Name {identity.get('Name')} != {EXPECTED_IDENTITY}")]
        if identity.get("Publisher") != EXPECTED_PUBLISHER:
            return [CheckResult("appx_manifest", "blocker", f"Identity Publisher != {EXPECTED_PUBLISHER}")]
        return [CheckResult("appx_manifest", "ok", "AppxManifest.xml ist valide mit Partner-Center-Identität")]
    except Exception as exc:
        return [CheckResult("appx_manifest", "blocker", f"Fehler beim Parsen von AppxManifest.xml: {exc}")]


def _check_tile_assets(root: Path) -> list[CheckResult]:
    required_assets = {
        "store_package/AmpelClip/assets/Square44x44Logo.png": (44, 44),
        "store_package/AmpelClip/assets/Square50x50Logo.png": (50, 50),
        "store_package/AmpelClip/assets/Square150x150Logo.png": (150, 150),
        "store_package/AmpelClip/assets/Wide310x150Logo.png": (310, 150),
        "store_package/AmpelClip/assets/Square310x310Logo.png": (310, 310),
        "store_assets/icon_44x44.png": (44, 44),
        "store_assets/icon_50x50.png": (50, 50),
        "store_assets/icon_150x150.png": (150, 150),
        "store_assets/icon_310x150.png": (310, 150),
        "store_assets/icon_310x310.png": (310, 310),
    }
    missing = []
    bad_dim = []
    for rel, dim in required_assets.items():
        p = root / rel
        if not p.exists():
            missing.append(rel)
        else:
            try:
                im = Image.open(p)
                if im.size != dim:
                    bad_dim.append(f"{rel}: {im.size}!={dim}")
            except Exception as e:
                bad_dim.append(f"{rel}: {e}")
    if missing or bad_dim:
        errs = []
        if missing: errs.append("Fehlend: " + ", ".join(missing))
        if bad_dim: errs.append("Falsche Dimension: " + ", ".join(bad_dim))
        return [CheckResult("store_tile_assets", "blocker", "; ".join(errs))]
    return [CheckResult("store_tile_assets", "ok", "Alle Microsoft Store Tile-Icons vorhanden und maßhaltig")]


def _check_store_screenshots(root: Path) -> list[CheckResult]:
    screenshot_dir = root / "screenshots" / "store"
    if not screenshot_dir.exists():
        return [CheckResult("store_screenshots", "blocker", "screenshots/store/ Verzeichnis fehlt")]
    shots = list(screenshot_dir.glob("*.png"))
    if len(shots) < 4:
        return [CheckResult("store_screenshots", "blocker", f"Zu wenige Store-Screenshots ({len(shots)} < 4)")]
    bad_res = []
    for shot in shots:
        try:
            im = Image.open(shot)
            if im.size != (1920, 1080):
                bad_res.append(f"{shot.name}: {im.size} != (1920, 1080)")
        except Exception as e:
            bad_res.append(f"{shot.name}: {e}")
    if bad_res:
        return [CheckResult("store_screenshots", "blocker", "Ungültige Screenshots: " + ", ".join(bad_res))]
    return [CheckResult("store_screenshots", "ok", f"{len(shots)} Store-Screenshots in 1920x1080 vorhanden")]


def _check_docs(root: Path) -> list[CheckResult]:
    required = {
        "STORE_LISTING.md": ["## Deutsch", "## English", "AmpelClip"],
        "PRIVACY_POLICY.md": ["## Deutsch", "## English", "keine Zwischenablageinhalte"],
        "SUPPORT.md": ["## Deutsch", "## English", "GitHub Issues"],
        "releases/windowsstore/WINDOWS_STORE_PREP.md": ["Offene externe Gates", "check_store_readiness.py"],
    }
    results: list[CheckResult] = []
    missing = []
    for rel_path, markers in required.items():
        path = root / rel_path
        if not path.exists():
            missing.append(rel_path)
            continue
        text = _read_text(path)
        absent = [marker for marker in markers if marker not in text]
        if absent:
            results.append(CheckResult(f"doc_{rel_path}", "blocker", "Marker fehlen: " + ", ".join(absent)))
    if missing:
        results.append(CheckResult("store_docs", "blocker", "Store-Dokumente fehlen: " + ", ".join(missing)))
    elif not any(result.status == "blocker" for result in results):
        results.append(CheckResult("store_docs", "ok", "Store-Listing, Privacy, Support und Prep-Notiz vorhanden"))
    return results


def _check_materials(root: Path) -> list[CheckResult]:
    required = [
        "README.md",
        "README_de.md",
        "LICENSE",
        "SECURITY.md",
        "THIRD_PARTY_LICENSES.txt",
        "AmpelTool_V6.spec",
        "build_exe.bat",
        "AmpelClip.ico",
        "AmpelClip.png",
    ]
    missing = [path for path in required if not (root / path).exists()]
    if missing:
        return [CheckResult("runtime_materials", "blocker", "Release-Material fehlt: " + ", ".join(missing))]

    exe_candidates = [
        root / "AmpelClip.exe",
        root / "dist" / "AmpelClip.exe",
        root / "releases" / "v6.0.0" / "AmpelTool_V6.exe",
    ]
    if any(path.exists() for path in exe_candidates):
        return [CheckResult("runtime_materials", "ok", "Runtime-, Icon-, Screenshot- und EXE-Material vorhanden")]
    return [CheckResult("runtime_materials", "warn", "Store-Material vorhanden, aber kein lokales EXE-Artefakt gefunden")]


def _check_desktop_config_path(root: Path) -> list[CheckResult]:
    source = _read_text(root / "Ampel6.py")
    markers = ["resolve_config_path", "LOCALAPPDATA", "CONFIG_PATH.parent.mkdir"]
    missing = [marker for marker in markers if marker not in source]
    if missing:
        return [
            CheckResult(
                "desktop_config_path",
                "blocker",
                "Store-tauglicher Config-Pfad fehlt: " + ", ".join(missing),
            )
        ]
    return [
        CheckResult(
            "desktop_config_path",
            "ok",
            "Frozen-Builds schreiben Konfiguration nach LOCALAPPDATA",
        )
    ]


def _check_secret_guardrails(root: Path) -> list[CheckResult]:
    gitignore = _read_text(root / ".gitignore")
    required_patterns = [
        "LOCK*.txt",
        "config.json",
        ".env",
        "credentials.json",
        "client_secret*.json",
        "token.json",
        "*.db",
        "*.sqlite",
        "*.log",
    ]
    missing = [pattern for pattern in required_patterns if pattern not in gitignore]
    if missing:
        return [CheckResult("secret_ignores", "blocker", "Sensible Muster fehlen in .gitignore: " + ", ".join(missing))]
    return [CheckResult("secret_ignores", "ok", "Config-, Lock-, Secret- und Datenartefakte sind ausgeschlossen")]


def _check_msix_and_wack(root: Path) -> list[CheckResult]:
    msix = list((root / "releases" / "windowsstore").glob("*.msix"))
    wack = list((root / "releases" / "windowsstore").glob("wack_*.xml"))
    results = []
    if msix:
        results.append(CheckResult("msix_artifact", "ok", "MSIX-Artefakt gefunden"))
    else:
        results.append(CheckResult("msix_artifact", "blocker", "MSIX-Artefakt fehlt noch"))
    if wack:
        results.append(CheckResult("wack_report", "ok", "WACK-XML-Report gefunden"))
    else:
        results.append(CheckResult("wack_report", "blocker", "WACK-XML-Report fehlt noch"))
    return results


def collect_results(root: Path = PROJECT_ROOT) -> list[CheckResult]:
    store_package, results = _check_store_package(root)
    results.extend(_check_store_settings(root, store_package))
    results.extend(_check_appx_manifest(root))
    results.extend(_check_tile_assets(root))
    results.extend(_check_store_screenshots(root))
    results.extend(_check_docs(root))
    results.extend(_check_materials(root))
    results.extend(_check_desktop_config_path(root))
    results.extend(_check_secret_guardrails(root))
    results.extend(_check_msix_and_wack(root))
    return results


def summarize(results: list[CheckResult]) -> str:
    counts = {status: sum(1 for result in results if result.status == status) for status in STATUSES}
    overall = "BLOCKED" if counts["blocker"] else "WARN" if counts["warn"] else "OK"
    lines = [f"AmpelClip Store readiness: {overall}"]
    lines.append(f"OK={counts['ok']} WARN={counts['warn']} BLOCKER={counts['blocker']}")
    for result in results:
        lines.append(f"[{result.status.upper()}] {result.key}: {result.summary}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print machine-readable results")
    parser.add_argument(
        "--allow-blockers",
        action="store_true",
        help="Return 0 even while external Partner Center/MSIX/WACK gates remain open",
    )
    args = parser.parse_args(argv)

    results = collect_results()
    has_blocker = any(result.status == "blocker" for result in results)

    if args.json:
        print(json.dumps([asdict(result) for result in results], ensure_ascii=False, indent=2))
    else:
        print(summarize(results))

    if has_blocker and not args.allow_blockers:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
