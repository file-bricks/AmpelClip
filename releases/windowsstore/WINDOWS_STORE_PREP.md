# AmpelClip Windows Store Preparation

Stand: 2026-09-22

## Status: Materialien vorbereitet, Veröffentlichung blockiert

Der lokale Preflight bestätigt die vorhandenen Metadaten und Materialien. Er validiert das
MSIX-Paket tiefgreifend auf Format, Manifest, Executable, BlockMap und Kacheln. Er ist jedoch kein
Release-, Signatur-, WACK- oder Store-Akzeptanznachweis:

- Partner-Center Publisher-DN `CN=52596601-BAB4-4F3F-B182-E8F3F273B202` (Lukas Geiger) und Identität `Geiger.AmpelClip` gesetzt.
- `store_package.json` und `releases/windowsstore/store_settings.json` synchronisiert.
- `store_package/AmpelClip/AppxManifest.xml` erstellt und schema-konform validiert.
- Alle Microsoft Store Tile-Icons (44x44, 50x50, 150x150, 310x150, 310x310) maßhaltig generiert.
- 4 offizielle Store-Screenshots in nativer 1920x1080 Full-HD-Auflösung in `screenshots/store/` hinterlegt.
- `STORE_LISTING.md` zweisprachig (DE/EN) mit exakt 7 Suchbegriffen (Policy 10.1.3 konform, keine geschützten Drittmarken) aktualisiert.
- `PRIVACY_POLICY.md`, `SUPPORT.md`, `LICENSE`, `SECURITY.md`, `THIRD_PARTY_LICENSES.txt` vorhanden und validiert.
- MSIX-Paketinhalt wird durch `scripts/check_store_readiness.py` deterministisch auf ZIP-Integrität, Manifest-Übereinstimmung, `AmpelClip.exe`, Pflichtdateien, Kachel-Assets und optionale SHA256-Prüfsummen tiefenvalidiert (Task #29 erledigt).

Im aktuellen Dirty Worktree liegen zwei bytegleiche, unversionierte MSIX-Kopien mit demselben
SHA-256-Wert. Sie enthalten ein lesbares Paket, aber keine `AppxSignature.p7x`; der lokale
Signaturstatus lautet `NotSigned`. Eigentum, Provenienz und Freigabe dieses Dirty Slice sind noch
nicht entschieden. Die Dateien sind daher keine bestätigten Release-Kandidaten.

## Vorhandene Store-Artefakte

- `store_package.json` mit Store-Metadaten, `runFullTrust` und lokalen Datenschutz-Grenzen.
- `releases/windowsstore/store_settings.json` für MSIX-Erzeugung.
- `store_package/AmpelClip/AppxManifest.xml` als vollständiges AppxManifest.
- `store_package/AmpelClip/assets/` & `store_assets/` mit allen Store-Tile-Logos.
- `screenshots/store/` mit 4 hochauflösenden Store-Screenshots (1920x1080).
- `STORE_LISTING.md` mit optimierten Texten für das Microsoft Partner Center.
- `PRIVACY_POLICY.md` und `SUPPORT.md` mit Store-tauglichen Nutzertexten.
- `scripts/check_store_readiness.py` als konservativer lokaler Preflight mit tiefer MSIX-Prüfung (`--msix`, `--skip-msix`).
- `tests/test_store_materials.py` und `tests/test_store_readiness.py` als automatisierte Verträge (12 Store-Readiness-Tests).

## Offene externe Gates

- Eigentum und Verwendung des vorhandenen Dirty-MSIX-Slice ausdrücklich freigeben oder ablehnen (#28).
- WACK-XML-Report `releases/windowsstore/wack_YYYYMMDD_HHMMSS.xml` via Windows App Certification Kit generieren (#30).
- Einreichung im Microsoft Partner Center nur nach ausdrücklicher Autorisierung (#30).

## Preflight-Ausführung

```powershell
python scripts\check_store_readiness.py --allow-blockers
```

Mit `--allow-blockers` endet der aktuelle Lauf erfolgreich und dokumentiert die offenen Gates. Ohne
diese Option endet er derzeit mit Exitcode 2, weil der WACK-XML-Report fehlt.

## Nächste manuelle Schritte zur Veröffentlichung

Diese Schritte erfordern eine freigegebene Paketquelle und die jeweils nötige externe
Autorisierung. Der aktuelle Dirty Slice darf dafür nicht stillschweigend übernommen werden.

1. Freigegebene Release-EXE (`AmpelClip.exe`) mit `build_exe.bat` reproduzierbar bauen.
2. Ein freigegebenes MSIX reproduzierbar erzeugen und Hash, Inhalt sowie Signaturstatus prüfen.
3. WACK als Administrator gegen genau dieses MSIX ausführen:
   ```cmd
   appcert.exe test -appxpackagepath releases\windowsstore\AmpelClip.msix -reportoutputpath releases\windowsstore\wack_report.xml
   ```
4. `python scripts\check_store_readiness.py` ohne `--allow-blockers` ausführen (muss 0 zurückgeben).
5. Erst nach ausdrücklicher Freigabe im Microsoft Partner Center ein Paket hochladen und die
   Store-Listing-Texte aus `STORE_LISTING.md` übertragen.
