# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### Geändert / Changed (2026-07-29)

- **UX / Barrierefreiheit & deutsche Rechtschreibkorrektur:** 
  Sämtliche UI-Elemente in `Ampel6.py` (Buttons, Eingabefelder, Listboxen, Vorschau- und Verlaufsanzeigen) wurden mit expliziten Accessibility-Kontexten (`AccessibleName`, `AccessibleDescription`, `ToolTip`) über `_set_accessible_context` ausgestattet. 
  Textuelle End-User-Schreibweise korrigiert ("Gross-/Kleinschreibung" -> "Groß-/Kleinschreibung"). Barrierefreiheits-Tests in `tests/test_ui_accessibility.py` erweitert und verifiziert (24/24 passed).

### Geändert / Changed (2026-07-26)

- **Abhängigkeiten & Lizenzinventar bereinigt (TW-AC-02):** Unbenutztes `pyperclip`
  aus `requirements.txt` und `THIRD_PARTY_LICENSES.txt` entfernt. `openpyxl>=3.0.0`
  (v3.1.5) als direkte Laufzeit-/Test-Abhängigkeit für Excel-Dateitests ergänzt.
  58/58 Pytest-Tests grün.

### Hinzugefügt / Added (2026-07-03)

- **macOS-/Linux-Source-Smoke dokumentiert:** Neues
  `MACOS_LINUX_SOURCE_SMOKE.md` plus ausführbarer Smoke
  `tests/source_platform_smoke.py` prüfen Source-Start, Tray-Laufzeitgate,
  Qt-Clipboard-Vorschau und temporären Config-Pfad ohne Packaging-Claim.
  `tests/test_source_platform_smoke_contract.py` hält Runbook und Smoke-Marker
  synchron.
- **Headless-Clipboard-Guard:** `_on_clipboard_change()` ignoriert jetzt auch
  fehlende Qt-`mimeData()`-Objekte sauber, statt bei Offscreen-/Headless-Smokes
  vor einem echten Clipboard-Text abzubrechen.

### Hinzugefügt / Added (2026-07-01)

- **Windows-Store-Readiness vorbereitet:** Store-Metadaten (`store_package.json`,
  `releases/windowsstore/store_settings.json`), Store-Listing DE/EN,
  Datenschutz-/Supporttexte und `releases/windowsstore/WINDOWS_STORE_PREP.md`
  ergänzt. Neuer Preflight `scripts/check_store_readiness.py` trennt vorhandene
  Store-Materialien von externen Gates (Partner Center, MSIX, WACK); Regressionen
  in `tests/test_store_readiness.py` sichern den erwarteten Blocker-Status.
- **Store-tauglicher Config-Pfad:** Frozen EXE-/Store-Builds schreiben Einstellungen
  jetzt nach `%LOCALAPPDATA%\AmpelClip\config.json`; Source-Starts bleiben beim
  projektlokalen `config.json`.

### Hinzugefügt / Added (2026-06-28)

- **Ampel-Status-Toggle im Web Companion:** Der Ampel-Status (rot/gelb/grün) war bisher nur
  als Anzeige sichtbar, aber nicht im Browser editierbar. Neu: Button „Status umschalten" wechselt
  den Status im Zyklus rot → gelb → grün → rot und speichert ihn im localStorage. Der Status
  steuert das Desktop-Verhalten beim Profil-Export; er hat keinen Effekt auf die Anonymisierung
  im Browser — ein Hinweistext macht das transparent.
  Reine Logik in `nextAmpelStatus()` (exportiert aus `library.js`, unit-getestet);
  DOM-Wiring in `app.js`; 7 neue Tests (59/59 grün).

### Behoben / Fixed (Bugsweep 2026-06-28)

- **_anonymize Performance (Bug 1):** `_anonymize` hatte O(P×W×N)-Komplexität und führte bei
  großen Whitelists (~500 Terme) und langem Clipboard-Text (~50.000 Zeichen) zu ~22 s GUI-Freeze.
  Ersetzt durch Single-Pass O((P+W)×N): Whitelist-Spans werden einmal auf dem Originaltext
  berechnet; alle Pattern-Matches auf dem gleichen Originaltext gesammelt, überlappende Spans
  gemergt und in einem einzigen right-to-left-Durchlauf substituiert. Semantik (sichere Richtung):
  alle Patterns gegen Originaltext, Ergebnis mindestens so schützend wie zuvor.

- **clipboard_lock Re-Entry-Guard (Bug 2):** Auf Windows trifft das `dataChanged`-Signal nach
  `clipboard.setText(anon)` verzögert ein (Nachrichtenqueue). Der `clipboard_lock`-Boolean war
  beim Eintreffen des Signals bereits auf `False` zurückgesetzt — der Lock griff nicht, der selbst
  geschriebene Anon-Text durchlief `_on_clipboard_change` erneut. Fix: `_last_written_text`
  Re-Entry-Guard — eigener `setText`-Aufruf merkt den Text; kommt er über `dataChanged` zurück,
  wird er ignoriert. Gilt für alle drei `setText`-Stellen.

