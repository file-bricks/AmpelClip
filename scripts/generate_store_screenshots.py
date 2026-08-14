"""
Generate official 1080p Store screenshots for AmpelClip.
Renders real UI views of all main tabs at 1920x1080 resolution.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Set offscreen Qt platform before importing Qt
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PIL import Image
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import Ampel6


def generate_store_screenshots() -> list[Path]:
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    window = Ampel6.AmpelTool()
    window.resize(1100, 750)
    window.show()

    # Pre-populate sample test data for nice screenshots
    if not window.sensitive:
        window.sensitive = [
            "Passwort", "Geheimcode", "Kreditkartennummer",
            "Kundennummer", "Vertraulich", "Gehaltsdaten"
        ]
    if not window.whitelist:
        window.whitelist = ["Public-Info", "Support-Team", "GmbH", "DEUTSCHLAND"]

    window._update_listboxes()

    # Populate sample history
    window.clip_history = [
        "Rechnungsbeleg DE89 3704 0044 0532 0130 00 - Rechnungsüberweisung für Lizenz",
        "Kontakt Support: max.mustermann@firma.de oder Tel. 0170-1234567",
        "Internes Dokument Version 1.4 - Entwurf zur Freigabe",
        "Kreditkarte: 4532 7512 8934 1120 Ablauf: 12/28 CVC: 882",
    ]
    window.list_history.clear()
    for item in window.clip_history:
        preview = item[:100].replace("\n", " ")
        if len(item) > 100:
            preview += "..."
        window.list_history.addItem(preview)

    # Set sample text in Ampel tab
    window._set_ampel("gelb")
    sample_orig = "Kunde: Max Mustermann\nE-Mail: max.mustermann@example.com\nIBAN: DE89 3704 0044 0532 0130 00\nTelefon: +49 89 1234567\nStatus: Whitelist GmbH freigegeben."
    sample_anon = window._anonymize(sample_orig)
    window.txt_original.setPlainText(sample_orig)
    window.txt_anon.setPlainText(sample_anon)
    window.lbl_status_detail.setText("GELB: Vorschau - 6 Patterns aktiv.")

    out_dirs = [
        PROJECT_ROOT / "screenshots" / "store",
        PROJECT_ROOT / "README" / "screenshots" / "store",
    ]
    for d in out_dirs:
        d.mkdir(parents=True, exist_ok=True)

    screens = [
        (0, "01_ampelclip_listenverwaltung.png"),
        (1, "02_ampelclip_regex_patterns.png"),
        (2, "03_ampelclip_ampelsteuerung.png"),
        (3, "04_ampelclip_verlauf_anonymisierung.png"),
    ]

    saved_paths: list[Path] = []
    target_width, target_height = 1920, 1080

    for tab_idx, filename in screens:
        window.tabs.setCurrentIndex(tab_idx)
        app.processEvents()

        # Grab window pixmap
        pixmap = window.grab()
        temp_img_path = PROJECT_ROOT / "screenshots" / "store" / f"temp_{filename}"
        pixmap.save(str(temp_img_path), "PNG")

        # Compose 1920x1080 frame with dark aesthetic background
        ui_img = Image.open(temp_img_path).convert("RGBA")
        canvas = Image.new("RGBA", (target_width, target_height), (30, 34, 42, 255))

        # Scale UI image maintaining aspect ratio
        max_ui_w = int(target_width * 0.88)
        max_ui_h = int(target_height * 0.85)
        scale = min(max_ui_w / ui_img.width, max_ui_h / ui_img.height)
        new_w = int(ui_img.width * scale)
        new_h = int(ui_img.height * scale)
        scaled_ui = ui_img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        # Center in canvas
        x = (target_width - new_w) // 2
        y = (target_height - new_h) // 2
        canvas.paste(scaled_ui, (x, y), scaled_ui)

        # Save to all destination dirs
        for d in out_dirs:
            final_path = d / filename
            canvas.save(final_path, "PNG")
            saved_paths.append(final_path)

        if temp_img_path.exists():
            temp_img_path.unlink()

    print(f"Generated {len(screens)} official Store screenshots in 1920x1080 resolution.")
    window.close()
    return saved_paths


if __name__ == "__main__":
    generate_store_screenshots()
