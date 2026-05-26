# Portierungsplan AmpelClip

Stand: 2026-05-26

## Ausgangslage

AmpelClip ist eine lokale PySide6-Desktop-App zur Überwachung und Anonymisierung der Zwischenablage. Der Kernnutzen liegt auf dem Desktop, weil Clipboard-Zugriff, Tray-Status und automatische Ersetzung auf Windows am zuverlässigsten kontrollierbar sind. Die vorhandene MIT-Lizenz, PySide6-Basis, `START.bat`, `build_exe.bat`, `AmpelTool_V6.spec` und die aktive EXE machen den Windows-Store-Pfad grundsätzlich realistisch.

Es gab bisher keinen eigenständigen Plan für Portierung oder plattformübergreifende Nutzung. Dieser Plan ergänzt daher die bestehende Windows-Store-Pipeline und grenzt mobile/webbasierte Varianten bewusst vom Desktop-Kern ab.

## Zielbild

AmpelClip bleibt zuerst eine lokale Desktop-Schutzschicht für Windows. Plattformübergreifend sinnvoll ist nicht ein direkter Clone der Clipboard-Überwachung, sondern ein gemeinsames Regel- und Profilformat, damit sensible Begriffe, Whitelist, Regex-Aktivierung und Ampel-Modus zwischen Desktop und späterem Web/PWA-Companion transportiert werden können.

## Plattformbewertung

| Plattform | Entscheidung | Begründung |
|---|---|---|
| Windows Store | P0, erster Release-Kanal | Höchste Passung: Clipboard, Tray, lokale Datenschutzfunktion und vorhandener PySide6-/PyInstaller-Stand. |
| Webapp / PWA | P1 als Companion | Sinnvoll für Regelpflege, Profilprüfung und manuelle Textanonymisierung im Browser; kein automatischer System-Clipboard-Monitor. |
| Android | P2 über PWA/Trusted-Web-Activity | Native Clipboard-Überwachung ist durch Android-Rechte und Hintergrundlimits eingeschränkt; sinnvoll bleibt Profilpflege und manueller Textcheck. |
| iOS | P2 über PWA | iOS erlaubt keine dauerhafte systemweite Clipboard-Überwachung; Fokus auf manuelle Anonymisierung und Profilimport. |
| macOS App | P3 Source-Smoke | PySide6 ist möglich, aber globaler Clipboard-/Tray-Flow und Packaging brauchen gesonderte Prüfung. |
| Linux App | P3 Source-Smoke | PySide6 ist möglich; Clipboard-Verhalten unterscheidet sich je nach X11/Wayland und Desktop-Umgebung. |

## Empfohlene Architektur

1. Desktop bleibt autoritative Vollversion für automatische Clipboard-Überwachung.
2. `ampelclip-profile-v1.json` wird das stabile Austauschformat für Regeln und Einstellungen.
3. Web/PWA-Companion kann später lokale Profile laden, bearbeiten und Beispieltexte manuell anonymisieren.
4. Android/iOS nutzen dieselbe Web/PWA-Linie statt eigener nativer Clipboard-Apps.
5. macOS/Linux werden nur als PySide6-Smoke-Ziele geführt, bis der Windows-Store-Pfad stabil ist.

## Reihenfolge

| Priorität | Schritt | Ergebnis |
|---|---|---|
| P0 | Windows-Store-Basis finalisieren | Store-Listing, Screenshots, MSIX/WACK, Privacy-/Support-URL. |
| P0 | Profilformat implementieren | Export/Import von Regeln und Einstellungen ohne Clipboard-Historie. |
| P1 | Web-Companion planen und prototypisch prüfen | Browserbasierter Profil-Editor und manueller Anonymisierungscheck. |
| P2 | Android/iOS als PWA-Smoke testen | Installierbarkeit, Dateiaustausch und manuelle Nutzung prüfen. |
| P3 | macOS/Linux Source-Smokes | Start, Tray, Clipboard und Konfiguration dokumentiert testen. |

## Nicht-Ziele

- Keine native Mobile-App mit dauerhafter System-Clipboard-Überwachung als erster Schritt.
- Keine Synchronisation sensibler Profile über fremde Cloud-Dienste.
- Keine Übernahme der lokalen Clipboard-Historie in Exporte.
- Keine Zusammenlegung von Desktop und Web in eine große einheitliche Codebasis, solange der Desktop-Clipboard-Kern dadurch komplizierter würde.

## Status

- Plan erstellt: 2026-05-26
- Austauschformat skizziert: `EXPORTFORMAT.md`
- Web/PWA-Companion-Struktur angelegt: `web_companion/README.md`
- Umsetzung offen: siehe `AUFGABEN.txt`
