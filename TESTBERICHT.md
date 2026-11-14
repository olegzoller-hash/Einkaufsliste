# Testbericht – Natur (14.11.2026)

## Lokal tatsächlich ausgeführt

| Prüfung | Ergebnis | Beschreibung |
|---|---|---|
| Python-Unit-Tests | BESTANDEN (3 Tests) | Leerer Feed, unvollständiger Eintrag, abgelaufenes Angebot |
| JavaScript-Assertions | BESTANDEN (6 Assertions) | Umlaut-Normalisierung, Synonyme, Milch/Hafermilch, Marktklammer, Allgemein |
| `scripts/update_offers.py` | BESTANDEN | Sieben Quellen korrekt übersprungen; keine fiktiven Angebote erstellt |
| `firebase.rules.json` / `sources.json` JSON-Syntax | BESTANDEN | JSON-Parser ohne Fehler |
| Automatische Quellenbereitstellung | NICHT IMPLEMENTIERT | Keine sieben zugelassenen strukturierten Feeds verfügbar |

## Nicht live getestet

Firebase-Instanz und veröffentlichte Sicherheitsregeln, echte anonyme Anmeldung, Freigabelink in mehreren Browsern, Mehrgeräte-Synchronisation, Lösch-/Rückgängig-Rennen, GitHub Pages, Live-GitHub-Action, regionale Händlerdaten, tatsächliche Prospektangebote, Safari-PWA-Installation, Touch-Long-Press auf einem iPhone und optischer Abgleich mit dem Original-Screenshot/-Icon. Kein Test wird für diese Punkte als erfolgreich bezeichnet.

## Bekannte Grenzen

1. Quellenliste: offizielle Händlerseiten sind Referenzen, keine gültigen maschinenlesbaren Feeds. URLs für manche Händler sind Startseiten statt nachgewiesener Prospekt-Endpunkte.
2. Es gibt **keinen** automatischen Abruf aus HTML-/PDF-Prospekten. Der Workflow verarbeitet nur freigegebene JSON-Feeds.
3. Einladungslink ist ein Zugriffsschlüssel ohne einzelne Zugriffsrechte oder Widerruf; Personen können Links weiterleiten.
4. Bei fehlendem Link nach Browserdaten-Löschung kann die bereits angelegte Liste nicht automatisch gefunden werden. Der alte Link verbindet zuverlässig wieder, sofern die Datenbank besteht.
5. Rückgängig restauriert einen Artikel nur, wenn die Kennung noch nicht belegt ist; kein transaktionales Konfliktmanagement bei gleichzeitigen Bearbeitungen desselben Artikels.
6. iPhone-Long-Press öffnet Marktauswahl, keine echte visuelle Ziehbewegung. Desktop-Drop funktioniert auf bereits sichtbare Gruppen.
7. Nur exakte, konfigurierte Produkt-Synonyme werden zugeordnet; viele Packungs-/Markenvarianten werden nicht erkannt. Vergleichspreise sind nicht nach Einheiten umgerechnet.
8. Platzhalter-Icons wurden **neu gezeichnet**, nicht aus der nicht mitgelieferten Original-PNG extrahiert. Verbindliche Designabnahme ist daher offen.
9. GitHub Action benötigt Schreibberechtigung auf dem Default-Branch; Branchschutz kann automatische Commits verhindern. GitHub-Schedule kann verspätet oder ausfallen.
10. In der Offline-Ansicht sind Echtzeitliste und aktuelle Angebotsdaten nicht verfügbar. Die PWA cached nur den App-Shell-Code.

## Abnahmezustand

**Teilweise implementierter, lokal getesteter Projektstand, nicht vollständig abgenommen.** Für vollständige Abnahme sind Firebase-/GitHub-Livezugriff, Originalbilddateien und zulässige Datenquellen notwendig.
