# FestCal

Event-Aggregator für die Rhein-Main-Region. Sammelt Veranstaltungen aus Frankfurt, Wiesbaden und Mainz und stellt sie als iCalendar-Feed bereit.

## Status: In Entwicklung

Der erste funktionsfähige Scraper ist implementiert und getestet. Events werden von frankfurter-stadtevents.de gesammelt.

| Komponente | Status |
|------------|--------|
| Projektstruktur | Fertig |
| Datenbank (SQLite) | Fertig |
| Event-Modell | Fertig |
| BaseScraper-Klasse | Fertig |
| Frankfurt Scraper | Fertig |
| Weitere Scraper | Ausstehend |
| iCalendar-Export | Fertig |
| Web-API (Flask) | Fertig |
| CalDAV-Server | Ausstehend |
| Tests | 41 Tests |

---

## Schnellstart

```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Datenbank initialisieren
python -m src.database.db_handler init

# Scraper ausführen
python -m src.scrapers.run_all

# Web-Interface starten
python -m src.web.app
```

---

## Roadmap

### Milestone 1: Fundament (Abgeschlossen)

- [x] Projektstruktur erstellen
- [x] SQLite-Datenbank mit SQLAlchemy
- [x] Event-Datenmodell definieren
- [x] BaseScraper-Abstraktion
- [x] Konfigurations-System (YAML)
- [x] Deduplizierungs-Logik
- [x] CI/CD Pipeline (GitHub Actions)

### Milestone 2: Erster funktionierender Scraper (Abgeschlossen)

- [x] Frankfurter Stadtevents Scraper implementieren
  - [x] Website-Struktur analysieren (frankfurter-stadtevents.de)
  - [x] HTML-Parsing mit BeautifulSoup
  - [x] Event-Extraktion und Mapping
  - [x] Fehlerbehandlung und Retry-Logik
  - [x] Multi-Datum Events (separate Einträge pro Datum)
- [x] End-to-End Test: Scrape → DB → Export
- [x] Logging-Utilities (`src/utils/logging_config.py`)
- [x] Metrics-Collection (`src/utils/metrics.py`)
- [x] Unit-, Integration- und E2E-Tests (41 Tests)

### Milestone 3: Weitere Quellen

- [ ] Wiesbaden Marketing Scraper
- [ ] Mainz Tourismus Scraper
- [ ] Eventbrite Integration (API)
- [ ] Robuste Fehlerbehandlung für alle Scraper

### Milestone 4: Kalender-Export

- [ ] iCalendar-Export testen und verfeinern
- [ ] Filterung nach Stadt/Kategorie/Datum
- [ ] CalDAV-Server implementieren
- [ ] Automatische Updates (Scheduler)

### Milestone 5: Web-Interface

- [ ] REST-API erweitern
- [ ] Einfaches Frontend (HTML/JS)
- [ ] Event-Suche und Filter
- [ ] ICS-Download Button

### Milestone 6: Produktion

- [ ] Docker-Setup finalisieren
- [ ] Dokumentation vervollständigen
- [ ] Performance-Optimierung
- [ ] Deployment-Anleitung

---

## Offene Aufgaben

### Hohe Priorität

- [ ] **Wiesbaden Scraper implementieren** - Nächste Datenquelle
- [ ] **Selenium-Setup** - Für JavaScript-lastige Seiten (z.B. visitfrankfurt.travel)
- [ ] **CalDAV-Server** - Kalender-Sync ermöglichen

### Mittlere Priorität

- [ ] Validierung der Event-Daten verbessern
- [ ] Rate-Limiting für Scraper
- [ ] Proxy-Unterstützung
- [ ] Kategorien aus Events extrahieren

### Niedrige Priorität

- [ ] Mehrsprachigkeit (DE/EN)
- [ ] Push-Benachrichtigungen
- [ ] Mobile-optimiertes Frontend

---

## Projektstruktur

