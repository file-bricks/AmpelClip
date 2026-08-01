"""
AmpelTool V6 - Datenschutz & Clipboard Monitor
Neu: Eingebaute Regex-Patterns für IBAN, Email, Telefon, Kreditkarten
"""

import os
import sys
import json
import re
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, List, Tuple, Dict

import pandas as pd
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QPushButton, QLabel, QLineEdit, QListWidget,
    QTextEdit, QFileDialog, QMessageBox, QFrame, QCheckBox,
    QSplitter, QSystemTrayIcon, QMenu, QGroupBox
)
from PySide6.QtCore import Qt, QSize, QEvent
from PySide6.QtGui import QAction, QIcon, QColor, QPixmap, QPainter, QBrush

# --- Konfiguration ---
APP_NAME = "AmpelClip"
APP_VERSION = "6"
PROFILE_SCHEMA_VERSION = "ampelclip-profile-v1"
PROFILE_DEFAULT_FILENAME = f"{PROFILE_SCHEMA_VERSION}.json"
VALID_AMPEL_STATUSES = {"rot", "gelb", "gruen"}
PATTERN_KEY_ALIASES = {
    "credit_card": "creditcard",
    "postal_code_de": "postcode_de",
}


def resolve_config_path() -> Path:
    override = os.environ.get("AMPELCLIP_CONFIG_PATH")
    if override:
        return Path(override)
    if getattr(sys, "frozen", False):
        appdata = os.environ.get("LOCALAPPDATA")
        if appdata:
            return Path(appdata) / APP_NAME / "config.json"
    return Path(__file__).parent / "config.json"


CONFIG_PATH = resolve_config_path()
CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
HISTORY_LIMIT = 15

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

# --- Eingebaute Regex-Patterns ---
BUILTIN_PATTERNS = {
    "iban": {
        "name": "IBAN (Kontonummer)",
        "regex": r"\b[A-Z]{2}\d{2}[\s]?(?:\d{4}[\s]?){4,7}\d{0,2}\b",
        "description": "Deutsche/EU Kontonummern (DE89 3704 0044 ...)",
        "default": True
    },
    "email": {
        "name": "E-Mail Adressen",
        "regex": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        "description": "name@domain.de",
        "default": True
    },
    "phone_de": {
        "name": "Telefonnummern (DE)",
        "regex": r"\b(?:\+49|0049|0)[\s.-]?(?:\d{2,4})[\s.-]?(?:\d{3,})[\s.-]?(?:\d{2,})\b",
        "description": "+49 170 1234567, 0170-1234567",
        "default": False
    },
    "creditcard": {
        "name": "Kreditkarten",
        "regex": r"\b(?:\d{4}[\s-]?){3}\d{4}\b",
        "description": "1234 5678 9012 3456",
        "default": False
    },
    "postcode_de": {
        "name": "Postleitzahlen (DE)",
        "regex": r"\b\d{5}\b",
        "description": "5-stellige PLZ",
        "default": False
    },
    "date_de": {
        "name": "Datumsangaben",
        "regex": r"\b\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\b",
        "description": "01.01.2024, 1/1/24",
        "default": False
    }
}


def _clean_unique_strings(values: Any) -> List[str]:
    if not isinstance(values, list):
        return []
    result: List[str] = []
    seen = set()
    for value in values:
        text = str(value).strip()
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return result


def _normalized_ampel_status(value: Any) -> str:
    status = str(value or "").strip().lower()
    return status if status in VALID_AMPEL_STATUSES else "rot"


def _normalized_builtin_patterns(
    values: Any,
    defaults: Dict[str, bool] | None = None,
) -> Dict[str, bool]:
    state = {
        key: bool((defaults or {}).get(key, info["default"]))
        for key, info in BUILTIN_PATTERNS.items()
    }
    if not isinstance(values, dict):
        return state
    for raw_key, enabled in values.items():
        key = PATTERN_KEY_ALIASES.get(str(raw_key), str(raw_key))
        if key in state:
            state[key] = bool(enabled)
    return state


def _collect_literal_spans(
    text: str,
    terms: List[str],
    *,
    case_sensitive: bool,
    whole_words: bool,
) -> List[Tuple[int, int]]:
    flags = 0 if case_sensitive else re.IGNORECASE
    spans: List[Tuple[int, int]] = []
    for term in terms:
        escaped = re.escape(term)
        pattern = rf"(?<!\w){escaped}(?!\w)" if whole_words else escaped
        for match in re.finditer(pattern, text, flags):
            spans.append((match.start(), match.end()))
    if not spans:
        return []
    spans.sort()
    merged: List[Tuple[int, int]] = [spans[0]]
    for start, end in spans[1:]:
        last_start, last_end = merged[-1]
        if start <= last_end:
            merged[-1] = (last_start, max(last_end, end))
        else:
            merged.append((start, end))
    return merged


def _substitute_outside_spans(
    text: str,
    pattern: re.Pattern,
    replacement: str,
    protected_spans: List[Tuple[int, int]],
) -> str:
    protected_spans = _filter_spans_for_pattern(text, pattern, protected_spans)
    if not protected_spans:
        return pattern.sub(replacement, text)

    chunks: List[str] = []
    cursor = 0
    for start, end in protected_spans:
        if cursor < start:
            chunks.append(pattern.sub(replacement, text[cursor:start]))
        chunks.append(text[start:end])
        cursor = end
    if cursor < len(text):
        chunks.append(pattern.sub(replacement, text[cursor:]))
    return "".join(chunks)


def _filter_spans_for_pattern(
    text: str,
    pattern: re.Pattern,
    protected_spans: List[Tuple[int, int]],
) -> List[Tuple[int, int]]:
    if not protected_spans:
        return []

    pattern_spans = [
        (match.start(), match.end())
        for match in pattern.finditer(text)
        if match.start() != match.end()
    ]
    if not pattern_spans:
        return protected_spans

    filtered: List[Tuple[int, int]] = []
    for start, end in protected_spans:
        is_subspan = any(
            match_start <= start
            and end <= match_end
            and (match_start < start or end < match_end)
            for match_start, match_end in pattern_spans
        )
        if not is_subspan:
            filtered.append((start, end))
    return filtered


