"""
Tests für Windows-Store-Artefakte und -Materialien in AmpelClip.
Prüft Vollständigkeit, Konsistenz, Bildauflösungen und Richtlinienkonformität der Store-Metadaten.
"""
import json
import subprocess
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PUBLISHER = "CN=52596601-BAB4-4F3F-B182-E8F3F273B202"
EXPECTED_IDENTITY = "Geiger.AmpelClip"


class TestStoreMaterials(unittest.TestCase):

    def test_store_package_json_exists_and_is_valid(self):
        path = PROJECT_ROOT / "store_package.json"
        self.assertTrue(path.exists(), "store_package.json fehlt")
        data = json.loads(path.read_text(encoding="utf-8"))
        required = [
            "app_name", "publisher", "publisher_display", "identity_name",
            "version", "description", "executable", "capabilities",
            "category", "age_rating", "privacy_url", "support_url", "languages"
        ]
        for field in required:
            self.assertIn(field, data, f"Pflichtfeld '{field}' fehlt in store_package.json")

    def test_store_package_publisher_matches_expected(self):
        path = PROJECT_ROOT / "store_package.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(
            data["publisher"], EXPECTED_PUBLISHER,
            "publisher CN stimmt nicht mit Partner-Center-Konto überein",
        )

    def test_store_package_executable_configured(self):
        path = PROJECT_ROOT / "store_package.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(
            data["executable"], "AmpelClip.exe",
            "executable in store_package.json muss AmpelClip.exe sein",
        )

    def test_store_package_urls_are_https(self):
        path = PROJECT_ROOT / "store_package.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertTrue(
            data.get("privacy_url", "").startswith("https://"),
            f"privacy_url '{data.get('privacy_url')}' muss eine HTTPS-URL sein"
        )
        self.assertTrue(
            data.get("support_url", "").startswith("https://"),
            f"support_url '{data.get('support_url')}' muss eine HTTPS-URL sein"
        )

    def test_appx_manifest_exists_and_valid(self):
        manifest_file = PROJECT_ROOT / "store_package" / "AmpelClip" / "AppxManifest.xml"
        self.assertTrue(manifest_file.exists(), "AppxManifest.xml fehlt unter store_package/AmpelClip/")
        tree = ET.parse(manifest_file)
        root = tree.getroot()

        # Check identity
        identity = None
        for elem in root.iter():
            if elem.tag.endswith("Identity"):
                identity = elem
                break
        self.assertIsNotNone(identity, "<Identity> Tag in AppxManifest.xml nicht gefunden")
        self.assertEqual(identity.get("Name"), EXPECTED_IDENTITY)
        self.assertEqual(identity.get("Publisher"), EXPECTED_PUBLISHER)
        self.assertEqual(identity.get("Version"), "6.0.0.0")

    def test_store_tile_assets_dimensions(self):
        expected_assets = {
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
        for rel_path, expected_dim in expected_assets.items():
            asset_path = PROJECT_ROOT / rel_path
            self.assertTrue(asset_path.exists(), f"Tile-Asset {rel_path} fehlt")
            im = Image.open(asset_path)
            self.assertEqual(
                im.size, expected_dim,
                f"Tile-Asset {rel_path} hat falsche Dimension: {im.size} != {expected_dim}"
            )

    def test_store_screenshots_exist_and_1080p(self):
        screenshot_dir = PROJECT_ROOT / "screenshots" / "store"
        self.assertTrue(screenshot_dir.exists(), "screenshots/store/ Ordner fehlt")
        shots = list(screenshot_dir.glob("*.png"))
        self.assertGreaterEqual(len(shots), 4, f"Mindestens 4 Store-Screenshots erwartet, gefunden: {len(shots)}")
        for shot in shots:
            im = Image.open(shot)
            self.assertEqual(
                im.size, (1920, 1080),
                f"Screenshot {shot.name} hat nicht die geforderte Auflösung 1920x1080: {im.size}"
            )

    def test_privacy_policy_exists_and_nonempty(self):
        path = PROJECT_ROOT / "PRIVACY_POLICY.md"
        self.assertTrue(path.exists(), "PRIVACY_POLICY.md fehlt")
        content = path.read_text(encoding="utf-8")
        self.assertGreater(len(content.strip()), 100, "PRIVACY_POLICY.md ist zu kurz / leer")

    def test_store_listing_exists_and_compliant(self):
        path = PROJECT_ROOT / "STORE_LISTING.md"
        self.assertTrue(path.exists(), "STORE_LISTING.md fehlt")
        content = path.read_text(encoding="utf-8")
        self.assertGreater(len(content.strip()), 500, "STORE_LISTING.md ist zu kurz")
        self.assertIn("## Deutsch", content, "STORE_LISTING.md enthält keinen deutschen Abschnitt")
        self.assertIn("## English", content, "STORE_LISTING.md enthält keinen englischen Abschnitt")

        # Policy 10.1.3: No third party trademarks in search keywords
        disallowed = ["gmail", "netflix", "spotify", "adobe", "google"]
        in_kw = False
        kw_count = 0
        for line in content.splitlines():
            if "Suchbegriffe" in line or "Keywords" in line:
                in_kw = True
                kw_count = 0
                continue
            if in_kw:
                if line.startswith("###") or line.startswith("---") or not line.strip():
                    if line.startswith("###") or line.startswith("---"):
                        in_kw = False
                    continue
                if line.strip().startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "-")):
                    kw_count += 1
                    kw_lower = line.lower()
                    for d in disallowed:
                        self.assertNotIn(d, kw_lower, f"Unerlaubte Marke '{d}' in Keyword: {line.strip()}")
                    self.assertLessEqual(kw_count, 7, "Maximal 7 Suchbegriffe pro Sprache erlaubt")

    def test_security_and_license_exist(self):
        sec_path = PROJECT_ROOT / "SECURITY.md"
        lic_path = PROJECT_ROOT / "LICENSE"
        third_path = PROJECT_ROOT / "THIRD_PARTY_LICENSES.txt"
        self.assertTrue(sec_path.exists(), "SECURITY.md fehlt")
        self.assertTrue(lic_path.exists(), "LICENSE fehlt")
        self.assertTrue(third_path.exists(), "THIRD_PARTY_LICENSES.txt fehlt")

    def test_check_store_readiness_script_passes_with_allow_blockers(self):
        script_path = PROJECT_ROOT / "scripts" / "check_store_readiness.py"
        self.assertTrue(script_path.exists(), "scripts/check_store_readiness.py fehlt")
        res = subprocess.run([sys.executable, str(script_path), "--allow-blockers"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"check_store_readiness.py schlug fehl:\n{res.stdout}\n{res.stderr}")


if __name__ == "__main__":
    unittest.main()
