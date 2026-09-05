# AmpelClip Web-Companion

Stand: 2026-09-05

Der Web-Companion ist als lokale Progressive Web App implementiert. Er ergänzt die Windows-App
um manuelle Browser-Workflows und ersetzt nicht deren automatische Zwischenablage-Überwachung.

## Implementierter Umfang

- `ampelclip-profile-v1.json` lokal importieren, normalisieren und wieder exportieren
- Sensibel-Liste, Whitelist, eingebaute Regex-Schalter und Ampel-Modus bearbeiten
- Beispieltexte lokal im Browser anonymisieren und das Ergebnis bewusst kopieren
- Profilzustand lokal im Browser speichern; Fehler von `localStorage` werden abgefangen
- Service Worker, Web-App-Manifest, Installationshinweis und PNG-/Maskable-/Apple-Touch-Icons
- Offline-Fallback sowie abgesicherter Profil-Download für Chromium, Firefox und Safari

Die Engine und die PWA-Dateiverträge werden automatisiert geprüft:

```bash
cd web_companion
npm test
```

Der Befehl benötigt keine npm-Pakete und führt die Node-Testdateien aus `tests/` aus. Er prüft
Logik und Dateiverträge, aber kein sichtbares Browser-Rendering und keine Geräteinstallation.

Für einen lokalen manuellen Browser-Smoke kann der Ordner über HTTP ausgeliefert werden:

```bash
cd web_companion
python -m http.server 8080
```

Danach ist die Anwendung unter `http://127.0.0.1:8080/` erreichbar. Ein solcher manueller Lauf ist
nur dann ein Nachweis, wenn Browser-/Geräteversion, geprüfte Schritte und Ergebnis protokolliert
werden; der Serverstart allein ist keine Browser-Abnahme.

## Grenzen und offene Gates

- Kein dauerhafter oder systemweiter Clipboard-Monitor im Browser oder auf Mobilgeräten
- Keine Cloud-Synchronisation sensibler Regeln und kein Upload von Beispieltexten
- Keine Übernahme oder Speicherung der Desktop-Clipboard-Historie im Profilformat
- Reale Chromium-/Firefox-/Safari-, Android- und iOS-Abnahmen stehen als TASKPLAN #31 aus
- Die derzeit uncommitteten PWA-Icon-/Manifeständerungen sind ein fremder Dirty Slice und bleiben
  bis zur Eigentümerentscheidung in TASKPLAN #28 unbestätigt

Der aktuelle `npm test`-Lauf ist grün. Daraus folgt weder eine veröffentlichte Web-App noch eine
bestätigte Offline-Installation auf einem realen Browser oder Mobilgerät.
