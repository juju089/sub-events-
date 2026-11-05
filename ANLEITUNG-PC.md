# Sub-App am PC einrichten

Du brauchst deinen GitHub-Login und einen PC-Browser. Ein eigenes öffentliches Repository **juju089/sub-events** legst du im ersten Schritt an. Für diesen Weg musst du nichts programmieren und keine Befehle eingeben. Das ZIP enthält alles, einschließlich der sonst leicht vergessenen GitHub-Automatik.

## 0. Neues Repository für das Sub anlegen

Dieses Paket ist für ein **eigenes** Repository namens **sub-events** vorbereitet. Dein bestehendes `substanz-events` bleibt ein separates Projekt. Es wurde noch kein neues Repository für dich angelegt.

1. Öffne https://github.com/new und melde dich mit **juju089** an.
2. Bei **Repository name** genau **sub-events** eintragen.
3. Sichtbarkeit **Public** wählen. Eine README kannst du aktivieren; sie wird gleich durch die Paket-README ersetzt. Keine zusätzliche Vorlage oder Automatik auswählen.
4. **Create repository** anklicken. Danach lautet die Adresse https://github.com/juju089/sub-events.
5. Falls du dieses Repository bereits angelegt hast, diesen Schritt überspringen.

Verwendest du einen anderen GitHub-Benutzernamen oder Repository-Namen, ändern sich die späteren App- und Abo-Adressen entsprechend. Die App berechnet die Abo-Adresse aus ihrer tatsächlichen Webadresse selbst.

## 1. ZIP vollständig entpacken

1. Lade `sub-events-komplett.zip` herunter.
2. Rechtsklick auf die ZIP-Datei → **Alle extrahieren** → **Extrahieren**.
3. Öffne den entpackten Ordner `sub-events`.
4. Du musst darin direkt die Ordner `site`, `scripts`, `tests`, `.github` und die Datei `README.md` sehen. Öffne nicht nur eine Ansicht innerhalb des ZIPs.

Der Punkt gehört zum Ordnernamen **.github**. Windows 11: Falls er nicht zu sehen ist, im Explorer **Anzeigen → Einblenden → Ausgeblendete Elemente**. Windows 10: **Ansicht → Ausgeblendete Elemente**. Unter `.github` befindet sich `workflows`, darin `update-and-deploy.yml`.

## 2. Programmdateien hochladen

1. Öffne https://github.com/juju089/sub-events und melde dich an.
2. Wähle oben den Reiter **Code**. Links über der Dateiliste muss **main** stehen.
3. Klicke auf **Add file → Upload files** (je nach Fensterbreite im Plus-Menü).
4. Ziehe aus dem Explorer die drei Ordner **site**, **scripts** und **tests** gemeinsam in die Upload-Fläche. Die Unterordner müssen erhalten bleiben. Über „choose your files“ lassen sich Ordner nicht in jedem Browser komfortabel auswählen; Ziehen ist hier einfacher.
5. Ziehe zusätzlich **README.md**, **ANLEITUNG-PC.md**, **ANLEITUNG-PC.html** und **PRUEFBERICHT.md** hinein. `.gitignore` kannst du ebenfalls mitnehmen, falls sichtbar; er ist für den Betrieb nicht zwingend.
6. Warte, bis alle Uploads fertig sind. Es sind deutlich weniger als 100 Dateien und jede ist kleiner als 25 MB.
7. Prüfe die Liste: Sie muss etwa `site/index.html`, `scripts/update_events.py`, `tests/test_update.py` enthalten. **Nicht** `sub-events/site/index.html` und **nicht** nur `index.html` ohne `site/`.
8. Als Commit-Nachricht z. B. **Sub-App hinzufügen** eingeben. Wähle **Commit directly to the main branch** und klicke **Commit changes**. Falls GitHub einen Dialog öffnet, dort bestätigen. Eine Rückfrage zum Ersetzen der bisherigen README ist erwartbar; die neue README gehört zum Paket.

