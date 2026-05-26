# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### Geändert / Changed
- README als klarere GitHub-Landing-Page mit English-first Einstieg, Suchkontext, korrekter MIT-Lizenz und echter Umlautschreibung überarbeitet.
- `llms.txt` als maschinenlesbarer Projektkontext ergänzt.
- Community-Workflows auf aktuelle Action-Versionen aktualisiert.

### Hinzugefügt / Added
- Portierungsplan für Windows Store, Web/PWA-Companion, Android/iOS-PWA-Smokes sowie macOS/Linux-Source-Smokes ergänzt.
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
