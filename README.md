# AmpelClip

Datenschutz-Ampel fuer Zwischenablage-Ueberwachung. Erkennt sensible Daten (IBAN, E-Mail, Telefonnummern, Kreditkarten) in Echtzeit und anonymisiert Clipboard-Inhalte automatisch.

## Funktionen

- **Ampel-System** -- Rot (blockiert) / Gelb (Vorschau) / Gruen (Auto-Anonymisierung)
- **Eingebaute Regex-Patterns** -- IBAN, E-Mail, Telefon (DE), Kreditkarten, PLZ, Datum
- **Eigene Wortlisten** -- Sensibel-Liste und Whitelist mit Import/Export (TXT, Excel)
- **System-Tray-Integration** -- Farbiges Icon zeigt aktuellen Status
- **Clipboard-Verlauf** -- Letzte 15 Eintraege mit Wiederherstellen und anonymisiertem Kopieren
- **Live-Vorschau** -- Original vs. anonymisierter Text nebeneinander

## Voraussetzungen

- Python 3.10+
- Windows

## Installation

```bash
pip install -r requirements.txt
```

## Verwendung

```bash
python Ampel6.py
```

Oder ueber `START.bat`.

### EXE erstellen

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --icon=ICO.ico --name=AmpelClip Ampel6.py
```

## Konfiguration

Einstellungen werden in `config.json` gespeichert (wird beim ersten Start automatisch erstellt).

| Einstellung | Beschreibung |
|-------------|-------------|
| `builtin_patterns` | Regex-Patterns aktivieren/deaktivieren |
| `ampel_status` | Aktueller Ampel-Status |
| `case_sensitive` | Gross-/Kleinschreibung beachten |
| `whole_words` | Nur ganze Woerter |
| `files` | Importierte Listendateien |

## So funktioniert es

1. Ampel auf gewuenschten Modus setzen (Rot/Gelb/Gruen)
2. Sensible Begriffe importieren oder eingebaute Patterns aktivieren
3. AmpelClip ueberwacht die Zwischenablage in Echtzeit
4. **Rot** -- Keine Aktion, nur Anzeige
5. **Gelb** -- Vorschau, zeigt was anonymisiert wuerde
6. **Gruen** -- Ersetzt sensible Daten automatisch durch `[ANONYM]`

## Autor

Lukas Geiger ([@lukisch](https://github.com/lukisch))

---

## English

Privacy traffic light for clipboard monitoring. Detects sensitive data (IBAN, email, phone numbers, credit cards) in real-time and anonymizes clipboard content automatically.

### Features

- **Traffic Light System** -- Red (blocked) / Yellow (preview) / Green (auto-anonymization)
- **Built-in Regex Patterns** -- IBAN, email, phone (DE), credit cards, postal codes, dates
- **Custom Word Lists** -- Sensitive list and whitelist with import/export (TXT, Excel)
- **System Tray Integration** -- Colored icon shows current status
- **Clipboard History** -- Last 15 entries with restore and anonymized copy
- **Live Preview** -- Original vs. anonymized text side by side

### Requirements

- Python 3.10+
- Windows

### Installation

```bash
pip install -r requirements.txt
```

### Usage

```bash
python Ampel6.py
```

Or via `START.bat`.

#### Build Executable

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --icon=ICO.ico --name=AmpelClip Ampel6.py
```

### Configuration

Settings are saved in `config.json` (auto-generated on first run).

| Setting | Description |
|---------|-------------|
| `builtin_patterns` | Enable/disable pattern types |
| `ampel_status` | Current traffic light state |
| `case_sensitive` | Case-sensitive matching |
| `whole_words` | Whole-word matching only |
| `files` | Previously imported list files |

### How It Works

1. Set the traffic light to the desired mode (Red/Yellow/Green)
2. Import sensitive terms or enable built-in patterns
3. AmpelClip monitors the clipboard in real-time
4. **Red** -- No action, display only
5. **Yellow** -- Preview, shows what would be anonymized
6. **Green** -- Automatically replaces sensitive data with `[ANONYM]`

### Author

Lukas Geiger ([@lukisch](https://github.com/lukisch))

## License

GPL-3.0 -- see [LICENSE](LICENSE)

> **Keine Garantie vollständiger Schwärzung/Anonymisierung.** Dieses Werkzeug unterstützt Privacy-Prozesse, kann sie aber nicht vollständig automatisieren. Manuelle Nachkontrolle ist Pflicht.
>
> **No guarantee of complete redaction/anonymization.** This tool supports privacy processes but cannot fully automate them. Manual review is required.


---

## Haftung / Liability

Dieses Projekt ist eine **unentgeltliche Open-Source-Schenkung** im Sinne der §§ 516 ff. BGB. Die Haftung des Urhebers ist gemäß **§ 521 BGB** auf **Vorsatz und grobe Fahrlässigkeit** beschränkt. Ergänzend gelten die Haftungsausschlüsse aus GPL-3.0 / MIT / Apache-2.0 §§ 15–16 (je nach gewählter Lizenz).

Nutzung auf eigenes Risiko. Keine Wartungszusage, keine Verfügbarkeitsgarantie, keine Gewähr für Fehlerfreiheit oder Eignung für einen bestimmten Zweck.

This project is an unpaid open-source donation. Liability is limited to intent and gross negligence (§ 521 German Civil Code). Use at your own risk. No warranty, no maintenance guarantee, no fitness-for-purpose assumed.

