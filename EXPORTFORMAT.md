# Exportformat AmpelClip

Stand: 2026-06-01

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
    "version": "6",
    "exported_at": "2026-06-01T08:30:00+00:00"
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
    "creditcard": false,
    "postcode_de": false,
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

## Implementierungsstand

Die Desktop-App erzeugt das Profil über `build_profile_export_payload()` ohne Seiteneffekte. Im Tab `Listenverwaltung` stehen `Profil exportieren` und `Profil importieren` bereit. Der Import akzeptiert zusätzlich die frühen Alias-Schlüssel `credit_card` und `postal_code_de`, normalisiert sie aber auf die aktuellen App-Schlüssel `creditcard` und `postcode_de`.

Regressionstests in `tests/test_profile_format.py` sichern ab, dass echte Umlaute erhalten bleiben und weder Clipboard-Historie noch lokale Dateipfade oder Rohtexte in das Profil gelangen.
