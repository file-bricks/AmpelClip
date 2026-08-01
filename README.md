<img src="assets/banner.svg" width="100%" alt="AmpelClip Banner">

# AmpelClip

**[English](README.md)** | [Deutsch](README_de.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Platform: Windows](https://img.shields.io/badge/platform-Windows-lightgrey.svg)]()
[![Offline-first](https://img.shields.io/badge/offline--first-yes-brightgreen.svg)]()

> Local-first clipboard privacy guard — traffic-light workflow to detect and anonymize sensitive text before you paste it.

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

Source runs save settings in the project-local `config.json`, which is created on first start.
Frozen Store/EXE builds use `%LOCALAPPDATA%\AmpelClip\config.json`.

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

## Windows Store Readiness

Store metadata, listing text, privacy/support pages and the conservative preflight live in:

- `store_package.json`
- `STORE_LISTING.md`
- `PRIVACY_POLICY.md`
- `SUPPORT.md`
- `releases/windowsstore/WINDOWS_STORE_PREP.md`

Run the preflight with:

```bash
python scripts/check_store_readiness.py --allow-blockers
```

The current Store gate is prepared but still blocked by external items: Partner Center publisher DN, a fresh MSIX build and a WACK XML report.

## Search Context

AmpelClip is part of the `file-bricks` local-first desktop tools family. It is closest to a clipboard redaction helper, not to a full DLP gateway, password manager, cloud content scanner or browser extension. Useful search phrases:

- `AmpelClip clipboard privacy monitor`
- `file-bricks AmpelClip`
- `local-first clipboard privacy tool`
- `Windows clipboard anonymization helper`
- `local clipboard anonymization PySide6`
- `Windows clipboard redaction helper`
- `privacy traffic light clipboard tool`
- `clipboard PII redaction desktop app`

## German README

A full German README is available in [README_de.md](README_de.md).

## License

MIT, see [LICENSE](LICENSE).

This project is an unpaid open-source donation. Liability is limited to intent and gross negligence (§ 521 German Civil Code). Use at your own risk. No warranty, maintenance guarantee or fitness-for-purpose is assumed.