**Nicht die ZIP-Datei selbst hochladen.** GitHub entpackt sie nicht als Website. Auch nicht nur den Inhalt von `site` hochladen: Der Workflow erwartet den Ordner `site`.

## 3. Den Workflow sicher hinzufügen – wichtig!

Wir legen diese eine Datei bewusst über GitHub an. So hängt die tägliche Automatik nicht davon ab, ob dein Browser den Punkt-Ordner beim Ziehen berücksichtigt hat.

1. Öffne im entpackten PC-Ordner `.github` → `workflows`.
2. Rechtsklick auf **update-and-deploy.yml** → **Öffnen mit → Editor** (Notepad). Nicht Word verwenden. Falls Windows nach einer App fragt, den Editor auswählen.
3. Im Editor **Strg+A**, dann **Strg+C**. Das kopiert den gesamten Dateiinhalt. Du musst nichts daran verändern.
4. Zurück bei GitHub im Repository unter **Code**: **Add file → Create new file**.
5. Bei **Name your file** genau diesen vollständigen Pfad eingeben:

```text
.github/workflows/update-and-deploy.yml
```

6. In das große Codefeld klicken und **Strg+V** drücken. Die erste Zeile muss `name: Termine aktualisieren und Pages veröffentlichen` sein. Den Inhalt nicht in den Dateinamen einfügen. Keine Markdown-Zeichen wie drei Backticks hinzufügen.
7. **Commit changes** anklicken, als Nachricht **Tägliche Aktualisierung und Pages einrichten**, direkt in **main** speichern.
8. Unter **Code** prüfen: `.github` → `workflows` → `update-and-deploy.yml` ist vorhanden. Die Datei darf **nicht** auf `.yml.txt` enden.

Falls du `.github` bereits mit hochgeladen hast und die Datei existiert: Öffne sie und prüfe den Inhalt. Nicht noch eine zweite Workflow-Datei anlegen. Bei Bedarf über das Stift-Symbol mit dem Inhalt aus dem ZIP ersetzen.

**Achtung:** Dieser Commit startet bereits einen Lauf. Solange Pages noch nicht aktiviert ist, darf dessen Veröffentlichung fehlschlagen. Das wird mit dem nächsten Schritt und einem neuen manuellen Lauf behoben.

## 4. GitHub Pages aktivieren

1. Oben im Repository **Settings** öffnen.
2. Links auf **Pages** klicken (unter „Code and automation“).
3. Im Abschnitt **Build and deployment** bei **Source** die Option **GitHub Actions** wählen. Falls ein Speichern-Button angezeigt wird, speichern.
4. Nicht „Deploy from a branch“ wählen. Keine zusätzliche vorgeschlagene Pages-Workflow-Datei erstellen – der passende Workflow ist bereits im Paket.

Der mitgelieferte Workflow beantragt die nötigen Rechte selbst. Eigene Tokens, Secrets und ein kostenpflichtiges Konto sind für dieses öffentliche Repository nicht erforderlich. Nur falls eine Fehlermeldung Bot-Commits ausdrücklich verbietet: **Settings → Actions → General → Workflow permissions** prüfen und **Read and write permissions** erlauben, sofern dein Konto diese Einstellung ändern darf. Bei Branchschutz müssen Bot-Commits auf `main` möglich sein.

## 5. Ersten vollständigen Lauf starten

1. Im Repository auf **Actions** klicken.
2. Falls GitHub die Workflows zunächst sperrt, für dein eigenes Repository aktivieren.
3. Links **Termine aktualisieren und Pages veröffentlichen** wählen.
4. Rechts **Run workflow** → Branch **main** → grüner Button **Run workflow**.
5. Den neuen Lauf öffnen. Warte einige Minuten. Die Jobs **build** und **deploy** müssen grüne Haken zeigen.
6. In der Laufzusammenfassung muss **Abruf erfolgreich** stehen. Ein grüner Lauf mit „Abruf fehlgeschlagen“ bedeutet: Das alte Programm wurde absichtlich erhalten und veröffentlicht; die Abrufwarnung muss noch geprüft werden.

