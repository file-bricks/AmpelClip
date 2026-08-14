import json
import os
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    with tempfile.TemporaryDirectory(prefix="ampelclip-source-smoke-") as tmp:
        config_path = Path(tmp) / "config.json"
        os.environ["AMPELCLIP_CONFIG_PATH"] = str(config_path)

        import Ampel6
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance() or QApplication([])
        app.setQuitOnLastWindowClosed(False)

        window = Ampel6.AmpelTool()
        try:
            assert Ampel6.resolve_config_path() == config_path
            print("source_start=PASS")

            assert isinstance(window._tray_available, bool)
            assert window.tray_icon is not None
            print("tray_runtime_gate=PASS")

            sample = "Kontakt: max@example.org"
            window.clipboard.setText(sample)
            app.processEvents()
            window._on_clipboard_change()

            assert window.txt_original.toPlainText() == sample
            assert "[ANONYM]" in window.txt_anon.toPlainText()
            print("clipboard_preview=PASS")

            window._save_config()
            saved = json.loads(config_path.read_text(encoding="utf-8"))
            assert saved["ampel_status"] in Ampel6.VALID_AMPEL_STATUSES
            assert "files" in saved
            print("config_path=PASS")
        finally:
            try:
                window.clipboard.dataChanged.disconnect(window._on_clipboard_change)
            except (RuntimeError, TypeError):
                pass
            window.tray_icon.hide()
            window.deleteLater()
            app.processEvents()
            app.quit()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
