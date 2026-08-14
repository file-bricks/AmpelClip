import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

sys.path.insert(0, str(Path(__file__).parent.parent))

from Ampel6 import AmpelTool


def _get_app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_manual_entry_and_filter_fields_expose_accessible_context():
    app = _get_app()
    tool = AmpelTool()
    try:
        assert tool.entry_sens.accessibleName() == "Sensiblen Begriff eingeben"
        assert "sensiblen Begriff" in tool.entry_sens.accessibleDescription()
        assert tool.entry_sens.toolTip() == "Neuen sensiblen Begriff eingeben"

        assert tool.entry_white.accessibleName() == "Whitelist-Begriff eingeben"
        assert "Whitelist-Begriff" in tool.entry_white.accessibleDescription()
        assert tool.entry_white.toolTip() == "Neuen Whitelist-Begriff eingeben"

        assert tool.filter_sens.accessibleName() == "Sensible Daten filtern"
        assert "Liste sensibler Daten" in tool.filter_sens.accessibleDescription()
        assert tool.filter_sens.toolTip() == "Filter für sensible Daten"

        assert tool.filter_white.accessibleName() == "Whitelist filtern"
        assert "Whitelist" in tool.filter_white.accessibleDescription()
        assert tool.filter_white.toolTip() == "Filter für die Whitelist"
    finally:
        try:
            tool.clipboard.dataChanged.disconnect(tool._on_clipboard_change)
        except (RuntimeError, TypeError):
            pass
        tool.tray_icon.hide()
        tool.deleteLater()
        app.processEvents()
