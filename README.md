# FestCal

Event-Aggregator für die Rhein-Main-Region. Sammelt Veranstaltungen aus Frankfurt, Wiesbaden und Mainz und stellt sie als iCalendar-Feed bereit.

## Status: In Entwicklung

Die Projektstruktur und Infrastruktur stehen. Die Scraper-Implementierungen fehlen noch.

| Komponente | Status |
|------------|--------|
| Projektstruktur | Fertig |
| Datenbank (SQLite) | Fertig |
| Event-Modell | Fertig |
| BaseScraper-Klasse | Fertig |
| Scraper-Implementierungen | Ausstehend |
| iCalendar-Export | Fertig |
| Web-API (Flask) | Fertig |
| CalDAV-Server | Ausstehend |
| Tests | Teilweise |

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

### Milestone 2: Erster funktionierender Scraper

- [ ] Frankfurt Tourismus Scraper implementieren
  - [ ] Website-Struktur analysieren
  - [ ] HTML-Parsing mit BeautifulSoup
  - [ ] Event-Extraktion und Mapping
  - [ ] Fehlerbehandlung und Retry-Logik
- [ ] End-to-End Test: Scrape → DB → Export
- [ ] Logging und Monitoring verbessern

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

- [ ] **Frankfurt Scraper implementieren** - Erste echte Datenquelle
- [ ] **Website-Struktur dokumentieren** - Welche Elemente enthalten die Event-Daten?
- [ ] **Selenium-Setup** - Falls JavaScript-Rendering nötig ist

### Mittlere Priorität

- [ ] Testabdeckung erhöhen (aktuell nur Grundgerüst)
- [ ] Validierung der Event-Daten verbessern
- [ ] Rate-Limiting für Scraper
- [ ] Proxy-Unterstützung

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
│   │   ├── frankfurt_scraper.py
│   │   ├── wiesbaden_scraper.py
│   │   └── run_all.py
│   ├── models/            # Datenmodelle
│   │   └── event.py
│   ├── calendar/          # iCal-Export
│   │   └── generator.py
│   ├── database/          # SQLite
│   │   └── db_handler.py
│   ├── utils/             # Hilfsfunktionen
│   └── web/               # Flask-API
│       └── app.py
├── config/
│   ├── sources.yaml       # Event-Quellen
│   └── settings.yaml      # Einstellungen
├── data/
│   └── events.db          # SQLite-Datenbank
└── tests/
```

---

## Befehle

### Entwicklung

```bash
# Alle Scraper ausführen
python -m src.scrapers.run_all

# Einzelnen Scraper
python -m src.scrapers.run_specific --source "Frankfurt Tourismus"

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
  - name: "Frankfurt Tourismus"
    url: "https://www.frankfurt-tourismus.de/events"
    scraper_class: "FrankfurtScraper"
    enabled: true

  - name: "Wiesbaden Marketing"
    url: "https://www.wiesbaden.de/veranstaltungen"
    scraper_class: "WiesbadenScraper"
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

- Scraper geben aktuell 0 Events zurück (nicht implementiert)
- CalDAV-Server noch nicht funktionsfähig
- Selenium WebDriver muss manuell installiert werden

---

## Lizenz

MIT License
