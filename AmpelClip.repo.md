# AmpelClip — Plan-D-Repository-Pointer (v2, host-fähig)

- GitHub: https://github.com/file-bricks/AmpelClip
- Kanonischer Branch: `master`
- Konvention: Plan D — dieser OneDrive-Ordner ist Daten-/Deploykopie, kein Git-Arbeitsbaum mehr

## Host-Tabelle

| Host | Lokaler Checkout | Verifizierter Stand | Datum |
|---|---|---|---|
| LAPTOP (ASUS-GEI) | `C:\_Local_DEV\repos\AmpelClip` | `51156b0` | 2026-08-01 |

**Regel:** Fehlt dein Host in der Tabelle → frisch von GitHub klonen (Standardpfad `C:\_Local_DEV\repos\AmpelClip`) und eigene Zeile ergänzen. GitHub ist die Synchronisationsquelle; Host-Zeilen anderer Systeme nie löschen.

## Was dieser OneDrive-Ordner ist

Keine lebende `.git` mehr (entfernt 2026-08-01). Der Dateistand entspricht **exakt** dem GitHub-Ref

    onedrive-worktree/2026-08-01 @ 85724e7 (aufgesetzt auf bugsweep/2026-06-23-desktop)

Das ist bewusst **nicht** `master`: Der Ordner trägt den Stand, mit dem hier zuletzt gearbeitet wurde, und genau den starten die `.bat`/`.exe` hier. Dieser Stand liegt vollständig auf GitHub — er wurde vor der Entkernung dorthin gesichert. Wer den kanonischen Stand braucht, nimmt den Klon.

> **Nicht gemergt:** Der oben genannte Ref wurde absichtlich **nicht** nach `master` gemergt. Ob und wie die Arbeit integriert wird, entscheidet der Eigner.

## Nur hier, nicht im Repo — bei `/MIR` verloren

| Was | Warum es nur hier liegt |
|---|---|
| `releases/` | fertige Binaries, gehören nicht ins Repo |
| `AUFGABEN.txt` | Planung/Steuerung lebt in OneDrive (Plan D §11), gitignored |
| `STORE_LISTING.md`, `PRIVACY_POLICY.md`, `SUPPORT.md`, `MACOS_LINUX_SOURCE_SMOKE.md` | untrackte Store-/Doku-Entwürfe |
| `*.ico`/`*.png`, `assets/`, `mobile_icons/` | generierte Icon-Sätze |
| `*-WORKSTATION-LG.*` | Konfliktkopien des anderen Hosts — Eigner-Entscheidung, nicht angetastet |

Insgesamt 81 untrackte Dateien; vollständige Liste in `AmpelClip_untracked.txt` im Backup.

## Nachziehen aus dem Klon — mit `/E`, NICHT `/MIR`

```
robocopy "C:\_Local_DEV\repos\AmpelClip" "<dieser Ordner>" /E ^
  /XD .git __pycache__ .venv node_modules /XF LOCK.txt LOCK.*.txt
```

⚠ **`/MIR` würde die oben aufgeführten Dateien löschen.** Und ein Nachziehen aus dem Klon überschreibt den hier liegenden Arbeitsstand mit dem kanonischen Branch — vorher prüfen, ob das gewollt ist.

## Migrations-Beleg (2026-08-01, Welle 3)

- Gate vor jedem Eingriff grün: `17 passed` (pytest) · Push-Probe `Everything up-to-date`.
- Ungepushte Arbeit vorher gesichert; nach der Sicherung galt: 0 Commits ausserhalb von origin, 0 offene getrackte Änderungen.
- Historien-Backup: `OneDrive\.BACKUP\repos\welle3\AmpelClip.bundle` (alle Refs) plus `AmpelClip_state.txt` und `AmpelClip_untracked.txt`.
- Entkernt: `.git` samt Index-Konfliktkopien entfernt; Zahl der Nutzdateien vor/nach identisch.