```
FestCal/
├── src/
│   ├── scrapers/          # Web-Scraper
│   │   ├── base_scraper.py
│   │   ├── frankfurt_scraper.py   # Frankfurter Stadtevents
│   │   ├── wiesbaden_scraper.py
│   │   └── run_all.py
│   ├── models/            # Datenmodelle
│   │   └── event.py
│   ├── calendar/          # iCal-Export
│   │   └── generator.py
│   ├── database/          # SQLite
│   │   └── db_handler.py
│   ├── utils/             # Hilfsfunktionen
│   │   ├── logging_config.py
│   │   ├── metrics.py
│   │   ├── deduplicator.py
│   │   └── validators.py
│   └── web/               # Flask-API
│       └── app.py
├── config/
│   ├── sources.yaml       # Event-Quellen
│   └── settings.yaml      # Einstellungen
├── data/
│   ├── events.db          # SQLite-Datenbank
│   └── exports/           # ICS-Exporte
└── tests/
    ├── fixtures/          # Test-HTML-Dateien
    ├── test_scrapers.py
    ├── test_scrapers_integration.py
    └── test_e2e.py
```

---

## Befehle

### Entwicklung

```bash
# Alle Scraper ausführen
python -m src.scrapers.run_all

# Einzelnen Scraper
python -m src.scrapers.run_specific --source "Frankfurter Stadtevents"

# iCalendar exportieren
python -m src.calendar.generator export --output data/exports/events.ics

# Web-Server starten
python -m src.web.app
```

### Tests & Qualität

```bash
# Tests
pytest
pytest --cov=src tests/

# Formatierung
black src/
isort src/

# Linting
flake8 src/
pylint src/
```

### Docker

```bash
docker-compose up -d
```

---

## Konfiguration

### config/sources.yaml

```yaml
sources:
  - name: "Frankfurter Stadtevents"
    url: "https://www.frankfurter-stadtevents.de/datum.html"
    scraper: "frankfurt_scraper"
    enabled: true

  - name: "Wiesbaden Marketing"
    url: "https://www.wiesbaden.de/veranstaltungen"
    scraper: "wiesbaden_scraper"
    enabled: true
```

### Umgebungsvariablen

```bash
CALDAV_PASSWORD=...      # CalDAV-Server Passwort
RHEINMAIN_API_KEY=...    # Optional: API-Zugang
```

---

## API-Endpunkte

| Methode | Pfad | Beschreibung |
|---------|------|--------------|
| GET | `/api/events` | Alle Events (mit Filter) |
| GET | `/api/events/{id}` | Einzelnes Event |
| GET | `/api/export/ics` | iCalendar-Download |
| GET | `/api/cities` | Verfügbare Städte |
| GET | `/api/categories` | Kategorien |

**Query-Parameter:** `city`, `category`, `start_date`, `end_date`, `limit`

---

## Neuen Scraper hinzufügen

1. Neue Datei in `src/scrapers/` erstellen
2. Von `BaseScraper` erben
3. `scrape()` Methode implementieren
4. In `sources.yaml` registrieren

```python
from .base_scraper import BaseScraper
from ..models.event import Event

class MeinScraper(BaseScraper):
    def scrape(self) -> list[Event]:
        html = self.fetch_page(self.url)
        events = []
        # Parsing-Logik hier
        return events
```

---

## Technologien

- **Python 3.9+**
- **Flask** - Web-Framework
- **SQLAlchemy** - ORM
- **SQLite** - Datenbank
- **BeautifulSoup4** - HTML-Parsing
- **Selenium** - JavaScript-Rendering
- **icalendar** - iCal-Generierung
- **pytest** - Testing

---

## Bekannte Probleme

- Wiesbaden/Mainz Scraper geben 0 Events zurück (noch nicht implementiert)
- CalDAV-Server noch nicht funktionsfähig
- Selenium WebDriver muss manuell installiert werden (für JavaScript-lastige Seiten)
- Einige Events auf frankfurter-stadtevents.de werden übersprungen (abweichende HTML-Struktur)

---

## Lizenz

MIT License
