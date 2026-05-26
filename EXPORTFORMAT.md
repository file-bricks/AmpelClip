# Exportformat AmpelClip

Stand: 2026-05-26

## Zweck

`ampelclip-profile-v1.json` soll Regeln und App-Einstellungen zwischen Desktop-App und späterem Web/PWA-Companion austauschbar machen. Das Format transportiert keine Clipboard-Historie und keine automatisch überwachten Originaltexte.

## Datei

Empfohlener Dateiname:

```text
ampelclip-profile-v1.json
```

## Schema-Skizze

```json
{
  "schema_version": "ampelclip-profile-v1",
  "app": {
    "name": "AmpelClip",
    "exported_at": "2026-05-26T00:00:00+02:00"
  },
  "settings": {
    "ampel_status": "gelb",
    "case_sensitive": false,
    "whole_words": true
  },
  "builtin_patterns": {
    "iban": true,
    "email": true,
    "phone_de": false,
    "credit_card": false,
    "postal_code_de": false,
    "date_de": false
  },
  "lists": {
    "sensibel": ["Beispiel"],
    "whitelist": ["Freigabe"]
  }
}
```

## Stabilitätsregeln

- `schema_version` ist Pflicht und bleibt bei inkompatiblen Änderungen eindeutig versioniert.
- Importierende Clients müssen unbekannte Felder ignorieren.
- Exportierende Clients dürfen additive Metadaten ergänzen.
- Clipboard-Historie, Rohtexte und lokale Dateipfade werden nicht exportiert.
- Listenwerte werden als UTF-8 geschrieben und müssen echte deutsche Umlaute erhalten.

## Nächster Umsetzungsschritt

Die Desktop-App sollte eine Funktion `build_profile_export_payload()` erhalten, die dieses Profil ohne Seiteneffekte erzeugt. Darauf aufbauend können GUI-Export, GUI-Import und spätere Web/PWA-Nutzung getestet werden.
