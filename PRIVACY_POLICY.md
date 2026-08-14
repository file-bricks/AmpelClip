# AmpelClip Privacy Policy

## Deutsch

AmpelClip ist eine lokale Windows-Desktop-App. Die App sendet keine Zwischenablageinhalte, Sensibel-Listen, Whitelists, Profile oder Verlaufsdaten an Server des Projekts.

Verarbeitet werden lokal:

- aktueller Textinhalt der Windows-Zwischenablage,
- erkannte sensible Muster,
- importierte Sensibel- und Whitelist-Begriffe,
- lokale Einstellungen und Ampel-Modus,
- ein begrenzter lokaler Verlauf der letzten Zwischenablageeinträge.

Die App speichert Einstellungen lokal. Für Store-Builds ist `%LOCALAPPDATA%\AmpelClip\config.json` als Zielpfad vorgesehen; bestehende Quell-/Entwicklungsstände können weiterhin eine projektlokale `config.json` lesen. Profil-Exporte (`ampelclip-profile-v1.json`) enthalten nur Regeln und Einstellungen, keine Clipboard-Historie, keine Rohtexte und keine lokalen Dateipfade.

AmpelClip nutzt keine Telemetrie, kein Tracking und keinen Cloud-Sync. Wer Inhalte in andere Anwendungen einfügt, unterliegt anschließend den Datenschutzregeln dieser Zielanwendungen.

Support: siehe `SUPPORT.md`.

## English

AmpelClip is a local Windows desktop app. The app does not send clipboard content, sensitive lists, whitelists, profiles or history data to project servers.

Processed locally:

- current text content from the Windows clipboard,
- detected sensitive patterns,
- imported sensitive and whitelist terms,
- local settings and traffic-light mode,
- a limited local history of recent clipboard entries.

The app stores settings locally. Store builds are expected to use `%LOCALAPPDATA%\AmpelClip\config.json`; existing source/development builds may still read a project-local `config.json`. Profile exports (`ampelclip-profile-v1.json`) contain rules and settings only, not clipboard history, raw clipboard text or local file paths.

AmpelClip uses no telemetry, tracking or cloud sync. Content pasted into other applications is then governed by the privacy practices of those target applications.

Support: see `SUPPORT.md`.
