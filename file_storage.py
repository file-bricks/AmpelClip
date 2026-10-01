"""Shared text publication without GUI dependencies."""

import logging
import os
from pathlib import Path
import stat
import tempfile
import threading

_SAVE_PUBLICATION_LOCK = threading.Lock()


def write_text_atomic(path: Path, text: str) -> None:
    """Publish complete text; preserve existing files when writing fails."""
    tmp = None
    identity = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent,
            prefix=".ampelclip-", suffix=".tmp", delete=False,
        ) as stream:
            tmp = Path(stream.name)
            identity = os.fstat(stream.fileno())
            stream.write(text)
        current = tmp.lstat()
        if not stat.S_ISREG(current.st_mode) or not os.path.samestat(current, identity):
            raise OSError("Die temporäre Speicherdatei wurde extern verändert.")
        # Concurrent Windows replacements can fail with WinError 5 even when
        # both staging handles are closed. Serialize publication in this process.
        with _SAVE_PUBLICATION_LOCK:
            tmp.replace(path)
        tmp = None
    finally:
        if tmp is not None and identity is not None:
            try:
                current = tmp.lstat()
                if stat.S_ISREG(current.st_mode) and os.path.samestat(current, identity):
                    tmp.unlink()
            except FileNotFoundError:
                pass
            except OSError as error:
                try:
                    logging.warning("Eigene temporäre Datei konnte nicht entfernt werden: %s", error)
                except Exception:
                    # A failing custom log handler must not hide the save error.
                    pass

