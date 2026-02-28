# AmpelClip

Datenschutz-Ampel fuer Zwischenablage-Ueberwachung. Erkennt sensible Daten (IBAN, E-Mail, Telefonnummern, Kreditkarten) in Echtzeit und anonymisiert Clipboard-Inhalte automatisch.

Privacy traffic light for clipboard monitoring. Detects sensitive data (IBAN, email, phone numbers, credit cards) in real-time and anonymizes clipboard content automatically.

## Funktionen / Features

- **Ampel-System / Traffic Light** -- Rot (blockiert) / Gelb (Vorschau) / Gruen (Auto-Anonymisierung)
- **Eingebaute Regex-Patterns** -- IBAN, E-Mail, Telefon (DE), Kreditkarten, PLZ, Datum
- **Eigene Wortlisten / Custom Word Lists** -- Sensibel-Liste und Whitelist mit Import/Export (TXT, Excel)
- **System-Tray-Integration** -- Farbiges Icon zeigt aktuellen Status
- **Clipboard-Verlauf / History** -- Letzte 15 Eintraege mit Wiederherstellen und anonymisiertem Kopieren
- **Live-Vorschau / Preview** -- Original vs. anonymisierter Text nebeneinander

## Voraussetzungen / Requirements

- Python 3.10+
- Windows

## Installation

```bash
pip install -r requirements.txt
```

## Verwendung / Usage

```bash
python Ampel6.py
```

Oder ueber `START.bat`.

### EXE erstellen / Build executable

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --icon=ICO.ico --name=AmpelClip Ampel6.py
```

## Konfiguration / Configuration

Einstellungen werden in `config.json` gespeichert (wird beim ersten Start automatisch erstellt).
Settings are saved in `config.json` (auto-generated on first run).

| Einstellung / Setting | Beschreibung / Description |
|----------------------|---------------------------|
| `builtin_patterns` | Regex-Patterns aktivieren/deaktivieren / Enable/disable pattern types |
| `ampel_status` | Aktueller Ampel-Status / Current traffic light state |
| `case_sensitive` | Gross-/Kleinschreibung beachten / Case-sensitive matching |
| `whole_words` | Nur ganze Woerter / Whole-word matching only |
| `files` | Importierte Listendateien / Previously imported list files |

## So funktioniert es / How it works

1. Ampel auf gewuenschten Modus setzen (Rot/Gelb/Gruen)
2. Sensible Begriffe importieren oder eingebaute Patterns aktivieren
3. AmpelClip ueberwacht die Zwischenablage in Echtzeit
4. **Rot** -- Keine Aktion, nur Anzeige
5. **Gelb** -- Vorschau, zeigt was anonymisiert wuerde
6. **Gruen** -- Ersetzt sensible Daten automatisch durch `[ANONYM]`

## Lizenz / License

GPL-3.0 -- siehe [LICENSE](LICENSE)

## Autor / Author

Lukas Geiger ([@lukisch](https://github.com/lukisch))