def build_profile_export_payload(
    sensitive: List[str],
    whitelist: List[str],
    builtin_enabled: Dict[str, bool],
    ampel_status: str,
    case_sensitive: bool,
    whole_words: bool,
    exported_at: datetime | str | None = None,
) -> Dict[str, Any]:
    if exported_at is None:
        exported_at_value = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    elif isinstance(exported_at, datetime):
        exported_at_value = exported_at.replace(microsecond=0).isoformat()
    else:
        exported_at_value = str(exported_at)

    return {
        "schema_version": PROFILE_SCHEMA_VERSION,
        "app": {
            "name": APP_NAME,
            "version": APP_VERSION,
            "exported_at": exported_at_value,
        },
        "settings": {
            "ampel_status": _normalized_ampel_status(ampel_status),
            "case_sensitive": bool(case_sensitive),
            "whole_words": bool(whole_words),
        },
        "builtin_patterns": _normalized_builtin_patterns(
            builtin_enabled,
            defaults={key: False for key in BUILTIN_PATTERNS},
        ),
        "lists": {
            "sensibel": _clean_unique_strings(sensitive),
            "whitelist": _clean_unique_strings(whitelist),
        },
    }


def normalize_profile_payload(payload: Any) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("Profil muss ein JSON-Objekt sein.")
    if payload.get("schema_version") != PROFILE_SCHEMA_VERSION:
        raise ValueError(f"Nicht unterstütztes Profilformat: {payload.get('schema_version')!r}")

    settings = payload.get("settings", {})
    if not isinstance(settings, dict):
        settings = {}
    lists = payload.get("lists", {})
    if not isinstance(lists, dict):
        lists = {}

    return {
        "schema_version": PROFILE_SCHEMA_VERSION,
        "app": payload.get("app", {}) if isinstance(payload.get("app", {}), dict) else {},
        "settings": {
            "ampel_status": _normalized_ampel_status(settings.get("ampel_status")),
            "case_sensitive": bool(settings.get("case_sensitive", False)),
            "whole_words": bool(settings.get("whole_words", False)),
        },
        "builtin_patterns": _normalized_builtin_patterns(payload.get("builtin_patterns", {})),
        "lists": {
            "sensibel": _clean_unique_strings(lists.get("sensibel", [])),
            "whitelist": _clean_unique_strings(lists.get("whitelist", [])),
        },
    }


