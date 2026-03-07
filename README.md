# AmpelClip

Privacy traffic light for clipboard monitoring. Detects sensitive data (IBAN, email, phone numbers, credit cards) in real-time and anonymizes clipboard content automatically.

## Features

- **Traffic Light System** -- Red (blocked) / Yellow (preview) / Green (auto-anonymization)
- **Built-in Regex Patterns** -- IBAN, email, phone (DE), credit cards, zip codes, dates
- **Custom Word Lists** -- Sensitive list and whitelist with import/export (TXT, Excel)
- **System Tray Integration** -- Colored icon shows current status
- **Clipboard History** -- Last 15 entries with restore and anonymized copy
- **Live Preview** -- Original vs. anonymized text side by side

## Requirements

- Python 3.10+
- Windows

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python Ampel6.py
```

Or via `START.bat`.

### Build Executable

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --icon=ICO.ico --name=AmpelClip Ampel6.py
```

## Configuration

Settings are saved in `config.json` (auto-generated on first run).

| Setting | Description |
|---------|-------------|
| `builtin_patterns` | Enable/disable pattern types |
| `ampel_status` | Current traffic light state |
| `case_sensitive` | Case-sensitive matching |
| `whole_words` | Whole-word matching only |
| `files` | Previously imported list files |

## How It Works

1. Set the traffic light to the desired mode (Red/Yellow/Green)
2. Import sensitive terms or enable built-in patterns
3. AmpelClip monitors the clipboard in real-time
4. **Red** -- No action, display only
5. **Yellow** -- Preview, shows what would be anonymized
6. **Green** -- Automatically replaces sensitive data with `[ANONYM]`

## License

GPL-3.0 -- see [LICENSE](LICENSE)

## Author

Lukas Geiger ([@lukisch](https://github.com/lukisch))

---

Deutsche Version: [README.de.md](README.de.md)
