# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### Added
- Separate German `README_de.md` with installation, workflow, limitations and search context.
- iOS/PWA installability assets: PNG app icons, Apple touch icon metadata, safe-area CSS and regression tests for install prompt, service worker offline fallback and query-insensitive cache hits.

### Changed
- README now links to the German README and sharpens the search/disambiguation context for local clipboard privacy, clipboard anonymization and redaction workflows.
- `llms.txt` updated for the 2026-06-13 visibility check with additional search phrases and external-discovery notes.
- Web Companion metadata now includes English discovery terms for clipboard privacy, local-first anonymization and redaction.
- `.gitignore` now excludes project locks, local env/credential files, local databases and automation planning folders before publication.

### Behoben / Fixed
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
