# Sichere Speicherung in AmpelClip

Konfiguration, JSON-Profile, Übersetzungskataloge und exportierte Textlisten werden zuerst in eine
exklusiv angelegte temporäre Datei im Zielordner geschrieben. Erst nach dem
vollständigen Schreiben und Schließen ersetzt diese Datei das gewählte Ziel.
Bei Serialisierungs-, Schreib- oder Veröffentlichungsfehlern bleibt die bisherige
Zieldatei erhalten. Die Fehlermeldung beim Profil-/Listenexport bleibt sichtbar;
Konfigurationsfehler werden weiterhin protokolliert.

Ein nicht lesbarer oder ungültiger Übersetzungskatalog wird nicht durch einen
leeren Katalog ersetzt. Der Übersetzungsscanner meldet den Fehler und liefert
`False`; beim CLI-Aufruf lautet der Exitcode `1`. Erfolgreiche Läufe liefern
`True` beziehungsweise Exitcode `0`.

Parallele Konfigurations-Saves verwenden unterschiedliche temporäre Dateien;
die Veröffentlichung wird innerhalb desselben Prozesses nacheinander ausgeführt.
Die zuletzt erfolgreich veröffentlichte Konfiguration gilt; es gibt keine
Zusammenführung konkurrierender Änderungen. Eine bereits vorhandene `config.tmp`
gehört diesem Schreibvorgang nicht und bleibt erhalten.

Beim Aufräumen wird nur die nachweislich eigene temporäre Datei entfernt.
Ein Fehler beim Aufräumen darf den ursprünglichen Speicherfehler nicht verdecken.
Kann die eigene Datei nicht entfernt werden, wird dies protokolliert; sie kann
Regellisten enthalten und sollte nach Beheben des Zugriffsproblems entfernt werden.

Diese Änderung schützt vor fehlgeschlagenen Schreibvorgängen. Sie garantiert
keine Speicherung bei Stromausfall oder erzwungenem Prozessabbruch. Bei einem
Abbruch können temporäre Dateien zurückbleiben. Gegen externe Änderungen zwischen
der letzten Dateiprüfung und dem Ersetzen besteht keine Sperrgarantie.

Der Profilinhalt bleibt auf Regeln und Einstellungen beschränkt; Clipboard-Verlauf
und Rohtexte werden weiterhin nicht exportiert. Dies ersetzt keine reale
Clipboard-, Browser-, Geräte- oder Windows-Store-Abnahme.
