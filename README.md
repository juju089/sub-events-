# Sub e. V. München · Veranstaltungen

Mobile PWA mit Suche, Filtern, Offline-Leseansicht, Einzeltermin-Download und abonnierbarem ICS-Kalender. Ein separates Projekt für das Sub e. V.; unabhängig vom zuvor erstellten Substanz-Paket.

**Loslegen: ZIP entpacken und `ANLEITUNG-PC.html` doppelt anklicken.** Die Anleitung führt ohne Programmierkenntnisse durch Repository-Erstellung, Datei-Upload, `.github/workflows`, Pages und Kalenderabo.

## Geplante GitHub-Adressen

Vorgesehen: neues öffentliches Repository **juju089/sub-events**, Branch **main**. Es wurde noch kein Repository angelegt und nichts hochgeladen.

- App nach Veröffentlichung: https://juju089.github.io/sub-events/
- Kalender-Abo: https://juju089.github.io/sub-events/events.ics
- Apple-Abo: webcal://juju089.github.io/sub-events/events.ics

Falls du einen anderen Namen verwendest, ändern sich die Adressen. Die App berechnet die Abo-Adresse selbst aus ihrer tatsächlichen URL; der eigentliche Datenabruf funktioniert unabhängig vom GitHub-Benutzernamen. Die User-Agent-Projektadresse im Abrufskript kannst du entsprechend anpassen.

## Quelle und Umfang

Offizieller Kalender: https://kalender.subonline.org/events-im-zentrum/. Verwendet wird dessen öffentliche **The Events Calendar REST API** unter `https://kalender.subonline.org/wp-json/tribe/events/v1/events`.

Enthalten sind die offiziellen Kategorien **Events im Zentrum** und **Mittendrin** (aktuell IDs 16 und 14). Die App übernimmt weder Theken-/Café-Dienstpläne noch Teilnehmerlisten. Suchbar sind Titel und Beschreibungen; die Kategorieauswahl entspricht den beiden offiziellen Veranstaltungsbereichen. Das Fenster umfasst die nächsten **180 Kalendertage**, ab heute in `Europe/Berlin`; es werden keine eigenen Wiederholungsregeln erfunden. Noch nicht veröffentlichte Termine können daher nicht erscheinen.

Der erste echte Datenbestand enthält **187 Termine**. Der genaue Abrufzeitpunkt und das Abfragefenster stehen in `site/data/events.json`. Im ersten Datenbestand sind Termine vom 5. November 2026 bis 3. Februar 2027 veröffentlicht, obwohl das Abfragefenster länger reicht.

Die Quelle liefert höchstens 50 Datensätze pro Seite und verliert derzeit den Kategorienfilter in `next_rest_url`. Deshalb erzeugt das Skript jede Seitenabfrage selbst, behält Filter und Zeitfenster bei und prüft Seitenzahl, Gesamtzahl, doppelte IDs und veränderte Gesamtzahlen während des Abrufs. Es lädt nicht bloß die erste Seite. Wegen einer beobachteten serverseitigen Zeitverschiebung bei den Abfragegrenzen lädt es mit einem zusätzlichen Tag Puffer auf jeder Seite und filtert anschließend nach dem tatsächlichen Berliner Terminstart.

## Zeiten, Orte und Anmeldung

Beginn **und Ende** stammen aus der Quelle. Lokale Berliner Zeiten werden gegen die mitgelieferten UTC-Zeiten geprüft. Der Gesamtfeed und Einzeltermine verwenden für Uhrzeittermine UTC und berücksichtigen dadurch Sommer-/Winterzeit ohne Abhängigkeit von der Gerätezeitzone. Ganztagstermine verwenden Datumswerte mit exklusivem Enddatum nach RFC 5545. IDs stammen aus den stabilen Quell-IDs; Titel- und Uhrzeitänderungen erzeugen keine neue Kalender-ID.

Beim enthaltenen Ganztagstermin „Christkindlmarkt“ umfasst auch der offizielle ICS-Export den 13. und 14. Dezember 2026 (exklusives Ende am 15.). Dieser Quellzeitraum wird unverändert übernommen; Details bitte beim Originaltermin prüfen.

Mittendrin findet teils außerhalb des Sub statt. Ein veröffentlichter Ort wird pro Termin übernommen. Bei fehlenden oder als gelöscht markierten Ortsangaben wird auf den Originaltermin verwiesen, statt eine Adresse zu erraten. Die Quelle enthält bei vielen Terminen kein separates Ortsfeld; eine Zuordnung zur Kategorie „Im Zentrum“ wird deshalb nicht stillschweigend zur vollständigen Straßenadresse erweitert.

Die App verlinkt immer auf den offiziellen Einzeltermin. Ein zusätzliches HTTPS-Websitefeld wird als „Information / Anmeldung“ verlinkt. Keine automatische Anmeldung oder Reservierung; fehlende Informationen bedeuten nicht, dass die Teilnahme ohne Anmeldung möglich ist.

## Sicherer Ersatzbetrieb

Netzwerkabrufe haben Zeitlimits und bis zu drei Versuche pro Seite. Fehlerhafte Antworten, fehlende Seiten, doppelte IDs, fehlende Pflichtfelder, widersprüchliche Uhrzeiten oder leere kommende Termine führen zum Abbruch des Datenupdates. Ein Rückgang um mehr als 50 % der weiterhin im Fenster liegenden Termine (bei mindestens sechs bisherigen Terminen) wird ebenfalls zurückgewiesen.

