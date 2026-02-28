# Changelog / Aenderungsprotokoll

Alle wesentlichen Aenderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

## [6.2.0] - 2026-01-03

### Hinzugefuegt / Added
- Eingebaute Regex-Patterns (IBAN, E-Mail, Telefon, Kreditkarten, PLZ, Datum)
- Neuer Tab "Regex-Patterns" mit aktivierbaren Mustertypen
- Live-Vorschau: Original vs. anonymisierter Text nebeneinander
- Korrektes SystemTray-Shutdown (atexit-Fix)

### Geaendert / Changed
- 4-Tab-Interface (Listenverwaltung, Regex-Patterns, Ampelsteuerung, Verlauf)
- IBAN und E-Mail standardmaessig aktiviert

## [5.0.0] - 2025-08-16

### Hinzugefuegt / Added
- Erstveroeffentlichung / Initial release
- Ampel-System (Rot/Gelb/Gruen)
- Sensibel-Liste und Whitelist mit Import/Export
- System-Tray-Integration mit Farbindikator
- Clipboard-History (15 Eintraege)
