# Microsoft Store Screenshots — AmpelClip

Offizielle Store-Screenshots im Standard-Format 1920x1080 (16:9), optimiert für das Windows Store Listing.

## Enthaltene Screenshots

1. **`01_ampelclip_listenverwaltung.png`**
   - **Ansicht:** Listenverwaltung
   - **Inhalt:** Import und Pflege sensibler Begriffe (Rot) und freigegebener Whitelist-Begriffe (Grün) via Text- und Excel-Dateien.

2. **`02_ampelclip_regex_patterns.png`**
   - **Ansicht:** Eingebaute Regex-Patterns
   - **Inhalt:** Automatische Erkennungsmuster für IBAN, E-Mail-Adressen, Telefonnummern, Kreditkarten, Postleitzahlen und Datum.

3. **`03_ampelclip_ampelsteuerung.png`**
   - **Ansicht:** Ampelsteuerung & Live-Vorschau
   - **Inhalt:** Umschaltung zwischen STOP (Rot), PREVIEW (Gelb) und ACTIVE (Grün) mit Side-by-Side Live-Vorschau von Original und Anonymisierung.

4. **`04_ampelclip_verlauf_anonymisierung.png`**
   - **Ansicht:** Verlauf & Wiederherstellung
   - **Inhalt:** Historie der erfassten Zwischenablage-Einträge mit Wiederherstellungsmöglichkeit für Original oder anonymisierten Text.

## Generierung

Die Screenshots können jederzeit reproduzierbar mit folgendem Befehl neu generiert werden:

```bash
python scripts/generate_store_screenshots.py
```
