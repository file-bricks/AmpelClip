"""
AmpelTool V6 - Datenschutz & Clipboard Monitor
Neu: Eingebaute Regex-Patterns fuer IBAN, Email, Telefon, Kreditkarten
"""

import sys
import json
import re
import logging
from pathlib import Path
from typing import List, Tuple, Dict

import pandas as pd
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QPushButton, QLabel, QLineEdit, QListWidget, 
    QTextEdit, QFileDialog, QMessageBox, QFrame, QCheckBox, 
    QSplitter, QSystemTrayIcon, QMenu, QGroupBox
)
from PyQt6.QtCore import Qt, QSize, QEvent
from PyQt6.QtGui import QAction, QIcon, QColor, QPixmap, QPainter, QBrush

# --- Konfiguration ---
CONFIG_PATH = Path(__file__).parent / "config.json"
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
        "regex": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
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
        self.tab_patterns = QWidget()  # NEU: Tab fuer Patterns
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

    # ---------------- SYSTEM TRAY LOGIK ----------------
    def _setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setToolTip("AmpelTool V6 Datenschutz")
        self._update_tray_icon_color()

        tray_menu = QMenu()
        action_show = QAction("Anzeigen", self)
        action_show.triggered.connect(self.show_window)
        tray_menu.addAction(action_show)
        tray_menu.addSeparator()
        action_quit = QAction("Beenden", self)
        action_quit.triggered.connect(self.quit_app)
        tray_menu.addAction(action_quit)
        
        self.tray_icon.setContextMenu(tray_menu)
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
        else:
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "AmpelTool minimiert",
                "Laeuft im Hintergrund weiter.",
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
        
        btn_load_white = QPushButton("Import Whitelist")
        btn_load_white.setObjectName("Success")
        btn_load_white.clicked.connect(lambda: self._load_files("whitelist"))
        
        files_layout.addWidget(btn_load_sens)
        files_layout.addWidget(btn_load_white)
        files_layout.addWidget(QPushButton("Export Sensibel", clicked=lambda: self._export_list("sensibel")))
        files_layout.addWidget(QPushButton("Export Whitelist", clicked=lambda: self._export_list("whitelist")))
        
        layout.addWidget(QLabel("Dateioperationen", objectName="Header"))
        layout.addWidget(frame_files)

        frame_manual = QFrame()
        manual_layout = QHBoxLayout(frame_manual)
        
        self.entry_sens = QLineEdit(placeholderText="Neuer sensibler Begriff...")
        self.entry_sens.returnPressed.connect(lambda: self._add_manual(self.entry_sens, self.sensitive))
        btn_add_sens = QPushButton("Hinzufuegen", objectName="Danger")
        btn_add_sens.clicked.connect(lambda: self._add_manual(self.entry_sens, self.sensitive))

        self.entry_white = QLineEdit(placeholderText="Neuer Whitelist Begriff...")
        self.entry_white.returnPressed.connect(lambda: self._add_manual(self.entry_white, self.whitelist))
        btn_add_white = QPushButton("Hinzufuegen", objectName="Success")
        btn_add_white.clicked.connect(lambda: self._add_manual(self.entry_white, self.whitelist))

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
        l_sens.addWidget(self.filter_sens)
        self.list_sens = QListWidget()
        self.list_sens.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        l_sens.addWidget(self.list_sens)
        btn_del_sens = QPushButton("Ausgewaehlte loeschen")
        btn_del_sens.clicked.connect(lambda: self._delete_selected(self.list_sens, self.sensitive))
        l_sens.addWidget(btn_del_sens)
        
        w_white = QWidget()
        l_white = QVBoxLayout(w_white)
        l_white.setContentsMargins(0,0,0,0)
        l_white.addWidget(QLabel("Whitelist (Gruen)"))
        self.filter_white = QLineEdit(placeholderText="Filter...")
        self.filter_white.textChanged.connect(self._update_listboxes)
        l_white.addWidget(self.filter_white)
        self.list_white = QListWidget()
        self.list_white.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        l_white.addWidget(self.list_white)
        btn_del_white = QPushButton("Ausgewaehlte loeschen")
        btn_del_white.clicked.connect(lambda: self._delete_selected(self.list_white, self.whitelist))
        l_white.addWidget(btn_del_white)

        splitter.addWidget(w_sens)
        splitter.addWidget(w_white)
        layout.addWidget(splitter, stretch=1)

    # ---------------- TAB: REGEX-PATTERNS (NEU) ----------------
    def _setup_tab_patterns(self):
        layout = QVBoxLayout(self.tab_patterns)
        
        layout.addWidget(QLabel("Eingebaute Datenschutz-Patterns", objectName="Header"))
        layout.addWidget(QLabel("Aktiviere Pattern-Typen um automatisch sensible Daten zu erkennen:"))
        
        # GroupBox fuer Patterns
        group = QGroupBox("Verfuegbare Patterns")
        group_layout = QVBoxLayout(group)
        
        self.pattern_checkboxes: Dict[str, QCheckBox] = {}
        
        for key, info in BUILTIN_PATTERNS.items():
            cb = QCheckBox(f"{info['name']} - {info['description']}")
            cb.setChecked(self.builtin_enabled.get(key, info["default"]))
            cb.stateChanged.connect(self._on_pattern_toggle)
            cb.setProperty("pattern_key", key)
            self.pattern_checkboxes[key] = cb
            group_layout.addWidget(cb)
        
        layout.addWidget(group)
        
        # Info-Box
        info_frame = QFrame()
        info_frame.setStyleSheet("background-color: #e7f3ff; border: 1px solid #b6d4fe; border-radius: 4px; padding: 10px;")
        info_layout = QVBoxLayout(info_frame)
        info_layout.addWidget(QLabel("<b>Hinweis:</b>"))
        info_layout.addWidget(QLabel("Diese Patterns erkennen typische Formate automatisch."))
        info_layout.addWidget(QLabel("Sie ergaenzen die manuellen Listen im Tab 'Listenverwaltung'."))
        info_layout.addWidget(QLabel("IBAN und Email sind standardmaessig aktiviert."))
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
        self.lbl_ampel_text = QLabel("ROT")
        vis_layout.addStretch()
        vis_layout.addWidget(self.lbl_ampel_icon)
        vis_layout.addWidget(self.lbl_ampel_text)
        vis_layout.addStretch()
        layout.addWidget(vis_container)

        ctrl_container = QHBoxLayout()
        btn_rot = QPushButton("STOP (Rot)", objectName="Danger", minimumHeight=40)
        btn_rot.clicked.connect(lambda: self._set_ampel("rot"))
        btn_gelb = QPushButton("PREVIEW (Gelb)", objectName="Warning", minimumHeight=40)
        btn_gelb.clicked.connect(lambda: self._set_ampel("gelb"))
        btn_gruen = QPushButton("ACTIVE (Gruen)", objectName="Success", minimumHeight=40)
        btn_gruen.clicked.connect(lambda: self._set_ampel("gruen"))
        ctrl_container.addWidget(btn_rot)
        ctrl_container.addWidget(btn_gelb)
        ctrl_container.addWidget(btn_gruen)
        layout.addLayout(ctrl_container)

        opt_container = QHBoxLayout()
        self.cb_case = QCheckBox("Gross-/Kleinschreibung beachten")
        self.cb_case.stateChanged.connect(self._on_option_change)
        self.cb_words = QCheckBox("Nur ganze Woerter")
        self.cb_words.stateChanged.connect(self._on_option_change)
        opt_container.addWidget(self.cb_case)
        opt_container.addWidget(self.cb_words)
        opt_container.addStretch()
        layout.addLayout(opt_container)

        layout.addSpacing(20)
        layout.addWidget(QLabel("Vorschau (Live-Anonymisierung):", objectName="Header"))
        preview_split = QSplitter(Qt.Orientation.Horizontal)
        self.txt_original = QTextEdit(readOnly=True, placeholderText="Original...")
        self.txt_anon = QTextEdit(readOnly=True, placeholderText="Ergebnis...")
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
        layout.addWidget(self.list_history)
        
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(QPushButton("Wiederherstellen", clicked=self._restore_history))
        btn_layout.addWidget(QPushButton("Anonymisiert Kopieren", clicked=self._restore_history_anon))
        btn_layout.addStretch()
        btn_layout.addWidget(QPushButton("Verlauf leeren", objectName="Danger", clicked=self._clear_history))
        layout.addLayout(btn_layout)

    # ---------------- CONFIG LOGIK ----------------
    def _load_config(self):
        if CONFIG_PATH.exists():
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                for path, typ in cfg.get("files", []):
                    self._load_file_internal(path, typ)
                self.ampel_status = cfg.get("ampel_status", "rot")
                self.case_sensitive = cfg.get("case_sensitive", False)
                self.whole_words = cfg.get("whole_words", False)
                
                # NEU: Builtin Patterns laden
                self.builtin_enabled = cfg.get("builtin_patterns", self.builtin_enabled)
                
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
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2)
        except Exception as e:
            logging.error(f"Config Save Error: {e}")

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
            if path.suffix == ".xlsx":
                content = pd.read_excel(path, header=None).squeeze().astype(str).tolist()
            else:
                content = path.read_text(encoding="utf-8").splitlines()
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
            except: 
                pass
        
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
        if items and QMessageBox.question(self, "Loeschen", f"{len(items)} loeschen?") == QMessageBox.StandardButton.Yes:
            for i in items:
                if i.text() in target: 
                    target.remove(i.text())
            self._compile_patterns()
            self._update_listboxes()
            self._save_config()

    # ---------------- AMPEL LOGIK ----------------
    def _set_ampel(self, status):
        self.ampel_status = status
        colors = {"rot": ("#dc3545", "ROT"), "gelb": ("#ffc107", "GELB (Vorschau)"), "gruen": ("#28a745", "GRUEN (Aktiv)")}
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
        if not text: 
            return ""
        for pat in self.patterns: 
            text = pat.sub("[ANONYM]", text)
        return text

    # ---------------- CLIPBOARD LOGIK ----------------
    def _on_clipboard_change(self):
        if not hasattr(self, 'clipboard'): 
            return
        if self.clipboard_lock: 
            return
        
        data = self.clipboard.mimeData()
        if not data.hasText(): 
            return
        text = data.text()
        
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
            self.lbl_status_detail.setText("ROT: Keine Aenderung am Clipboard.")
        elif self.ampel_status == "gelb":
            if text != anon:
                self.lbl_status_detail.setText("GELB: Vorschau - " + str(len(self.patterns)) + " Patterns aktiv.")
            else:
                self.lbl_status_detail.setText("GELB: Vorschau - Keine Treffer.")
        elif self.ampel_status == "gruen":
            if text != anon:
                self.clipboard_lock = True
                self.clipboard.setText(anon)
                self.clipboard_lock = False
                self.lbl_status_detail.setText("GRUEN: Automatisch anonymisiert!")
                self.txt_original.setPlainText(text)
                self.txt_anon.setPlainText(anon)
            else:
                self.lbl_status_detail.setText("GRUEN: Sauber - Keine sensiblen Daten.")

    def _restore_history(self):
        r = self.list_history.currentRow()
        if r >= 0:
            self.clipboard_lock = True
            self.clipboard.setText(self.clip_history[r])
            self.clipboard_lock = False
            self.statusBar().showMessage("Wiederhergestellt.")

    def _restore_history_anon(self):
        r = self.list_history.currentRow()
        if r >= 0:
            self.clipboard_lock = True
            self.clipboard.setText(self._anonymize(self.clip_history[r]))
            self.clipboard_lock = False
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