- **manage_translations.py Quote-Bug (Bug 3):** `STRING_PATTERNS` nutzte `[^"\']+` als
  Zeichenklasse, die weder `"` noch `'` erlaubt — Strings mit Apostrophen wurden abgeschnitten.
  Behoben durch getrennte Double-Quote- (`[^"]+`) und Single-Quote-Varianten (`[^']+`) pro Funktion.

### Added
- Separate German `README_de.md` with installation, workflow, limitations and search context.
- iOS/PWA installability assets: PNG app icons, Apple touch icon metadata, safe-area CSS and regression tests for install prompt, service worker offline fallback and query-insensitive cache hits.

### Changed
- README now links to the German README and sharpens the search/disambiguation context for local clipboard privacy, clipboard anonymization and redaction workflows.
- `llms.txt` updated for the 2026-06-13 visibility check with additional search phrases and external-discovery notes.
- Web Companion metadata now includes English discovery terms for clipboard privacy, local-first anonymization and redaction.
- `.gitignore` now excludes project locks, local env/credential files, local databases and automation planning folders before publication.

### Behoben / Fixed
- Die manuellen Sensibel-/Whitelist-Felder und die beiden Filterfelder exponieren jetzt sprechende Accessible Names, Descriptions und Tooltips, statt sich für Screenreader fast nur auf Position und Placeholder zu verlassen.
- Whitelist-Teiltreffer innerhalb eines größeren sensiblen Regex-Treffers schützen den Match nicht mehr fälschlich. Dadurch bleiben IBANs oder ähnliche Formatdaten nicht mehr teilweise im Klartext, wenn z. B. nur eine Bankleitzahl in der Whitelist steht.
- Whitelist-Einträge schützen jetzt auch Treffer aus eingebauten Regex-Patterns. Vorher wurden z. B. freigegebene E-Mail-Adressen trotz Whitelist weiter anonymisiert, sobald das eingebaute E-Mail-Pattern aktiv war.
- Regressionstest ergänzt: Whitelist bewahrt freigegebene Builtin-Regex-Treffer, während andere Treffer im selben Text weiter anonymisiert werden.

### Geändert / Changed
- README als klarere GitHub-Landing-Page mit English-first Einstieg, Suchkontext, korrekter MIT-Lizenz und echter Umlautschreibung überarbeitet.
- `llms.txt` mit `## Audience`, `## Search Phrases` (Fenced-Block-Format) und `## Last-checked` auf aktuellen Standard gebracht.
- Community-Workflows auf aktuelle Action-Versionen aktualisiert.
- `.gitignore` um Muster für Entwicklungs-Artefakte (`*.bak`, `*_FINAL_*`) erweitert.
- `build_exe.bat` als Hilfsskript für reproduzierbare Builds hinzugefügt.

### Build / Release
- EXE neu gebaut 2026-06-01 (PyInstaller, `AmpelTool_V6.spec`); Smoke-Test bestanden (Prozess stabil nach 8 s). Vorherige EXE war vom 2026-05-17, Source (`Ampel6.py`) vom 2026-06-01.

### Hinzugefügt / Added
- Desktop-Export und -Import für `ampelclip-profile-v1.json` ergänzt; das Profil enthält Ampel-Modus, Regex-Schalter, Sensibel-Liste und Whitelist, aber keine Clipboard-Historie, Rohtexte oder lokalen Dateipfade.
- Regressionstests für Profil-Schema, UTF-8/Umlaute, Alias-Import und falsche Schema-Version ergänzt.
- Austauschformat `ampelclip-profile-v1.json` für spätere plattformübergreifende Profilübergabe skizziert.
- Planungsordner `web_companion/` für eine spätere PWA-Linie angelegt.

## [6.2.0] - 2026-01-03

### Hinzugefügt / Added
- Eingebaute Regex-Patterns (IBAN, E-Mail, Telefon, Kreditkarten, PLZ, Datum)
- Neuer Tab "Regex-Patterns" mit aktivierbaren Mustertypen
- Live-Vorschau: Original vs. anonymisierter Text nebeneinander
- Korrektes SystemTray-Shutdown (atexit-Fix)

### Geändert / Changed
- 4-Tab-Interface (Listenverwaltung, Regex-Patterns, Ampelsteuerung, Verlauf)
- IBAN und E-Mail standardmäßig aktiviert

## [5.0.0] - 2025-08-16

### Hinzugefügt / Added
- Erstveröffentlichung / Initial release
- Ampel-System (Rot/Gelb/Grün)
- Sensibel-Liste und Whitelist mit Import/Export
- System-Tray-Integration mit Farbindikator
- Clipboard-History (15 Einträge)
