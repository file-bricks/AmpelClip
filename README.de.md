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
|-------------|--------------|
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

## Lizenz

GPL-3.0 -- siehe [LICENSE](LICENSE)

## Autor

Lukas Geiger ([@lukisch](https://github.com/lukisch))

---

English version: [README.md](README.md)
