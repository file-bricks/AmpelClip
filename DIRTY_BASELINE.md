# AmpelClip – Bugsweep-Branch und OneDrive-Dirty-Baseline

Stand: 2026-07-22. Der kontrollierte Plan-D-Clone ist ein sauberer Checkout von
`origin/bugsweep/2026-06-23-desktop` auf `f18d003`; `origin/master` steht auf
`02bad18`. Damit ist der Bugsweep-Branch fünf Commits vor `master`.

## Integrationsentscheidung

Jede in diesem OneDrive-Arbeitsbaum vorgefundene Datei steht auf **Besitzer
unbekannt, separat klären, behalten**. Ohne Eigentümer- und Merge-Freigabe wird
keine Datei übernommen, committet, archiviert, gelöscht, zurückgesetzt oder
gepusht. Details einschließlich aller 29 Pfade, Status, Hash-Kurzwerte,
Artefaktbefunde und Aufnahmeentscheidung sind im gleichnamigen
`DIRTY_BASELINE.md` des Plan-D-Clone dokumentiert.

Besonders geschützt bleiben der fünf Commits vor `master` liegende
`bugsweep/2026-06-23-desktop`-Branch, der Store-/Source-Smoke-Slice vom
2026-07-01 bis 2026-07-03 sowie der Icon-Slice vom 2026-07-16. Diese Zeitstempel
belegen keine Autorenschaft und erlauben keine Integration.