Bei einem roten Lauf den fehlgeschlagenen Schritt aufklappen. Unten in dieser Anleitung findest du die häufigsten Ursachen. Nach einer Korrektur wieder einen neuen manuellen Lauf auf `main` starten.

## 6. App und Kalender ausprobieren

App nach erfolgreicher Veröffentlichung öffnen:

https://juju089.github.io/sub-events/

1. „Datenstand“ prüfen. Die mitgelieferten Ausgangsdaten stammen vom 5. November 2026; nach einem erfolgreichen Abruf erscheint das neue Abrufdatum.
2. Ein Suchwort wie **Schach** eingeben, Kategorien und Zeitraum ausprobieren.
3. **Filter zurücksetzen** anklicken. Ein leerer Filtertreffer ist kein technischer Fehler.
4. Bei einem Termin **Termin speichern** wählen: Eine einzelne ICS-Datei wird heruntergeladen. Das ist eine Momentaufnahme.
5. Für alle künftigen Aktualisierungen unten **Kalender abonnieren** verwenden oder die HTTPS-Abo-Adresse kopieren:

```text
https://juju089.github.io/sub-events/events.ics
```

Bitte erst abonnieren, wenn die App veröffentlicht ist. Die Adresse ist vorher noch nicht verfügbar. **ICS herunterladen** ist ein einmaliger Import und kein Abo. Nicht dasselbe Programm zusätzlich immer wieder importieren, sonst können doppelte Einträge entstehen.

## 7. iPhone / Android

**iPhone:** App-Adresse in Safari öffnen → Teilen → **Zum Home-Bildschirm**. Zum Kalenderabo in der App **Kalender abonnieren** antippen und bestätigen. Falls der direkte Link nicht öffnet: In Apple Kalender über **Kalender → Hinzufügen → Kalenderabonnement hinzufügen** die HTTPS-Adresse einsetzen. Menübezeichnungen können je nach iOS-Version abweichen.

**Android:** App-Adresse in Chrome öffnen → Browser-Menü → **App installieren** oder **Zum Startbildschirm**. Für Google Kalender am PC die Google-Kalender-Webseite öffnen → **Weitere Kalender + → Per URL** → HTTPS-Abo-Adresse einfügen. Der Kalender erscheint anschließend auf dem Handy, wenn dasselbe Konto verwendet wird und dieser Kalender eingeblendet ist.

**Outlook:** In Outlook im Web Kalender öffnen → **Kalender hinzufügen → Aus dem Internet abonnieren** und die HTTPS-Adresse einsetzen.

Die App lädt neue Daten beim Öffnen und über **Aktualisieren**. Offline zeigt sie zuletzt geladene Daten; für die erste Nutzung und für neue Daten wird Internet benötigt. Kalender-Apps bestimmen selbst ihr Aktualisierungsintervall. Änderungen können daher verspätet sichtbar werden.

## Welche Termine sind enthalten?

Die App übernimmt die öffentlichen Bereiche **Events im Zentrum** und **Mittendrin** des offiziellen Sub-Kalenders. Dienstpläne sind nicht enthalten. Der Abruf umfasst ein rollierendes Fenster der **nächsten 180 Tage**. Das bedeutet nicht, dass der Veranstalter schon für jeden dieser Tage Termine veröffentlicht hat. Wiederholungen werden nur übernommen, wenn sie als konkrete Termine in der Quelle stehen.

Treffpunkte können außerhalb des Sub liegen. Verbindliche Angaben zu Ort, Zugänglichkeit, Zielgruppe und Anmeldung stehen unter **Originaltermin**. Ein fehlendes Anmeldungsfeld bedeutet nicht automatisch, dass keine Anmeldung nötig ist. Die App meldet niemanden an und speichert keine persönlichen Teilnahmepläne.

## 8. Was passiert danach automatisch?

GitHub ruft täglich um **05:37 UTC** die offizielle Seite ab: 06:37 Uhr im Winter, 07:37 Uhr im Sommer in Deutschland. Der Lauf kann sich bei GitHub verzögern. Er prüft den Datenparser, speichert die Termine, erstellt die Kalenderdatei und veröffentlicht die App neu.

