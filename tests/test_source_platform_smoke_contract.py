import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from Ampel6 import AmpelTool


def test_source_smoke_runbook_names_the_executable_contract():
    text = (ROOT / "MACOS_LINUX_SOURCE_SMOKE.md").read_text(encoding="utf-8")

    assert "tests\\source_platform_smoke.py" in text
    assert "source_start=PASS" in text
    assert "tray_runtime_gate=PASS" in text
    assert "clipboard_preview=PASS" in text
    assert "config_path=PASS" in text
    assert "kein nativer macOS-/Linux-Release" in text


def test_source_platform_smoke_runs_headless():
    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    env.setdefault("QT_QPA_PLATFORM", "offscreen")

    result = subprocess.run(
        [sys.executable, "tests/source_platform_smoke.py"],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "source_start=PASS" in result.stdout
    assert "tray_runtime_gate=PASS" in result.stdout
    assert "clipboard_preview=PASS" in result.stdout
    assert "config_path=PASS" in result.stdout


def test_clipboard_change_ignores_missing_mime_data():
    class EmptyClipboard:
        def mimeData(self):
            return None

    tool = AmpelTool.__new__(AmpelTool)
    tool.clipboard = EmptyClipboard()
    tool.clipboard_lock = False

    tool._on_clipboard_change()
