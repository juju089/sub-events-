# Prüfbericht · Sub e. V. München · 5. November 2026

## Ergebnis und Originalquelle

Echter HTTPS-Abruf der öffentlichen REST-Schnittstelle des offiziellen Kalenders unter `https://kalender.subonline.org/wp-json/tribe/events/v1/events` erfolgreich. Die öffentlichen Kategorien „Events im Zentrum“ und „Mittendrin“ wurden vollständig über **vier Seiten** abgefragt. Nach Prüfung und Begrenzung auf die nächsten 180 Tage enthält das Paket **187 Termine**: 181 „Im Zentrum“, sechs „Mittendrin“, darunter insgesamt ein Ganztagstermin. Die aktuell veröffentlichten Termine reichen vom 5. November 2026 bis zum 3. Februar 2027. Noch nicht veröffentlichte Termine werden nicht erfunden.

Quellen: [offizielle Website](https://subonline.org/), [offizieller Kalender](https://kalender.subonline.org/events-im-zentrum/). Ein Datenschnappschuss der vier Originalantworten ist enthalten. Der genaue Abrufzeitpunkt steht in `site/data/events.json` und `site/data/status.json`.

## Quellenspezifische Beobachtungen und Umsetzung

- Die API liefert höchstens 50 Datensätze pro Seite, auch wenn mehr angefragt werden. Ein Abruf nur der ersten Seite würde Termine verlieren.
- In den gelieferten Folgeseiten-URLs fehlt derzeit der Kategorienfilter. Das Skript erzeugt deshalb für jede Seite eine eigene URL mit unverändertem Kategorien- und Datumsfilter; es folgt dem fehlerhaften Link nicht.
- Abfragegrenzen werden von der Quelle zeitlich verschoben. Das Skript fragt mit einem Tag Puffer vor und nach dem Zielzeitraum ab und begrenzt anschließend anhand des tatsächlichen lokalen Terminbeginns.
- Beginn und Ende sind vorhanden. Lokale Zeiten müssen mit den UTC-Angaben unter `Europe/Berlin` übereinstimmen. Widersprüche führen zum Abbruch.
- Der Ganztagstermin „Christkindlmarkt“ wurde zusätzlich gegen den offiziellen Einzel-ICS-Export geprüft. Dieser nennt `DTSTART:20261213` und das exklusive `DTEND:20261215`. Das Paket übernimmt genau diesen veröffentlichten Zeitraum (13.–14. Dezember), statt ihn anhand des Titels auf einen Tag zu kürzen. Der Originalexport ist als Testdatei enthalten.
- Veranstaltungsorte unterscheiden sich: Unter anderem ist Café Glück als externer Mittendrin-Treffpunkt enthalten. Bei 173 der 187 Termine fehlt in der Schnittstelle ein separates Ortsfeld; dort verweist die App auf den Originaltermin. Sie erfindet keine Straßenadresse.
- Dienstplan-Kategorien werden nicht in App und Abo übernommen.

## Ausgeführte Prüfungen

**11 Python-Tests bestanden:**

1. Echter fester Datenbestand: 187 eindeutige Termine, sechs Mittendrin-Termine, ein Ganztagstermin, Titel mit HTML-Entities, Anfang/Ende und unterschiedliche Orte.
2. Vier Seiten mit erhaltenen Kategorie-, Datums- und Seitennummernparametern.
3. Abbruch bei Ausfall einer Folgeseite und bei während des Abrufs veränderter Gesamtzahl.
4. Fehlende Seiten, doppelte IDs, ungültige Datumswerte, Endzeit vor Beginn, UTC-Widerspruch, fremde Zeitzone und unsicherer Quellenlink werden zurückgewiesen.
5. Dienstplan-Einträge werden ausgefiltert; HTML-Beschreibungen werden in reinen Text umgewandelt.
6. Gesamt-ICS: IDs, UTC-Zeiten, Endzeiten, Ganztags-Datumsfelder, CRLF, Escaping und Faltung auf höchstens 75 UTF-8-Bytes.
7. Veraltete/leere kommende Daten und auffällig großer Datenverlust werden abgewiesen.
8. Drei Netzwerkversuche mit Zeitlimits.
9. Timeout, ungültige Daten und fehlende Folgeseiten lassen einen vorhandenen JSON- und ICS-Bestand **Byte für Byte unverändert**. Der Fehlerstatus wird gesetzt; ein erfolgreicher Folgeabruf hebt ihn auf.
10. Ohne vorhandenen Bestand führt ein Abruffehler zum Abbruch.
11. Schreibfehler bleiben auch bei aktiviertem Ersatzbetrieb fatal und verhindern die weitere Workflow-Veröffentlichung.

**7 Node-Tests bestanden:** App-Integration mit Datenabruf, Anzeige, Suche, Kategorieauswahl und Zurücksetzen; Offline-Ansicht mit gespeichertem Bestand; Umgang mit gesperrtem Browser-Speicher; sichtbare Abrufwarnung; Such- und Zeitfilter; Berliner Datum unabhängig von der Gerätezeitzone; Einzel-ICS mit UTC, realer Endzeit und Ganztagsfeldern; Manifest und vorhandene Dateien; Service-Worker-Cache und Offline-Fallback im Testmodell; ICS-Abrufe werden vom Service Worker nicht verdeckt zwischengespeichert.

**Zusätzliche Prüfungen:**

- JavaScript-Syntax für `app.js`, `calendar.js` und `sw.js` geprüft.
- Unabhängiger Parser `icalendar` 7.3.0 liest 187 VEVENTs mit eindeutigen IDs ohne gemeldete VEVENT-Fehler; 186 Uhrzeittermine und ein Ganztagstermin. Einzel-ICS-Dateien für Uhrzeit- und Ganztagstermin ebenfalls unabhängig gelesen.
- Workflow mit PyYAML 6.0.3 unabhängig eingelesen: täglicher Zeitplan 05:37 UTC, Build-/Deploy-Abhängigkeit, Veröffentlichungsordner und nötige Pages-Rechte geprüft.
- PNG-Icons geöffnet und ihre Größen kontrolliert.
- Fertiges ZIP auf CRC und vollständige Pfade geprüft, einschließlich `.github/workflows/update-and-deploy.yml`. Anschließend neu entpackt und die Python-/Node-Tests daraus wiederholt.

## Grenzen

Kein neues GitHub-Repository wurde angelegt, nichts hochgeladen und kein echter GitHub-Actions-/Pages-Lauf ausgeführt. Die Anleitung enthält diese Einrichtung und die Erfolgskontrolle nach dem Upload. Als neuer Repository-Name ist `sub-events` unter dem bisherigen GitHub-Konto `juju089` vorgesehen.

Eine visuelle Browserprüfung sowie echte Installation/Offline-Prüfung auf iPhone oder Android wurden nicht durchgeführt. Die lokale Browservorschau war in dieser Arbeitsumgebung zuvor nicht zuverlässig erreichbar; die automatisierten App- und Service-Worker-Prüfungen verwenden Testmodelle und ersetzen keinen echten Gerätetest. Es werden keine erfolgreich geprüften Screenshots oder Kalenderabos auf Benutzerkonten behauptet.

Die fremde Schnittstelle kann sich ändern, unvollständige oder falsche Inhalte veröffentlichen. Die Schutzprüfungen erkennen nicht jede mögliche inhaltliche Abweichung. Kalender-Apps bestimmen selbst, wann sie Abos neu laden; GitHub-Zeitpläne können sich verzögern. Der Kalender enthält ein rollierendes Zukunftsfenster, keine dauerhafte Historie. Angaben zu Zielgruppe, Anmeldung und Treffpunkt sind beim Originaltermin zu prüfen.

## Prüfungen wiederholen

Im entpackten Projektordner, mit Python 3.12+ und Node.js 24:

```text
python -m unittest discover -s tests -v
node --test tests/*.test.cjs
node --check site/app.js
node --check site/calendar.js
node --check site/sw.js
python scripts/update_events.py
```

Keine zusätzlichen Python-/npm-Pakete für die Tests oder den Betrieb nötig; bei lokalen Python-Läufen unter Windows können separat installierte `tzdata`-Daten erforderlich sein. Die unabhängigen Prüf-Bibliotheken wurden nur für die Paketkontrolle verwendet und sind nicht im ZIP enthalten.