Bei Netzfehlern oder auffällig unvollständigen Daten bleiben die bisherigen Termine erhalten. Die App zeigt eine Warnung. Im Repository unter **Actions** steht die genaue Fehlermeldung. Du musst nicht jeden Tag selbst Dateien hochladen. Kontrolliere gelegentlich den Datenstand und die Actions-Ansicht. GitHub kann Zeitpläne in öffentlichen Repositories nach 60 Tagen ohne Aktivität deaktivieren; dann den Zeitplan wieder aktivieren oder einen manuellen Lauf anstoßen und die Actions-Anzeige prüfen.

## Wenn etwas nicht klappt

| Beobachtung | Lösung |
|---|---|
| Unter Actions ist kein Workflow sichtbar | Unter Code prüfen, ob `.github/workflows/update-and-deploy.yml` auf `main` liegt. Schritt 3 nachholen. Datei darf nicht `.txt` heißen. |
| „Run workflow“ fehlt | Den konkreten Workflow links auswählen; prüfen, ob die Datei auf `main` liegt und du mit dem Besitzerkonto angemeldet bist. |
| Fehler bei „Configure GitHub Pages“, „Get Pages site“ oder „Not Found“ | Settings → Pages → Source **GitHub Actions** einstellen, dann einen neuen Lauf starten. |
| Fehler bei `git push`, etwa 403 oder protected branch | Bot-Schreibrechte bzw. Branchschutz prüfen. Keine fremden Tokens eintragen. |
| Tests finden `site` oder `scripts` nicht | Ordner liegen eine Ebene zu tief oder wurden flach hochgeladen. Repository-Wurzel muss direkt `site`, `scripts`, `tests`, `.github` enthalten. |
| App zeigt 404 | Zuerst auf grünen deploy-Job warten. Die genaue App-Adresse mit `/sub-events/` verwenden. Keine eigene Zusatzdatei unter einem zusätzlichen Paketordner ablegen. |
| App ist leer, Datenstand fehlt | Prüfen, ob `site/data/events.json` und `site/data/status.json` vorhanden sind. Browser neu laden, Filter zurücksetzen und Internet prüfen. |
| Warnung „Abruf fehlgeschlagen“ | Alte Daten bleiben nutzbar. Unter Actions die Abrufwarnung lesen und später erneut starten. Bei geändertem Seitenaufbau Datenabruf anpassen lassen. |
| Beim Ort steht „siehe Originaltermin“ | Die Quelle enthält für diesen Termin keinen auswertbaren Ort. Über „Originaltermin“ Details und ggf. Anmeldung prüfen. |
| Termine erscheinen doppelt | Prüfen, ob derselbe Feed mehrfach abonniert oder zusätzlich als Datei importiert wurde. Nur ein Abo verwenden. |
| Nach dem Update noch alte Darstellung | Browser aktualisieren; falls nötig Website-Daten dieser App löschen und neu öffnen. Das entfernt nur den lokalen Zwischenspeicher. |

## Dateistruktur zum Vergleichen

```text
Repository-Wurzel (main)
├── .github/
│   └── workflows/
│       └── update-and-deploy.yml
├── site/
│   ├── index.html
│   ├── app.js, calendar.js, style.css, sw.js
│   ├── manifest.webmanifest
│   ├── events.ics
│   ├── data/
│   │   ├── events.json
│   │   └── status.json
│   └── icons/ (3 PNG-Dateien)
├── scripts/update_events.py
├── tests/ (Tests und fixtures/alle-events.html)
├── README.md
├── ANLEITUNG-PC.md
├── ANLEITUNG-PC.html
└── PRUEFBERICHT.md
```

Quelle des Programms: https://kalender.subonline.org/events-im-zentrum/. Die App ist unabhängig; verbindliche Angaben, Änderungen und Tickets bitte beim Veranstalter prüfen. Die Datenschnittstelle kann sich ändern und dann Wartung benötigen.