Bei solchen Abruf-/Parserfehlern bleiben `events.json` und `events.ics` unverändert. Nur `status.json` meldet den Fehler. Mit `--allow-stale` veröffentlicht der Workflow den letzten erfolgreichen Stand und eine sichtbare Warnung. Ohne vorhandenen Bestand oder bei Schreibfehlern bricht er vor Commit und Veröffentlichung ab. Ein grüner Workflow kann bewusst alte Daten veröffentlicht haben; die Laufzusammenfassung zeigt den Abrufstatus. Die App warnt außerdem bei über 48 Stunden altem Datenstand.

Nicht jede fehlerhafte oder unvollständige Antwort einer fremden Quelle ist automatisch erkennbar. Die Kategorien oder Schnittstelle können sich ändern; dann muss das Skript angepasst werden. Auch ein echter großer Rückgang des Programms kann eine manuelle Prüfung erfordern.

## Dateien

- `site/`: fertige PWA ohne Frontend-Build oder externe JavaScript-Abhängigkeiten.
- `scripts/update_events.py`: Datenabruf, Prüfung und ICS; Python-Standardbibliothek.
- `.github/workflows/update-and-deploy.yml`: Tests, Tagesabruf, Datensicherung und GitHub Pages.
- `tests/fixtures/api-pages.json`: vier vollständig abgerufene Original-API-Seiten für reproduzierbare Tests.
- `tests/fixtures/events.json`: fester normalisierter Testbestand.
- `ANLEITUNG-PC.html` und `.md`: Anfängeranleitung.
- `PRUEFBERICHT.md`: tatsächlich ausgeführte Prüfungen und Grenzen.

## Automatik und Pages

Täglich **05:37 UTC** (06:37 Uhr im deutschen Winter, 07:37 Uhr im Sommer), außerdem bei Push auf `main` und manuell. GitHub kann Zeitpläne verzögern und deaktiviert geplante Läufe in öffentlichen Repositories nach 60 Tagen ohne Aktivität. Der Workflow schreibt normalerweise täglich einen Daten-/Status-Commit; trotzdem gelegentlich Actions und Datenstand prüfen.

Pages muss unter **Settings → Pages → Source: GitHub Actions** aktiviert werden. Der mitgelieferte Workflow nutzt `contents: write` für Daten-Commits und `pages: write` / `id-token: write` für die Veröffentlichung. Keine eigenen Tokens oder Secrets nötig. Branchschutz kann Bot-Commits verhindern.

Die Veröffentlichung erfolgt im selben Workflow wie der Abruf. Es ist kein zweiter Workflow nötig, den ein Bot-Commit auslösen müsste. Nur der Inhalt von `site/` wird öffentlich als Website veröffentlicht, nicht das gesamte Repository als Pages-Artefakt.

## Lokal testen

Python 3.12+ mit Berlin-Zeitzonendaten und Node.js 24. Keine npm-Installation nötig. Unter Windows bei Bedarf einmal `py -m pip install tzdata` ausführen; auf GitHub Ubuntu sind Zeitzonendaten vorhanden.

```text
python -m unittest discover -s tests -v
node --test tests/*.test.cjs
node --check site/app.js
node --check site/calendar.js
node --check site/sw.js
python scripts/update_events.py
python -m http.server 8000 --directory site
```

Danach http://localhost:8000 öffnen. Gegebenenfalls `py` statt `python` verwenden. Die App nicht per Doppelklick auf `site/index.html` prüfen; Datei-URLs unterstützen Datenabruf und PWA nicht vollständig. Die HTML-Anleitung ist dagegen bewusst direkt im Browser lesbar.

Optional: `python scripts/update_events.py --days 180`. Das Abfragefenster ist auf 1 bis 366 Tage begrenzt. `--snapshot DATEIPFAD` speichert erfolgreiche Originalantworten für eigene Tests. Historische Testdaten werden in den automatisierten Tests mit festem Datum geprüft; dadurch laufen sie auch nach Ablauf der Termine weiter.

## Datenschutz und Hinweise

Keine Analysewerkzeuge, externen Schriftarten oder persönlichen Teilnahmeprofile. Im Browser werden öffentlich geladene Termine zwischengespeichert. Ein einmaliger ICS-Import ist kein Abo. Kalender-Apps bestimmen ihre Aktualisierungsintervalle selbst; Änderungen und entfernte Termine können verspätet sichtbar werden. Das rollierende Kalenderfenster enthält keine dauerhafte Veranstaltungshistorie.

Unabhängige Übersicht, keine offizielle App des Sub e. V. Veranstaltungsangaben und Inhalte bleiben Sache des Veranstalters; dessen Rechte bleiben unberührt. Das typografische Icon ist eine eigene Gestaltung, kein übernommenes Vereinslogo. Für einen eigenen öffentlichen Betrieb ggf. erforderliche eigene Betreiberinformationen ergänzen; der Link zum Sub-Impressum bezeichnet dessen Herausgeber.

Offizielle Quellen: [Sub](https://subonline.org/), [Kalender](https://kalender.subonline.org/events-im-zentrum/), [REST-API-Dokumentation des Kalenderherstellers](https://dev.theeventscalendar.com/knowledgebase/introduction-to-the-events-calendar-rest-api/), [GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages), [GitHub-Zeitpläne](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule).
