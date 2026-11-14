# Natur – Einrichtung von Grund auf

**Stand: 14. November 2026.** Diese ZIP-Datei ist ein lokales Projekt, **keine bereits veröffentlichte App**. Voraussetzung: kostenloses GitHub-Konto und Firebase-/Google-Konto. Keine Anmeldung für spätere Einkaufslisten-Mitglieder.

## 1. Neues Firebase-Projekt

1. Auf https://console.firebase.google.com/ **Projekt hinzufügen** → z. B. `natur-einkauf-2026` → fortfahren. Analytics ist nicht erforderlich.
2. In der Projektübersicht **Web-App hinzufügen** (Symbol `</>`) → App-Namen `Natur Web` → registrieren. **Firebase Hosting** nicht aktivieren (Hosting übernimmt GitHub Pages).
3. In **Projekteinstellungen → Allgemein → Deine Apps → SDK-Einrichtung und -Konfiguration → Konfiguration** die Werte `apiKey`, `authDomain`, `databaseURL` (kommt ggf. erst nach dem nächsten Schritt), `projectId`, `appId` notieren.
4. **Erstellen → Realtime Database → Datenbank erstellen**, verfügbare EU-Region wählen (beispielsweise `europe-west1`, falls angeboten), **gesperrten Modus** wählen. Region nach Anlage nicht ohne Migration ändern.
5. Nun `databaseURL` aus **Realtime Database** kopieren. Diese URL muss exakt zur gerade angelegten Datenbank passen.
6. **Erstellen → Authentication → Anmeldemethode → Neue Methode hinzufügen → Anonym → Aktivieren → Speichern**. Anonymous Auth läuft später unsichtbar.
7. **Realtime Database → Regeln**: gesamten Inhalt aus `firebase.rules.json` einfügen, **Veröffentlichen**. Die Regeln erlauben nur authentifizierten anonymen/sonstigen Firebase-Sitzungen den Zugriff auf eine Liste mit einer unerratbaren 64-stelligen Kennung. JEDER, der die Listenkennung kennt, kann diese Liste lesen und bearbeiten. Das ist die ausdrücklich gewünschte Linkfreigabe, **kein personenbezogenes Berechtigungssystem**.
8. Datei `docs/config.example.js` kopieren und als `docs/config.js` speichern. Die fünf Werte durch die Konfigurationswerte des eigenen Firebase-Projekts ersetzen. Kein `HIER_` darf übrig sein. `config.js` ist öffentlich lesbare Client-Konfiguration, **kein Geheimnis** und darf beim Upload mit ins Repository. Niemals Servicekonto-Schlüssel oder Admin-Secrets hinein kopieren.

## 2. Neues GitHub-Repository

1. Auf https://github.com/new **Repository name:** `einkaufsliste-natur`; Sichtbarkeit **Public** (kostenloses GitHub Pages); Repository erstellen, **ohne** zusätzliche README-Vorlage.
2. ZIP entpacken. **Alle Inhalte des Ordners `einkaufsliste-natur`** (einschließlich `.github`, `docs`, `scripts` sowie `docs/config.js`) in das Stammverzeichnis des neuen Repositories hochladen. Am einfachsten mit **Add file → Upload files**; GitHub-Webupload kann versteckte Ordner oder komplexe Ordnerstrukturen je nach Browser einschränken – in dem Fall GitHub Desktop verwenden. Änderungen committen.
3. **Settings → Pages → Build and deployment:** **Deploy from a branch** auswählen; Branch `main`, Folder `/docs`, **Save**. Nach dem ersten erfolgreichen Deployment steht die Adresse unter **Settings → Pages**. Typischerweise `https://BENUTZERNAME.github.io/einkaufsliste-natur/`. Die echte Adresse dort ablesen.
4. **Settings → Actions → General → Workflow permissions**: **Read and write permissions** für den automatischen Commit der Angebotsdatei aktivieren, **Save**. Keine Firebase-Secrets erforderlich. Eventuell greifen Organisationsrichtlinien.
5. **Actions → Angebotsdaten aktualisieren → Run workflow → Run workflow**. Beim ersten Start werden keine Angebote erfunden, wenn keine zulässigen Datenfeeds eingerichtet sind. Protokoll kontrollieren.
6. Die Sonntag-Ausführung verwendet `cron: '0 8 * * 0'` mit `timezone: 'Europe/Berlin'` (Sommer-/Winterzeit). GitHub kann Läufe verzögern oder bei Inaktivität deaktivieren. Actions-Rechte und Repo-Einstellungen regelmäßig prüfen.

## 3. Gemeinsame Liste nutzen

1. GitHub-Pages-Adresse in Safari öffnen. **Gemeinsame Liste erstellen** **ein einziges Mal** drücken. Die Webseite wechselt zu einer URL mit `#list=` und 64 Hex-Zeichen. **Diese URL sofort sichern** (WhatsApp, Notizen oder Lesezeichen), da sie nicht aus einer alten Session wiederherstellbar ist.
2. **Teilen** → Link per WhatsApp/iMessage versenden. Der Link ist ein Bearbeitungsschlüssel. Jeder Linkempfänger kann ihn weiterleiten. Bei Verlust aller Kopien kann die Liste ohne administrative Datenbankeinsicht nicht rekonstruiert werden.
3. Auf weiteren Geräten den vollständigen Einladungslink öffnen; **nicht** erneut „Liste erstellen“ drücken. Änderungen werden über Firebase in Echtzeit synchronisiert.
4. iPhone: Safari → Teilen-Symbol → **Zum Home-Bildschirm** → Hinzufügen. Den vollständigen Listenlink zunächst in Safari öffnen und **von dieser Seite aus** zum Home-Bildschirm hinzufügen. Wenn iOS beim PWA-Start die URL ohne Fragment öffnet, den Einladungslink erneut in der App öffnen.
5. Funktionstest: auf Gerät A `Milch` eingeben, auf Gerät B erscheint `Milch`. Auf Gerät B Karte kurz tippen → Artikel sollte auf beiden Geräten verschwinden. **Rückgängig** zeitnah betätigen. Der „⋯“-Button wählt eine feste Marktzuordnung; auf Desktop kann man eine Karte auf eine Marktgruppe ziehen. iPhone: längeres Drücken öffnet den Markt-Auswahldialog, da natives HTML5-Drag-and-drop auf Safari-Touch nicht zuverlässig ist.

