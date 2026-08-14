# AmpelClip Windows Store Preparation

Stand: 2026-08-14

## Status: Bereit für MSIX-Packaging

Der Windows-Store-Pfad für AmpelClip ist vollständig vorbereitet. Alle Vorab-Prüfungen (14/14 Checks) sind grün:
- Partner-Center Publisher-DN `CN=52596601-BAB4-4F3F-B182-E8F3F273B202` (Lukas Geiger) und Identität `Geiger.AmpelClip` gesetzt.
- `store_package.json` und `releases/windowsstore/store_settings.json` synchronisiert.
- `store_package/AmpelClip/AppxManifest.xml` erstellt und schema-konform validiert.
- Alle Microsoft Store Tile-Icons (44x44, 50x50, 150x150, 310x150, 310x310) maßhaltig generiert.
- 4 offizielle Store-Screenshots in nativer 1920x1080 Full-HD-Auflösung in `screenshots/store/` hinterlegt.
- `STORE_LISTING.md` zweisprachig (DE/EN) mit exakt 7 suchbegriffen (Policy 10.1.3 konform, keine geschützten Drittmarken) aktualisiert.
- `PRIVACY_POLICY.md`, `SUPPORT.md`, `LICENSE`, `SECURITY.md`, `THIRD_PARTY_LICENSES.txt` vorhanden und validiert.

## Vorhandene Store-Artefakte

- `store_package.json` mit Store-Metadaten, `runFullTrust` und lokalen Datenschutz-Grenzen.
- `releases/windowsstore/store_settings.json` für MSIX-Erzeugung.
- `store_package/AmpelClip/AppxManifest.xml` als vollständiges AppxManifest.
- `store_package/AmpelClip/assets/` & `store_assets/` mit allen Store-Tile-Logos.
- `screenshots/store/` mit 4 hochauflösenden Store-Screenshots (1920x1080).
- `STORE_LISTING.md` mit optimierten Texten für das Microsoft Partner Center.
- `PRIVACY_POLICY.md` und `SUPPORT.md` mit Store-tauglichen Nutzertexten.
- `scripts/check_store_readiness.py` als 14-Punkte Preflight-Audit.
- `tests/test_store_materials.py` und `tests/test_store_readiness.py` mit 100% Testabdeckung.

## Offene externe Gates

- MSIX-Artefakt `releases/windowsstore/AmpelClip.msix` via WinStorePackager / Windows SDK erzeugen.
- WACK-XML-Report `releases/windowsstore/wack_YYYYMMDD_HHMMSS.xml` via Windows App Certification Kit generieren.
- Einreichung im Microsoft Partner Center.

## Preflight-Ausführung

```powershell
python scripts\check_store_readiness.py --allow-blockers
```

## Nächste manuelle Schritte zur Veröffentlichung

1. Aktuelle Release-EXE (`AmpelClip.exe`) mit `build_exe.bat` bauen.
2. MSIX mit `makeappx pack /d store_package\AmpelClip /p releases\windowsstore\AmpelClip.msix` oder WinStorePackager erzeugen.
3. WACK als Administrator gegen `AmpelClip.msix` ausführen:
   ```cmd
   appcert.exe test -appxpackagepath releases\windowsstore\AmpelClip.msix -reportoutputpath releases\windowsstore\wack_report.xml
   ```
4. `python scripts\check_store_readiness.py` ohne `--allow-blockers` ausführen (muss 0 zurückgeben).
5. Im Microsoft Partner Center neues Paket hochladen und Store-Listing-Texte aus `STORE_LISTING.md` übertragen.
