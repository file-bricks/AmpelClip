# Security Policy

## Supported Versions

| Version | Supported | Security Maintenance |
|---|---|---|
| `1.2.x` | :white_check_mark: Yes | Current release, active security patches |
| `1.1.x` | :white_check_mark: Yes | Critical security updates only |
| `< 1.1.0` | :x: No | Please upgrade to the latest release |

## Reporting a Vulnerability

If you discover a potential security vulnerability in AmpelClip, please report it responsibly:

1. **Do NOT open a public issue** on GitHub.
2. **Use GitHub's [Private Vulnerability Reporting](../../security/advisories/new)** (preferred).
3. **Alternative Direct Email Contact**:
   - `security@open-bricks.org`
   - `security@file-bricks.org`
   - `lukas@open-bricks.org`

### Information to Include

Please provide:
- Detailed description of the vulnerability and attack vector
- Reproduction steps, sample clipboard content, or proof-of-concept scripts
- Affected version(s) and Windows environment (e.g. Windows 11 / Windows 10)
- Assessment of potential impact and proposed remediation (if available)

## Response Commitment & SLA

- **Initial Acknowledgment**: Within **48 hours** (`[INV-SLA-10]`).
- **Triage & Reproduction**: Within 5 business days.
- **Remediation & Coordinated Disclosure**: Security patches will be prioritized and published alongside a security advisory.

## Security Architecture & Invariants

AmpelClip enforces strict local execution boundaries:
- **`[INV-LOCAL-01]` Zero Egress**: All clipboard inspection and anonymization runs 100% locally in-process. No cloud network sockets, no remote telemetry.
- **`[INV-PERM-02]` Non-Elevated Execution**: Runs under standard user rights (`RunAsInvoker`). Does not require administrator privileges or kernel drivers.
- **`[INV-MEM-07]` Volatile In-Memory History**: Clipboard history is capped at 15 volatile entries and is never persisted to disk in unencrypted state.
- **`[INV-RULE-05]` Deterministic Whitelisting**: Whitelist entries take absolute precedence over built-in pattern substitution.