## 4. Angebotsdaten (wesentliche Einschränkung)

Die offiziellen Websites in `sources.json` sind nur Quellenhinweise und **keine bereits freigegebenen technischen Datenfeeds**. Kein automatischer Prospektabruf wird als funktionsfähig ausgegeben, solange `feedUrl` fehlt. Für Händler ohne verlässlich lizenzierte/zugelassene maschinenlesbare JSON-Quelle bleiben die Angebote leer. Das ist beabsichtigt: keine erfundenen, veralteten oder durch unzulässiges Scraping beschafften Preise.

Sobald ein Händler/Datendienst die automatisierte Weiterverarbeitung schriftlich erlaubt und einen **stabilen HTTPS-JSON-Endpunkt** bereitstellt, in `sources.json` beim betreffenden Markt `feedUrl` ergänzen. Erwartetes JSON-Format:

```json
{"offers":[{"name":"Gurke","market":"netto","price":0.88,"validFrom":"2026-11-09","validTo":"2026-11-14","sourceUrl":"https://example.org/beleg-zum-angebot"}]}
```

Die hier gezeigten Daten sind **ausschließlich Schema-Beispieldaten**, kein aktuelles Angebot. `market` muss exakt einer Marktkennung in `markets.json` entsprechen. Das Python-Skript verwirft unvollständige, abgelaufene, zukünftige und nicht-HTTPS-belegte Einträge. Händler- oder filialabhängige Angebote dürfen nur importiert werden, wenn der Feed die Region 59872 entsprechend absichert; der Importer **kann regionale Gültigkeit selbst nicht unabhängig überprüfen**. Es gibt weder PDF-OCR noch automatisches Auslesen von Händlerwebseiten. Keine Zugangsbeschränkungen umgehen.

Das wöchentliche Skript **ruft ausschließlich konfigurierte Feeds ab** und aktualisiert `docs/offers.json`; die App lädt diese Datei beim Öffnen bzw. über **Angebote abgleichen** und gleicht lokal ab. Es gibt **keinen** geheimen GitHub-Token im Browser und keinen Firebase-Zugriff des Python-Skripts; damit entfällt der alte HTTP-401-Datenabruf. Fehlgeschlagene Feed-Abfragen stoppen den Workflow vor einem Commit; bereits veröffentlichte Angebotsdaten bleiben erhalten und werden clientseitig nach Ablauf ausgeblendet.

## 5. Prüfung & Fehlerbehebung

- Vorab lokal: `python -m unittest discover -s scripts/tests -v`, `python scripts/update_offers.py`, `node docs/normalize.test.mjs`. Ein einfacher lokaler HTTP-Server (`python -m http.server 8000 -d docs`) dient nur der Layoutprüfung; Firebase erfordert korrektes Projekt und zulässige Browser-Origin.
- **HTTP 401:** Bei dieser Architektur nicht im Angebotsworkflow erwartet; bei Firebase Web-Sitzung Anonymous Auth prüfen.
- **HTTP 403 / permission_denied:** Datenbankregeln, Region/`databaseURL`, aktivierte Anonymous Auth sowie vollständigen Einladungslink kontrollieren.
- **Keine Artikel:** Browserkonsole prüfen; App muss über HTTPS laufen, `config.js` muss existieren, und Regeln müssen veröffentlicht sein.
- **Keine Angebote:** `sources.json` hat standardmäßig sieben deaktivierte Feed-Anbindungen. Das ist kein Fehler, sondern ein offener externer Integrationsschritt.
- **Doppelte Listen:** Wird durch normalen Start niemals automatisch erstellt. Neue Listen entstehen ausschließlich durch **Gemeinsame Liste erstellen**. Die einmalig erzeugte Link-URL ist maßgeblich.
- **Sicherheit:** Wer die URL kennt, besitzt vollständige Bearbeitungsrechte. Kein Widerruf einzelner Personen, keine Rollen, kein Passwortschutz. Für personenbezogene oder vertrauliche Daten ungeeignet. Firebase Anonymous Auth allein beweist keine Identität oder Einladung; allein der geheime Link fungiert als Zugriffsschlüssel.
- **Icon:** Mitgelieferte Icons sind ein **provisorischer stilisierter Ersatz**, da die originale, zuvor ausgewählte PNG-Datei bei dieser Eingabe nicht beilag. Für motivgetreue Abnahme das Original bereitstellen und die vier PNGs mit dessen Bildinhalt neu exportieren.

## 6. Keine zusätzlichen Gebühren / Grenzen

Die Architektur ist auf Firebase Spark, GitHub Pages und Actions ausgelegt, aber aktuelle Nutzungsgrenzen, Dienst-Verfügbarkeit und GitHub-Actions-Permissions selbst im jeweiligen Konto prüfen. Kein Servicekonto/Secret erforderlich. Mehrgerätetests, Firebase-Regeltests an einer echten Instanz, PWA-Safari-Installation und Live-Quellintegration sind ohne Zugriff auf Ihr neues Projekt nicht hier überprüfbar.
