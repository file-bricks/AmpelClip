# macOS-/Linux-Source-Smoke AmpelClip

Stand: 2026-07-03

## Zweck

Dieser Smoke ist kein nativer macOS-/Linux-Release und kein Packaging-Versprechen. Er prüft, ob die PySide6-Source-Linie grundsätzlich ohne Windows-EXE-/Store-Kontext startet und ob die plattformkritischen Stellen sichtbar bleiben:

- App-Start aus Source mit `python Ampel6.py`-Importpfad
- System-Tray-Verfügbarkeit als Laufzeitbedingung
- Clipboard-Zugriff über Qt statt Windows-spezifische APIs
- Konfigurationspfad ohne User- oder Store-Artefakte

## Ausführung

```powershell
$env:PYTHONIOENCODING = "utf-8"
$env:QT_QPA_PLATFORM = "offscreen"
python tests\source_platform_smoke.py
```

Auf macOS/Linux kann `QT_QPA_PLATFORM=offscreen` weggelassen werden, wenn ein echter Desktop-Smoke mit sichtbarem Fenster gewünscht ist. Für CI oder headless Läufe bleibt `offscreen` der erwartete Modus.

## Prüfvertrag

| Bereich | Smoke-Prüfung | Aussage |
|---|---|---|
| Start | `Ampel6` importieren und `AmpelTool` ohne Eventloop-Start instanziieren | Source-Start bricht nicht schon beim GUI-Aufbau ab |
| Tray | `QSystemTrayIcon.isSystemTrayAvailable()` wird gelesen und als boolescher Laufzeitzustand behandelt | Kein harter Anspruch, dass jede Linux-/macOS-Shell einen Tray hat |
| Clipboard | Qt-Clipboard nimmt Text an und `_on_clipboard_change()` erzeugt Original-/Anonymisiert-Vorschau | Kernlogik hängt nicht an Windows-Clipboard-APIs |
| Konfiguration | `AMPELCLIP_CONFIG_PATH` zeigt auf eine temporäre Datei und `_save_config()` schreibt dort atomar | Source-Smoke bleibt frei von lokalen Nutzerpfaden |

## Grenzen

- Wayland, X11, GNOME/KDE-Tray-Verhalten und macOS-Menüleistenintegration werden hier nicht vollständig validiert.
- Der Smoke prüft keinen PyInstaller-, DMG-, AppImage-, Flatpak-, Snap-, Deb- oder RPM-Build.
- Automatische globale Clipboard-Überwachung auf macOS/Linux bleibt eine separate Produktentscheidung nach echter Nutzer-Nachfrage.
- Für Store- oder Release-Aussagen bleiben Windows-Store-Preflight, MSIX und WACK getrennte Gates.

## Erfolgsbedingung

Der Smoke gilt als grün, wenn `tests/source_platform_smoke.py` mit Exitcode `0` endet und diese Marker ausgibt:

```text
source_start=PASS
tray_runtime_gate=PASS
clipboard_preview=PASS
config_path=PASS
```
