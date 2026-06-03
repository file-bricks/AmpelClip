# AmpelClip

AmpelClip is a local-first Windows clipboard privacy monitor. It watches clipboard text, detects sensitive patterns such as IBANs, email addresses, German phone numbers and credit-card-like numbers, and helps anonymize copied content before it is pasted elsewhere.

![AmpelClip main window](README/screenshots/main.png)

## Start Here

| Need | Use |
|---|---|
| Run the desktop tool | `python Ampel6.py` or `START.bat` |
| Configure detection | Enable built-in regex patterns and import sensitive/whitelist terms |
| Review before replacing | Use yellow preview mode |
| Auto-anonymize clipboard text | Use green mode after checking the rules |
| Understand limits | Read the manual-review warning below |

## Why AmpelClip

- **Traffic-light workflow**: red for monitor-only, yellow for preview, green for automatic replacement.
- **Clipboard-focused privacy support**: useful before pasting text into documents, tickets, chat tools, LLM prompts or web forms.
- **Built-in pattern detection**: IBAN, email, German phone numbers, credit-card-like numbers, postal codes and dates.
- **Custom lists**: import sensitive terms and whitelist terms from TXT or Excel files.
- **Local-first desktop app**: clipboard handling stays on the local Windows machine.
- **Tray integration and history**: colored tray icon plus the last 15 clipboard entries.

AmpelClip is not a DLP platform and does not guarantee complete redaction. It is a helper for privacy workflows, not a substitute for manual review.

## Install

Requirements:

- Python 3.10+
- Windows

```bash
git clone https://github.com/file-bricks/AmpelClip.git
cd AmpelClip
pip install -r requirements.txt
python Ampel6.py
```

You can also start the app with `START.bat`.

## How It Works

1. Choose red, yellow or green mode.
2. Enable built-in patterns and optionally import sensitive terms or whitelists.
3. Copy text as usual.
4. AmpelClip checks the clipboard content locally.
5. In yellow mode, review the original and anonymized preview.
6. In green mode, matching sensitive content is replaced with `[ANONYM]`.

## Configuration

Settings are saved in `config.json`, which is created on first start.

| Setting | Description |
|---|---|
| `builtin_patterns` | Enabled and disabled built-in pattern types |
| `ampel_status` | Current traffic-light mode |
| `case_sensitive` | Case-sensitive matching |
| `whole_words` | Whole-word matching only |
| `files` | Previously imported list files |

## Build Executable

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --icon=ICO.ico --name=AmpelClip Ampel6.py
```

## Search Context

AmpelClip is part of the `file-bricks` local-first desktop tools family. Useful search phrases:

- `AmpelClip clipboard privacy monitor`
- `file-bricks AmpelClip`
- `local clipboard anonymization PySide6`
- `Windows clipboard redaction helper`
- `privacy traffic light clipboard tool`

## Deutsch

AmpelClip ist ein lokales Windows-Tool zur Datenschutz-Unterstützung in der Zwischenablage. Es erkennt sensible Daten wie IBANs, E-Mail-Adressen, deutsche Telefonnummern und kreditkartenähnliche Zahlen in kopiertem Text und hilft, diese Inhalte vor dem Einfügen zu anonymisieren.

### Funktionen

- **Ampel-System**: Rot für reines Beobachten, Gelb für Vorschau, Grün für automatische Anonymisierung.
- **Eingebaute Regex-Patterns**: IBAN, E-Mail, Telefon (DE), Kreditkarten, PLZ und Datum.
- **Eigene Wortlisten**: Sensibel-Liste und Whitelist mit Import/Export für TXT und Excel.
- **System-Tray-Integration**: Farbiges Icon zeigt den aktuellen Status.
- **Clipboard-Verlauf**: Letzte 15 Einträge mit Wiederherstellen und anonymisiertem Kopieren.
- **Live-Vorschau**: Original und anonymisierter Text nebeneinander.

### Nutzung

```bash
git clone https://github.com/file-bricks/AmpelClip.git
cd AmpelClip
pip install -r requirements.txt
python Ampel6.py
```

Oder über `START.bat`.

### Wichtige Grenze

AmpelClip garantiert keine vollständige Schwärzung oder Anonymisierung. Das Werkzeug unterstützt Datenschutz-Prozesse, kann sie aber nicht vollständig automatisieren. Manuelle Nachkontrolle ist Pflicht.

## License

MIT, see [LICENSE](LICENSE).

This project is an unpaid open-source donation. Liability is limited to intent and gross negligence (§ 521 German Civil Code). Use at your own risk. No warranty, maintenance guarantee or fitness-for-purpose is assumed.