def write_profile_payload(path: Path, payload: Dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def read_profile_payload(path: Path) -> Dict[str, Any]:
    return normalize_profile_payload(json.loads(path.read_text(encoding="utf-8")))


def read_first_column_values(path: Path) -> List[str]:
    if path.suffix.lower() == ".xlsx":
        df = pd.read_excel(path, header=None)
        if df.empty:
            return []
        return df.iloc[:, 0].dropna().astype(str).tolist()
    # utf-8-sig entfernt ein evtl. BOM; bei Nicht-UTF-8-Listen (cp1252/Latin-1 aus
    # Excel/Editor) auf cp1252 zurueckfallen, statt die Datei (und damit den
    # Datenschutz-Schutz) STILL zu verwerfen (Exception wurde in _load_file_internal
    # geschluckt -> Liste blieb leer, Nutzer glaubt geschuetzt zu sein).
    try:
        text = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        text = path.read_text(encoding="cp1252", errors="replace")
    return text.splitlines()

# --- Stylesheet (Modernes Design) ---
STYLESHEET = """
QMainWindow { background-color: #f0f2f5; }
QTabWidget::pane { border: 1px solid #dcdcdc; background: white; border-radius: 4px; }
QTabBar::tab { background: #e1e4e8; padding: 8px 20px; margin-right: 2px; border-top-left-radius: 4px; border-top-right-radius: 4px; color: #333; }
QTabBar::tab:selected { background: white; font-weight: bold; border-bottom: 2px solid #007bff; }
QLabel { color: #333; font-size: 14px; }
QLabel#Header { font-size: 18px; font-weight: bold; color: #2c3e50; }
QLabel#SubHeader { font-size: 14px; font-weight: bold; color: #34495e; margin-top: 10px; }
QPushButton { background-color: #ffffff; border: 1px solid #ced4da; border-radius: 4px; padding: 6px 12px; font-size: 13px; color: #495057; }
QPushButton:hover { background-color: #e9ecef; border-color: #adb5bd; }
QPushButton#Danger { color: #dc3545; border-color: #dc3545; }
QPushButton#Danger:hover { background-color: #dc3545; color: white; }
QPushButton#Success { color: #28a745; border-color: #28a745; }
QPushButton#Success:hover { background-color: #28a745; color: white; }
QPushButton#Warning { color: #ffc107; border-color: #ffc107; }
QPushButton#Warning:hover { background-color: #ffc107; color: #212529; }
QLineEdit, QListWidget, QTextEdit { border: 1px solid #ced4da; border-radius: 4px; padding: 4px; background-color: white; selection-background-color: #007bff; }
QGroupBox { font-weight: bold; border: 1px solid #dcdcdc; border-radius: 4px; margin-top: 10px; padding-top: 10px; }
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
QCheckBox { spacing: 8px; }
QCheckBox::indicator { width: 18px; height: 18px; }
"""

class AmpelTool(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AmpelTool V6 - Datenschutz & Clipboard")
        self.resize(1000, 800)
        self.setMinimumSize(900, 700)
        
        # Variablen
        self.sensitive: List[str] = []
        self.whitelist: List[str] = []
        self.clip_history: List[str] = []
        self.file_history: List[Tuple[str, str]] = []
        self.patterns: List[re.Pattern] = []
        
        # Eingebaute Pattern-Status
        self.builtin_enabled: Dict[str, bool] = {
            key: info["default"] for key, info in BUILTIN_PATTERNS.items()
        }
        
        self.ampel_status = "rot"
        self.case_sensitive = False
        self.whole_words = False
        self.clipboard_lock = False
        self._last_written_text: str | None = None  # Re-Entry-Guard (Windows queued dataChanged)
        self.force_quit = False

        # GUI & System
        self._init_ui()
        self._setup_tray()

        # Clipboard initialisieren
        self.clipboard = QApplication.clipboard()
        
        # Config laden
        self._load_config()
        self._compile_patterns()
        
        # Signal verbinden
        self.clipboard.dataChanged.connect(self._on_clipboard_change)
        
        self.setStyleSheet(STYLESHEET)
        self.statusBar().showMessage("Bereit. V6 mit Regex-Patterns.")

    def _init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        self.tab_data = QWidget()
        self.tab_patterns = QWidget()  # NEU: Tab für Patterns
        self.tab_ampel = QWidget()
        self.tab_history = QWidget()

        self.tabs.addTab(self.tab_data, "Listenverwaltung")
        self.tabs.addTab(self.tab_patterns, "Regex-Patterns")  # NEU
        self.tabs.addTab(self.tab_ampel, "Ampelsteuerung")
        self.tabs.addTab(self.tab_history, "Verlauf")

        self._setup_tab_data()
        self._setup_tab_patterns()  # NEU
        self._setup_tab_ampel()
        self._setup_tab_history()

    def _set_accessible_context(
        self,
        widget: QWidget,
        *,
        name: str,
        description: str,
        tooltip: str | None = None,
    ) -> None:
        widget.setAccessibleName(name)
        widget.setAccessibleDescription(description)
        if tooltip:
            widget.setToolTip(tooltip)

    # ---------------- SYSTEM TRAY LOGIK ----------------
    def _setup_tray(self):
        # Ohne verfuegbaren System-Tray darf die App beim Schliessen NICHT in den
        # Tray verstecken (sonst unsichtbar + nicht mehr erreichbar, da
        # setQuitOnLastWindowClosed(False) gesetzt ist). Flag steuert den closeEvent.
        self._tray_available = QSystemTrayIcon.isSystemTrayAvailable()
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setToolTip("AmpelTool V6 Datenschutz")
        self._update_tray_icon_color()

        self._tray_menu = QMenu(self)
        action_show = QAction("Anzeigen", self)
        action_show.triggered.connect(self.show_window)
        self._tray_menu.addAction(action_show)
        self._tray_menu.addSeparator()
        action_quit = QAction("Beenden", self)
        action_quit.triggered.connect(self.quit_app)
        self._tray_menu.addAction(action_quit)

        self.tray_icon.setContextMenu(self._tray_menu)
        self.tray_icon.activated.connect(self._on_tray_click)
        self.tray_icon.show()

    def _draw_color_icon(self, color_code):
        size = 64
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(color_code)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, size, size)
        painter.end()
        return QIcon(pixmap)

    def _update_tray_icon_color(self):
        colors = {"rot": "#dc3545", "gelb": "#ffc107", "gruen": "#28a745"}
        c = colors.get(self.ampel_status, "#6c757d")
        self.tray_icon.setIcon(self._draw_color_icon(c))

    def _on_tray_click(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_window()

    def show_window(self):
        self.show()
        self.activateWindow()

    def quit_app(self):
        """Beendet die Anwendung sauber inkl. SystemTray"""
        self.force_quit = True
        self._save_config()
        self.tray_icon.hide()  # Tray-Icon entfernen
        self.tray_icon.deleteLater()  # Ressourcen freigeben
        QApplication.quit()  # App beenden

    def closeEvent(self, event):
        if self.force_quit:
            event.accept()
            return
        if not getattr(self, "_tray_available", True):
            # Kein System-Tray -> normal beenden, sonst liefe die App unsichtbar
            # weiter (setQuitOnLastWindowClosed(False)).
            self._save_config()
            event.accept()
            QApplication.quit()
            return
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "AmpelTool minimiert",
            "Läuft im Hintergrund weiter.",
            QSystemTrayIcon.MessageIcon.Information, 2000
        )

    # ---------------- TAB: LISTENVERWALTUNG ----------------
    def _setup_tab_data(self):
        layout = QVBoxLayout(self.tab_data)
        
        frame_files = QFrame()
        files_layout = QHBoxLayout(frame_files)
        
        btn_load_sens = QPushButton("Import Sensibel")
        btn_load_sens.setObjectName("Danger")
        btn_load_sens.clicked.connect(lambda: self._load_files("sensibel"))
        self._set_accessible_context(
            btn_load_sens,
            name="Sensible Begriffe importieren",
            description="Lädt eine Text- oder Excel-Datei mit sensiblen Begriffen.",
            tooltip="Sensible Begriffe aus Datei importieren",
        )
        
        btn_load_white = QPushButton("Import Whitelist")
        btn_load_white.setObjectName("Success")
        btn_load_white.clicked.connect(lambda: self._load_files("whitelist"))
        self._set_accessible_context(
            btn_load_white,
            name="Whitelist-Begriffe importieren",
            description="Lädt eine Text- oder Excel-Datei mit freigegebenen Whitelist-Begriffen.",
            tooltip="Whitelist-Begriffe aus Datei importieren",
        )
        
        btn_export_sens = QPushButton("Export Sensibel", clicked=lambda: self._export_list("sensibel"))
        self._set_accessible_context(
            btn_export_sens,
            name="Sensible Begriffe exportieren",
            description="Exportiert alle aktuellen sensiblen Begriffe in eine Textdatei.",
            tooltip="Sensible Begriffe in Datei exportieren",
        )
        btn_export_white = QPushButton("Export Whitelist", clicked=lambda: self._export_list("whitelist"))
        self._set_accessible_context(
            btn_export_white,
            name="Whitelist-Begriffe exportieren",
            description="Exportiert alle aktuellen Whitelist-Begriffe in eine Textdatei.",
            tooltip="Whitelist-Begriffe in Datei exportieren",
        )
        btn_export_prof = QPushButton("Profil exportieren", clicked=self._export_profile)
        self._set_accessible_context(
            btn_export_prof,
            name="Profil exportieren",
            description="Exportiert Einstellungen und Listen ohne Verlauf in ein JSON-Profil.",
            tooltip="Einstellungen und Regellisten in JSON-Profil exportieren",
        )
        btn_import_prof = QPushButton("Profil importieren", clicked=self._import_profile)
        self._set_accessible_context(
            btn_import_prof,
            name="Profil importieren",
            description="Importiert Einstellungen und Listen aus einem JSON-Profil.",
            tooltip="Einstellungen und Regellisten aus JSON-Profil importieren",
        )
        
        files_layout.addWidget(btn_load_sens)
        files_layout.addWidget(btn_load_white)
        files_layout.addWidget(btn_export_sens)
        files_layout.addWidget(btn_export_white)
        files_layout.addWidget(btn_export_prof)
        files_layout.addWidget(btn_import_prof)
        
        layout.addWidget(QLabel("Dateioperationen", objectName="Header"))
        layout.addWidget(frame_files)

        frame_manual = QFrame()
        manual_layout = QHBoxLayout(frame_manual)
        
        self.entry_sens = QLineEdit(placeholderText="Neuer sensibler Begriff...")
        self.entry_sens.returnPressed.connect(lambda: self._add_manual(self.entry_sens, self.sensitive))
        self._set_accessible_context(
            self.entry_sens,
            name="Sensiblen Begriff eingeben",
            description="Feld für einen neuen sensiblen Begriff. Bestätigen Sie mit Eingabe oder dem roten Hinzufügen-Button.",
            tooltip="Neuen sensiblen Begriff eingeben",
        )
        btn_add_sens = QPushButton("Hinzufügen", objectName="Danger")
        btn_add_sens.clicked.connect(lambda: self._add_manual(self.entry_sens, self.sensitive))
        self._set_accessible_context(
            btn_add_sens,
            name="Sensiblen Begriff hinzufügen",
            description="Fügt den Begriff aus dem linken Eingabefeld zur Liste sensibler Daten hinzu.",
            tooltip="Sensiblen Begriff zur roten Liste hinzufügen",
        )

        self.entry_white = QLineEdit(placeholderText="Neuer Whitelist Begriff...")
        self.entry_white.returnPressed.connect(lambda: self._add_manual(self.entry_white, self.whitelist))
        self._set_accessible_context(
            self.entry_white,
            name="Whitelist-Begriff eingeben",
            description="Feld für einen neuen Whitelist-Begriff. Bestätigen Sie mit Eingabe oder dem grünen Hinzufügen-Button.",
            tooltip="Neuen Whitelist-Begriff eingeben",
        )
        btn_add_white = QPushButton("Hinzufügen", objectName="Success")
        btn_add_white.clicked.connect(lambda: self._add_manual(self.entry_white, self.whitelist))
        self._set_accessible_context(
            btn_add_white,
            name="Whitelist-Begriff hinzufügen",
            description="Fügt den Begriff aus dem rechten Eingabefeld zur Whitelist hinzu.",
            tooltip="Whitelist-Begriff zur grünen Liste hinzufügen",
        )

        manual_layout.addWidget(self.entry_sens)
        manual_layout.addWidget(btn_add_sens)
        manual_layout.addSpacing(20)
        manual_layout.addWidget(self.entry_white)
        manual_layout.addWidget(btn_add_white)
        
        layout.addWidget(QLabel("Manuelle Eingabe", objectName="Header"))
        layout.addWidget(frame_manual)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        w_sens = QWidget()
        l_sens = QVBoxLayout(w_sens)
        l_sens.setContentsMargins(0,0,0,0)
        l_sens.addWidget(QLabel("Sensible Daten (Rot)"))
        self.filter_sens = QLineEdit(placeholderText="Filter...")
        self.filter_sens.textChanged.connect(self._update_listboxes)
        self._set_accessible_context(
            self.filter_sens,
            name="Sensible Daten filtern",
            description="Filtert die Liste sensibler Daten nach dem eingegebenen Text.",
            tooltip="Filter für sensible Daten",
        )
        l_sens.addWidget(self.filter_sens)
        self.list_sens = QListWidget()
        self.list_sens.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self._set_accessible_context(
            self.list_sens,
            name="Liste sensibler Begriffe",
            description="Liste aller aktuell erfassten sensiblen Begriffe.",
            tooltip="Sensible Begriffe",
        )
        l_sens.addWidget(self.list_sens)
        btn_del_sens = QPushButton("Ausgewählte löschen")
        btn_del_sens.clicked.connect(lambda: self._delete_selected(self.list_sens, self.sensitive))
        self._set_accessible_context(
            btn_del_sens,
            name="Sensible Begriffe löschen",
            description="Löscht alle in der linken Liste ausgewählten Begriffe.",
            tooltip="Ausgewählte sensible Begriffe löschen",
        )
        l_sens.addWidget(btn_del_sens)
        
        w_white = QWidget()
        l_white = QVBoxLayout(w_white)
        l_white.setContentsMargins(0,0,0,0)
        l_white.addWidget(QLabel("Whitelist (Grün)"))
        self.filter_white = QLineEdit(placeholderText="Filter...")
        self.filter_white.textChanged.connect(self._update_listboxes)
        self._set_accessible_context(
            self.filter_white,
            name="Whitelist filtern",
            description="Filtert die Whitelist nach dem eingegebenen Text.",
            tooltip="Filter für die Whitelist",
        )
        l_white.addWidget(self.filter_white)
        self.list_white = QListWidget()
        self.list_white.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self._set_accessible_context(
            self.list_white,
            name="Whitelist-Begriffe",
            description="Liste aller freigegebenen Whitelist-Begriffe.",
            tooltip="Whitelist-Begriffe",
        )
        l_white.addWidget(self.list_white)
        btn_del_white = QPushButton("Ausgewählte löschen")
        btn_del_white.clicked.connect(lambda: self._delete_selected(self.list_white, self.whitelist))
        self._set_accessible_context(
            btn_del_white,
            name="Whitelist-Begriffe löschen",
            description="Löscht alle in der rechten Liste ausgewählten Begriffe.",
            tooltip="Ausgewählte Whitelist-Begriffe löschen",
        )
        l_white.addWidget(btn_del_white)

        splitter.addWidget(w_sens)
        splitter.addWidget(w_white)
        layout.addWidget(splitter, stretch=1)

    # ---------------- TAB: REGEX-PATTERNS (NEU) ----------------
    def _setup_tab_patterns(self):
        layout = QVBoxLayout(self.tab_patterns)
        
        layout.addWidget(QLabel("Eingebaute Datenschutz-Patterns", objectName="Header"))
        layout.addWidget(QLabel("Aktiviere Pattern-Typen um automatisch sensible Daten zu erkennen:"))
        
        # GroupBox für Patterns
        group = QGroupBox("Verfügbare Patterns")
        group_layout = QVBoxLayout(group)
        
        self.pattern_checkboxes: Dict[str, QCheckBox] = {}
        
        for key, info in BUILTIN_PATTERNS.items():
            cb = QCheckBox(f"{info['name']} - {info['description']}")
            cb.setChecked(self.builtin_enabled.get(key, info["default"]))
            cb.stateChanged.connect(self._on_pattern_toggle)
            cb.setProperty("pattern_key", key)
            self._set_accessible_context(
                cb,
                name=f"Pattern {info['name']}",
                description=f"Aktiviert oder deaktiviert das Erkennungsmuster für {info['description']}.",
                tooltip=info["description"],
            )
            self.pattern_checkboxes[key] = cb
            group_layout.addWidget(cb)
        
        layout.addWidget(group)
        
        # Info-Box
        info_frame = QFrame()
        info_frame.setStyleSheet("background-color: #e7f3ff; border: 1px solid #b6d4fe; border-radius: 4px; padding: 10px;")
        info_layout = QVBoxLayout(info_frame)
        info_layout.addWidget(QLabel("<b>Hinweis:</b>"))
        info_layout.addWidget(QLabel("Diese Patterns erkennen typische Formate automatisch."))
        info_layout.addWidget(QLabel("Sie ergänzen die manuellen Listen im Tab 'Listenverwaltung'."))
        info_layout.addWidget(QLabel("IBAN und E-Mail sind standardmäßig aktiviert."))
        layout.addWidget(info_frame)
        
        # Statistik
        self.lbl_pattern_stats = QLabel("Aktive Patterns: 0")
        self.lbl_pattern_stats.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(self.lbl_pattern_stats)
        
        layout.addStretch()
        
        self._update_pattern_stats()

    def _on_pattern_toggle(self):
        for key, cb in self.pattern_checkboxes.items():
            self.builtin_enabled[key] = cb.isChecked()
        self._compile_patterns()
        self._update_pattern_stats()
        self._save_config()
        self._on_clipboard_change()

    def _update_pattern_stats(self):
        active = sum(1 for v in self.builtin_enabled.values() if v)
        total = len(BUILTIN_PATTERNS)
        self.lbl_pattern_stats.setText(f"Aktive Patterns: {active}/{total}")

    # ---------------- TAB: AMPELSTEUERUNG ----------------
    def _setup_tab_ampel(self):
        layout = QVBoxLayout(self.tab_ampel)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        vis_container = QWidget()
        vis_layout = QHBoxLayout(vis_container)
        self.lbl_ampel_icon = QLabel()
        self.lbl_ampel_icon.setFixedSize(100, 100)
        self._set_accessible_context(
            self.lbl_ampel_icon,
            name="Ampel-Farbindikator",
            description="Visueller Indikator des aktuellen Ampel-Schutzstatus.",
        )
        self.lbl_ampel_text = QLabel("ROT")
        self._set_accessible_context(
            self.lbl_ampel_text,
            name="Ampelstatus Textanzeige",
            description="Textuelle Anzeige des aktuellen Ampel-Schutzstatus.",
        )
        vis_layout.addStretch()
        vis_layout.addWidget(self.lbl_ampel_icon)
        vis_layout.addWidget(self.lbl_ampel_text)
        vis_layout.addStretch()
        layout.addWidget(vis_container)

        ctrl_container = QHBoxLayout()
        btn_rot = QPushButton("STOP (Rot)", objectName="Danger", minimumHeight=40)
        btn_rot.clicked.connect(lambda: self._set_ampel("rot"))
        self._set_accessible_context(
            btn_rot,
            name="Schutzmodus STOP (Rot)",
            description="Aktiviert den STOP-Modus. Keine automatischen Ersetzungen in der Zwischenablage.",
            tooltip="STOP-Modus aktivieren (Zwischenablage unverändert lassen)",
        )
        btn_gelb = QPushButton("PREVIEW (Gelb)", objectName="Warning", minimumHeight=40)
        btn_gelb.clicked.connect(lambda: self._set_ampel("gelb"))
        self._set_accessible_context(
            btn_gelb,
            name="Schutzmodus PREVIEW (Gelb)",
            description="Aktiviert den Vorschau-Modus. Anonymisiert nur in der App-Vorschau.",
            tooltip="PREVIEW-Modus aktivieren (Vorschau in App)",
        )
        btn_gruen = QPushButton("ACTIVE (Grün)", objectName="Success", minimumHeight=40)
        btn_gruen.clicked.connect(lambda: self._set_ampel("gruen"))
        self._set_accessible_context(
            btn_gruen,
            name="Schutzmodus ACTIVE (Grün)",
            description="Aktiviert den Aktiv-Modus. Anonymisiert sensible Daten automatisch in der Zwischenablage.",
            tooltip="ACTIVE-Modus aktivieren (Automatische Anonymisierung)",
        )
        ctrl_container.addWidget(btn_rot)
        ctrl_container.addWidget(btn_gelb)
        ctrl_container.addWidget(btn_gruen)
        layout.addLayout(ctrl_container)

        opt_container = QHBoxLayout()
        self.cb_case = QCheckBox("Groß-/Kleinschreibung beachten")
        self.cb_case.stateChanged.connect(self._on_option_change)
        self._set_accessible_context(
            self.cb_case,
            name="Groß-/Kleinschreibung beachten",
            description="Aktiviert die exakte Unterscheidung von Groß- und Kleinschreibung bei Suchmustern.",
            tooltip="Groß-/Kleinschreibung bei Treffern beachten",
        )
        self.cb_words = QCheckBox("Nur ganze Wörter")
        self.cb_words.stateChanged.connect(self._on_option_change)
        self._set_accessible_context(
            self.cb_words,
            name="Nur ganze Wörter",
            description="Beschränkt Suchmuster auf eigenständige ganze Wörter.",
            tooltip="Suchmuster nur auf vollständige Wörter anwenden",
        )
        opt_container.addWidget(self.cb_case)
        opt_container.addWidget(self.cb_words)
        opt_container.addStretch()
        layout.addLayout(opt_container)

        layout.addSpacing(20)
        layout.addWidget(QLabel("Vorschau (Live-Anonymisierung):", objectName="Header"))
        preview_split = QSplitter(Qt.Orientation.Horizontal)
        self.txt_original = QTextEdit(readOnly=True, placeholderText="Original...")
        self._set_accessible_context(
            self.txt_original,
            name="Originaler Zwischenablagentext",
            description="Zeigt den aus der Zwischenablage gelesenen Originaltext.",
            tooltip="Originaltext der Zwischenablage",
        )
        self.txt_anon = QTextEdit(readOnly=True, placeholderText="Ergebnis...")
        self._set_accessible_context(
            self.txt_anon,
            name="Anonymisiertes Ergebnis",
            description="Zeigt das Ergebnis nach Anwendung aller aktiven Muster und Whitelists.",
            tooltip="Anonymisiertes Ergebnis",
        )
        preview_split.addWidget(self.txt_original)
        preview_split.addWidget(self.txt_anon)
        layout.addWidget(preview_split, stretch=1)
        
        self.lbl_status_detail = QLabel("Warte auf Clipboard...")
        self.lbl_status_detail.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.lbl_status_detail)

    # ---------------- TAB: VERLAUF ----------------
    def _setup_tab_history(self):
        layout = QVBoxLayout(self.tab_history)
        self.list_history = QListWidget(alternatingRowColors=True)
        self.list_history.itemDoubleClicked.connect(self._restore_history)
        self._set_accessible_context(
            self.list_history,
            name="Zwischenablagen-Verlauf",
            description="Liste der zuletzt kopierten Zwischenablage-Einträge. Doppelklick stellt den Eintrag her.",
            tooltip="Verlauf der Zwischenablage",
        )
        layout.addWidget(self.list_history)
        
        btn_restore = QPushButton("Wiederherstellen", clicked=self._restore_history)
        self._set_accessible_context(
            btn_restore,
            name="Originaltext wiederherstellen",
            description="Stellt den ausgewählten Verlaufseintrag im Original in der Zwischenablage wieder her.",
            tooltip="Ausgewählten Eintrag original wiederherstellen",
        )
        btn_restore_anon = QPushButton("Anonymisierten Text kopieren", clicked=self._restore_history_anon)
        self._set_accessible_context(
            btn_restore_anon,
            name="Anonymisierten Text kopieren",
            description="Anonymisiert den ausgewählten Verlaufseintrag und kopiert ihn in die Zwischenablage.",
            tooltip="Ausgewählten Eintrag anonymisiert kopieren",
        )
        btn_clear_history = QPushButton("Verlauf leeren", objectName="Danger", clicked=self._clear_history)
        self._set_accessible_context(
            btn_clear_history,
            name="Verlauf leeren",
            description="Löscht alle Einträge aus dem Verlauf der Zwischenablage.",
            tooltip="Gesamten Verlauf leeren",
        )

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(btn_restore)
        btn_layout.addWidget(btn_restore_anon)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_clear_history)
        layout.addLayout(btn_layout)

    # ---------------- CONFIG LOGIK ----------------
    def _load_config(self):
        if CONFIG_PATH.exists():
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                for entry in cfg.get("files", []):
                    # Einzelnen fehlerhaften Eintrag ueberspringen, statt das ganze
                    # Config-Laden (Status/Patterns/Checkboxes) abzubrechen.
                    if not (isinstance(entry, (list, tuple)) and len(entry) == 2):
                        continue
                    self._load_file_internal(entry[0], entry[1])
                self.ampel_status = _normalized_ampel_status(cfg.get("ampel_status"))
                self.case_sensitive = cfg.get("case_sensitive", False)
                self.whole_words = cfg.get("whole_words", False)
                
                # Builtin Patterns laden: Aliase auflösen + unbekannte Keys filtern
                self.builtin_enabled = _normalized_builtin_patterns(
                    cfg.get("builtin_patterns", {}),
                    defaults={key: info["default"] for key, info in BUILTIN_PATTERNS.items()},
                )
                
                self.cb_case.setChecked(self.case_sensitive)
                self.cb_words.setChecked(self.whole_words)
                
                # Pattern Checkboxes aktualisieren
                for key, cb in self.pattern_checkboxes.items():
                    cb.setChecked(self.builtin_enabled.get(key, False))
                
                self._set_ampel(self.ampel_status)
                self._update_pattern_stats()
            except Exception as e:
                logging.error(f"Config Error: {e}")
        else:
            self._set_ampel("rot")

    def _save_config(self):
        unique_files = []
        seen = set()
        for p, t in self.file_history:
            if (p, t) not in seen:
                seen.add((p, t))
                unique_files.append((p, t))
        cfg = {
            "files": unique_files,
            "ampel_status": self.ampel_status,
            "case_sensitive": self.case_sensitive,
            "whole_words": self.whole_words,
            "builtin_patterns": self.builtin_enabled  # NEU
        }
        try:
            # Atomar schreiben (tmp + replace): _save_config laeuft bei jedem Toggle/
            # Add/Delete/Ampelwechsel -> ein Crash waehrend json.dump wuerde sonst eine
            # leere/halbe config.json hinterlassen (Verlust aller Listen/Patterns).
            tmp = CONFIG_PATH.with_suffix(".tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2)
            tmp.replace(CONFIG_PATH)
        except Exception as e:
            logging.error(f"Config Save Error: {e}")

    # ---------------- PROFIL-AUSTAUSCH ----------------
    def _build_profile_payload(self):
        return build_profile_export_payload(
            sensitive=self.sensitive,
            whitelist=self.whitelist,
            builtin_enabled=self.builtin_enabled,
            ampel_status=self.ampel_status,
            case_sensitive=self.case_sensitive,
            whole_words=self.whole_words,
        )

    def _apply_profile_payload(self, payload):
        profile = normalize_profile_payload(payload)
        self.sensitive = profile["lists"]["sensibel"]
        self.whitelist = profile["lists"]["whitelist"]
        self.ampel_status = profile["settings"]["ampel_status"]
        self.case_sensitive = profile["settings"]["case_sensitive"]
        self.whole_words = profile["settings"]["whole_words"]
        self.builtin_enabled = profile["builtin_patterns"]

        self.cb_case.setChecked(self.case_sensitive)
        self.cb_words.setChecked(self.whole_words)
        for key, cb in self.pattern_checkboxes.items():
            cb.setChecked(self.builtin_enabled.get(key, False))

        self._compile_patterns()
        self._update_listboxes()
        self._update_pattern_stats()
        self._set_ampel(self.ampel_status)
        self._save_config()

    def _export_profile(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Profil exportieren",
            PROFILE_DEFAULT_FILENAME,
            "JSON (*.json)",
        )
        if not path:
            return
        try:
            write_profile_payload(Path(path), self._build_profile_payload())
            QMessageBox.information(self, "Profil exportiert", "Profil wurde ohne Verlauf und Rohtexte exportiert.")
        except Exception as e:
            QMessageBox.critical(self, "Export fehlgeschlagen", str(e))

    def _import_profile(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Profil importieren",
            "",
            "JSON (*.json)",
        )
        if not path:
            return
        try:
            self._apply_profile_payload(read_profile_payload(Path(path)))
            QMessageBox.information(self, "Profil importiert", "Profil wurde übernommen.")
        except Exception as e:
            QMessageBox.critical(self, "Import fehlgeschlagen", str(e))

    # ---------------- DATEI LOGIK ----------------
    def _load_files(self, typ):
        paths, _ = QFileDialog.getOpenFileNames(self, "Dateien laden", "", "Excel/Text (*.xlsx *.txt)")
        for path in paths: 
            self._load_file_internal(path, typ)
        self._save_config()
        self._update_listboxes()

    def _load_file_internal(self, path_str, typ):
        path = Path(path_str)
        if not path.exists(): return
        try:
            target = self.sensitive if typ == "sensibel" else self.whitelist
            content = read_first_column_values(path)
            for item in content:
                c = item.strip()
                if c and c not in target: 
                    target.append(c)
            self.file_history.append((str(path), typ))
            self._compile_patterns()
        except Exception as e:
            logging.error(f"File Load Error: {e}")

    def _export_list(self, typ):
        data = self.sensitive if typ == "sensibel" else self.whitelist
        path, _ = QFileDialog.getSaveFileName(self, "Export", "", "Text (*.txt)")
        if path:
            try: 
                Path(path).write_text("\n".join(data), encoding="utf-8")
            except Exception as e: 
                QMessageBox.critical(self, "Fehler", str(e))

    # ---------------- PATTERN KOMPILIERUNG (ERWEITERT) ----------------
    def _compile_patterns(self):
        flags = 0 if self.case_sensitive else re.IGNORECASE
        self.patterns = []
        white_set = set(self.whitelist)
        
        # 1. Manuelle sensible Begriffe
        for item in self.sensitive:
            if item in white_set: 
                continue
            esc = re.escape(item)
            pat = rf"(?<!\w){esc}(?!\w)" if self.whole_words else esc
            try:
                self.patterns.append(re.compile(pat, flags))
            except re.error as e:
                logging.warning(f"Ungültiges Regex-Pattern für '{item}': {e}")
        
        # 2. NEU: Eingebaute Regex-Patterns
        for key, enabled in self.builtin_enabled.items():
            if enabled and key in BUILTIN_PATTERNS:
                regex = BUILTIN_PATTERNS[key]["regex"]
                try:
                    self.patterns.append(re.compile(regex, flags))
                except Exception as e:
                    logging.error(f"Pattern Compile Error ({key}): {e}")

    def _update_listboxes(self):
        self.list_sens.clear()
        f = self.filter_sens.text().lower()
        for i in self.sensitive: 
            if not f or f in i.lower(): 
                self.list_sens.addItem(i)
        
        self.list_white.clear()
        f = self.filter_white.text().lower()
        for i in self.whitelist: 
            if not f or f in i.lower(): 
                self.list_white.addItem(i)

    def _add_manual(self, entry, target):
        t = entry.text().strip()
        if t and t not in target:
            target.append(t)
            entry.clear()
            self._compile_patterns()
            self._update_listboxes()
            self._save_config()

    def _delete_selected(self, lst, target):
        items = lst.selectedItems()
        if items and QMessageBox.question(self, "Löschen", f"{len(items)} löschen?") == QMessageBox.StandardButton.Yes:
            for i in items:
                if i.text() in target: 
                    target.remove(i.text())
            self._compile_patterns()
            self._update_listboxes()
            self._save_config()

    # ---------------- AMPEL LOGIK ----------------
    def _set_ampel(self, status):
        self.ampel_status = status
        colors = {"rot": ("#dc3545", "ROT"), "gelb": ("#ffc107", "GELB (Vorschau)"), "gruen": ("#28a745", "GRÜN (Aktiv)")}
        c, t = colors.get(status, ("#6c757d", "AUS"))
        
        self.lbl_ampel_icon.setStyleSheet(f"border-radius: 50px; background-color: {c}; border: 4px solid rgba(0,0,0,0.1);")
        self.lbl_ampel_text.setText(t)
        self.lbl_ampel_text.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {c};")
        
        if hasattr(self, 'tray_icon'):
            self._update_tray_icon_color()
        self._save_config()
        
        if hasattr(self, 'txt_original'):
            self._on_clipboard_change()

    def _on_option_change(self):
        self.case_sensitive = self.cb_case.isChecked()
        self.whole_words = self.cb_words.isChecked()
        self._compile_patterns()
        self._save_config()
        self._on_clipboard_change()

    def _anonymize(self, text):
        """Ersetzt sensible Textstellen durch [ANONYM].

        Single-Pass-Algorithmus (O((P+W)×N) statt O(P×W×N)):
        Whitelist-Spans werden einmal auf dem Originaltext berechnet; alle
        Pattern-Matches werden auf dem gleichen Originaltext gefunden und
        in einem einzigen right-to-left-Durchlauf substituiert.

        Semantische Anmerkung: Anders als beim früheren sequenziellen Ansatz
        werden alle Patterns gegen den ORIGINALEN Text ausgewertet. Das Ergebnis
        ist mindestens so schützend wie zuvor — in Grenzfällen mit sich
        überschneidenden Patterns sogar konsequenter.
        """
        if not text:
            return ""

        # Whitelist-Spans einmal auf dem Originaltext berechnen (O(W×N))
        protected_spans = _collect_literal_spans(
            text,
            self.whitelist,
            case_sensitive=self.case_sensitive,
            whole_words=self.whole_words,
        )

        # Alle zu ersetzenden Spans über alle Patterns sammeln
        to_replace: List[Tuple[int, int]] = []
        for pat in self.patterns:
            # Privacy-Fix: Whitelist-Spans die vollständig von einem Pattern-Match
            # überdeckt werden, schützen diesen Match nicht (IBAN-Teilstring-Bug)
            effective_protected = _filter_spans_for_pattern(text, pat, protected_spans)
            for m in pat.finditer(text):
                start, end = m.start(), m.end()
                if start == end:
                    continue
                # Match nur ersetzen wenn nicht durch Whitelist-Span geschützt
                if not any(
                    p_start <= start and end <= p_end
                    for p_start, p_end in effective_protected
                ):
                    to_replace.append((start, end))

        if not to_replace:
            return text

        # Überlappende Spans mergen
        to_replace.sort()
        merged: List[Tuple[int, int]] = []
        cur_start, cur_end = to_replace[0]
        for start, end in to_replace[1:]:
            if start <= cur_end:
                cur_end = max(cur_end, end)
            else:
                merged.append((cur_start, cur_end))
                cur_start, cur_end = start, end
        merged.append((cur_start, cur_end))

        # Right-to-left substituieren (verhindert Offset-Verschiebung)
        chars = list(text)
        for start, end in reversed(merged):
            chars[start:end] = list("[ANONYM]")
        return "".join(chars)

    # ---------------- CLIPBOARD LOGIK ----------------
    def _on_clipboard_change(self):
        if not hasattr(self, 'clipboard') or self.clipboard is None:
            return
        if self.clipboard_lock:
            return

        try:
            data = self.clipboard.mimeData()
            if not data or not data.hasText():
                return
            text = data.text()
        except Exception as e:
            logging.error(f"Clipboard Error: {e}")
            return

        # Re-Entry-Guard: eigenen Clipboard-Write ignorieren (Windows queued
        # dataChanged — Signal trifft erst NACH setText() ein, wenn der bool-Lock
        # längst zurückgesetzt wurde).
        if text is not None and text == self._last_written_text:
            self._last_written_text = None
            return
        
        # History aktualisieren
        if not self.clip_history or self.clip_history[0] != text:
            self.clip_history.insert(0, text)
            if len(self.clip_history) > HISTORY_LIMIT: 
                self.clip_history.pop()
            self.list_history.clear()
            for i in self.clip_history:
                preview = i[:100].replace("\n", " ")
                if len(i) > 100:
                    preview += "..."
                self.list_history.addItem(preview)

        anon = self._anonymize(text)
        self.txt_original.setPlainText(text)
        self.txt_anon.setPlainText(anon)

        # Ampel-Status verarbeiten
        if self.ampel_status == "rot":
            self.lbl_status_detail.setText("ROT: Keine Änderung am Clipboard.")
        elif self.ampel_status == "gelb":
            if text != anon:
                self.lbl_status_detail.setText("GELB: Vorschau - " + str(len(self.patterns)) + " Patterns aktiv.")
            else:
                self.lbl_status_detail.setText("GELB: Vorschau - Keine Treffer.")
        elif self.ampel_status == "gruen":
            if text != anon:
                self._last_written_text = anon  # Re-Entry-Guard setzen
                self.clipboard.setText(anon)
                self.lbl_status_detail.setText("GRÜN: Automatisch anonymisiert!")
                self.txt_original.setPlainText(text)
                self.txt_anon.setPlainText(anon)
            else:
                self.lbl_status_detail.setText("GRÜN: Sauber - Keine sensiblen Daten.")

    def _restore_history(self):
        r = self.list_history.currentRow()
        if r >= 0:
            self._last_written_text = self.clip_history[r]  # Re-Entry-Guard setzen
            self.clipboard.setText(self.clip_history[r])
            self.statusBar().showMessage("Wiederhergestellt.")

    def _restore_history_anon(self):
        r = self.list_history.currentRow()
        if r >= 0:
            anon = self._anonymize(self.clip_history[r])
            self._last_written_text = anon  # Re-Entry-Guard setzen
            self.clipboard.setText(anon)
            self.statusBar().showMessage("Anonymisiert kopiert.")

    def _clear_history(self):
        self.clip_history.clear()
        self.list_history.clear()
        self.statusBar().showMessage("Verlauf geleert.")


# ==================== MAIN ====================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setQuitOnLastWindowClosed(False)
    
    window = AmpelTool()
    window.show()
    sys.exit(app.exec())
