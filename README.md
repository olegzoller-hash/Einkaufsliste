# Natur – geteilte Einkaufsliste

iPhone-freundliche PWA mit Firebase Realtime Database, unsichtbarer Anonymous Auth, 256-Bit-Listenlinks, Produktkarten, Marktgruppen, Rückgängig und Angebotsabgleich mit validierten lokalen Angebotsdaten.

**Start:** `README_EINRICHTUNG.md` lesen, `docs/config.example.js` als `docs/config.js` ausfüllen, Repository auf GitHub Pages `/docs` veröffentlichen, Firebase Anonymous Auth und Regeln aktivieren.

**Grenzen:** Angebotsquellen sind nicht automatisiert (keine autorisierten JSON-Feeds bereitgestellt). Original-Icon und Original-Screenshot waren in diesem Upload nicht verfügbar. Provisorische Icons. Die App ist lokal vorbereitet, aber nicht auf Nutzerkonten live ausgerollt. Der sonntägliche Workflow ist betriebsbereit für später konfigurierte autorisierte JSON-Feeds; bis dahin bleiben Angebote leer. Mehrgerätetests und echte Dienstintegration sind offen.

Automatisierung: `.github/workflows/update-offers.yml` → `scripts/update_offers.py` → `docs/offers.json`. Private Listenprodukte verlassen Firebase nicht für den Workflow.
