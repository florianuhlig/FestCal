# Event Aggregator

Ein Python-Projekt zur automatischen Sammlung, Aggregation und Bereitstellung von Festen, Veranstaltungen und Events in Frankfurt, Wiesbaden und Umgebung als iCalendar/CalDAV-Feed.

## 📋 Projektübersicht

Dieses Tool durchsucht automatisch verschiedene Quellen nach Veranstaltungen in der Rhein-Main-Region und stellt diese in einem standardisierten iCalendar-Format (.ics) bereit, das in gängige Kalender-Apps (Google Calendar, Apple Calendar, Outlook, etc.) importiert werden kann.

## ✨ Features

- **Multi-Source Aggregation**: Sammelt Events von verschiedenen Webseiten und APIs
- **Automatische Updates**: Regelmäßige Aktualisierung der Event-Daten
- **iCalendar Export**: Standard-konforme .ics-Dateien
- **CalDAV Server**: Optional: Eigener CalDAV-Server für Synchronisation
- **Filterung**: Nach Stadt, Kategorie, Datum
- **Deduplizierung**: Automatisches Entfernen von Duplikaten
- **Web-Interface**: Einfache Übersicht aller Events

## 🏗️ Projektstruktur

```
rhein-main-events/
├── src/
│   ├── scrapers/           # Web-Scraper für verschiedene Quellen
│   │   ├── __init__.py
│   │   ├── base_scraper.py
│   │   ├── frankfurt_scraper.py
│   │   ├── wiesbaden_scraper.py
│   │   └── tourismus_scraper.py
│   ├── models/             # Datenmodelle
│   │   ├── __init__.py
│   │   └── event.py
│   ├── calendar/           # iCalendar-Generierung
│   │   ├── __init__.py
│   │   ├── generator.py
│   │   └── caldav_server.py
│   ├── database/           # Datenbank-Handler
│   │   ├── __init__.py
│   │   └── db_handler.py
│   ├── utils/              # Hilfsfunktionen
│   │   ├── __init__.py
│   │   ├── deduplicator.py
│   │   └── validators.py
│   └── web/                # Web-Interface
│       ├── __init__.py
│       └── app.py
├── config/
│   ├── sources.yaml        # Konfiguration der Event-Quellen
│   └── settings.yaml       # Allgemeine Einstellungen
├── data/
│   ├── events.db           # SQLite Datenbank
│   └── exports/            # Exportierte .ics Dateien
├── tests/
│   ├── test_scrapers.py
│   ├── test_calendar.py
│   └── test_deduplication.py
├── requirements.txt
├── setup.py
├── docker-compose.yml
├── Dockerfile
└── README.md
```

## 🚀 Installation

### Voraussetzungen

- Python 3.9 oder höher
- pip
- Optional: Docker & Docker Compose

### Lokale Installation

```bash
# Repository klonen
git clone https://github.com/dein-username/rhein-main-events.git
cd rhein-main-events

# Virtuelle Umgebung erstellen
python -m venv venv
source venv/bin/activate  # Unter Windows: venv\Scripts\activate

# Dependencies installieren
pip install -r requirements.txt

# Datenbank initialisieren
python -m src.database.db_handler init

# Konfiguration anpassen
cp config/settings.yaml.example config/settings.yaml
# Bearbeite settings.yaml nach Bedarf
```

### Docker Installation

```bash
# Mit Docker Compose starten
docker-compose up -d
```

## 📦 Dependencies

Die wichtigsten Python-Pakete (vollständige Liste in `requirements.txt`):

```
# Web Scraping
requests>=2.31.0
beautifulsoup4>=4.12.0
selenium>=4.15.0
scrapy>=2.11.0

# Kalender & Datum
icalendar>=5.0.11
caldav>=1.3.9
python-dateutil>=2.8.2
pytz>=2023.3

# Datenbank
sqlalchemy>=2.0.23
alembic>=1.13.0

# Web Framework
flask>=3.0.0
flask-cors>=4.0.0

# Utilities
pyyaml>=6.0.1
python-dotenv>=1.0.0
schedule>=1.2.0

# Testing
pytest>=7.4.3
pytest-cov>=4.1.0
```

## ⚙️ Konfiguration

### sources.yaml

Definiert die Event-Quellen:

```yaml
sources:
  - name: "Frankfurt Tourismus"
    url: "https://www.frankfurt-tourismus.de/events"
    type: "web"
    scraper: "frankfurt_scraper"
    enabled: true
    categories: ["fest", "kultur", "musik", "sport"]
    
  - name: "Wiesbaden Marketing"
    url: "https://www.wiesbaden.de/veranstaltungen"
    type: "web"
    scraper: "wiesbaden_scraper"
    enabled: true
    categories: ["fest", "kultur", "markt"]
    
  - name: "Rhein-Main API"
    url: "https://api.rheinmain.de/events"
    type: "api"
    api_key_env: "RHEINMAIN_API_KEY"
    enabled: true
```

### settings.yaml

Allgemeine Einstellungen:

```yaml
app:
  name: "Rhein-Main Event Aggregator"
  timezone: "Europe/Berlin"
  
database:
  path: "data/events.db"
  
scraping:
  user_agent: "Mozilla/5.0 (compatible; RheinMainEventBot/1.0)"
  delay_between_requests: 2  # Sekunden
  max_retries: 3
  
calendar:
  export_path: "data/exports"
  calendar_name: "Rhein-Main Feste"
  update_interval: 3600  # Sekunden (1 Stunde)
  
caldav:
  enabled: false
  host: "0.0.0.0"
  port: 8080
  username: "admin"
  password_env: "CALDAV_PASSWORD"
  
web:
  enabled: true
  host: "0.0.0.0"
  port: 5000
  debug: false
  
filtering:
  cities:
    - "Frankfurt am Main"
    - "Wiesbaden"
    - "Mainz"
    - "Darmstadt"
    - "Offenbach"
  max_distance_km: 50  # Umkreis
```

## 🔧 Verwendung

### Event-Daten sammeln

```bash
# Alle Quellen einmal durchsuchen
python -m src.scrapers.run_all

# Nur bestimmte Quelle
python -m src.scrapers.run_specific --source "Frankfurt Tourismus"

# Mit Zeitraum
python -m src.scrapers.run_all --start-date 2024-01-01 --end-date 2024-12-31
```

### iCalendar exportieren

```bash
# Alle Events exportieren
python -m src.calendar.generator export --output data/exports/rhein_main_events.ics

# Nach Stadt filtern
python -m src.calendar.generator export --city "Frankfurt" --output frankfurt_events.ics

# Nach Kategorie filtern
python -m src.calendar.generator export --category "fest" --output feste.ics
```

### Web-Interface starten

```bash
python -m src.web.app
```

Öffne dann: http://localhost:5000

### CalDAV Server starten

```bash
python -m src.calendar.caldav_server
```

CalDAV URL: http://localhost:8080/calendars/rhein-main-events/

### Automatische Updates einrichten

```bash
# Cron-Job erstellen (Linux/Mac)
crontab -e

# Füge hinzu (alle 6 Stunden):
0 */6 * * * cd /pfad/zum/projekt && /pfad/zum/venv/bin/python -m src.scrapers.run_all
```

## 🗂️ Datenmodell

### Event

```python
class Event:
    id: str                    # Eindeutige ID
    title: str                 # Titel des Events
    description: str           # Beschreibung
    start_datetime: datetime   # Startzeit
    end_datetime: datetime     # Endzeit
    location: str              # Veranstaltungsort
    address: str               # Adresse
    city: str                  # Stadt
    postal_code: str           # PLZ
    latitude: float            # Koordinaten
    longitude: float           
    category: str              # Kategorie (fest, kultur, etc.)
    organizer: str             # Veranstalter
    url: str                   # Original-URL
    image_url: str             # Bild-URL
    price: str                 # Preis-Info
    source: str                # Quelle
    created_at: datetime       # Erstellt am
    updated_at: datetime       # Aktualisiert am
```

## 🎯 API Endpoints (Web-Interface)

```
GET  /api/events              # Alle Events (mit Filterung)
GET  /api/events/{id}         # Einzelnes Event
GET  /api/export/ics          # iCalendar Download
GET  /api/cities              # Verfügbare Städte
GET  /api/categories          # Verfügbare Kategorien
GET  /api/stats               # Statistiken
```

Query-Parameter:
- `city`: Stadt filtern
- `category`: Kategorie filtern
- `start_date`: Ab Datum (ISO 8601)
- `end_date`: Bis Datum (ISO 8601)
- `limit`: Max. Anzahl Ergebnisse

## 🧪 Tests ausführen

```bash
# Alle Tests
pytest

# Mit Coverage
pytest --cov=src tests/

# Spezifische Tests
pytest tests/test_scrapers.py
```

## 🐳 Docker

### Docker Compose Konfiguration

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "5000:5000"
      - "8080:8080"
    volumes:
      - ./data:/app/data
      - ./config:/app/config
    environment:
      - PYTHONUNBUFFERED=1
      - CALDAV_PASSWORD=${CALDAV_PASSWORD}
    restart: unless-stopped

  scheduler:
    build: .
    command: python -m src.scheduler
    volumes:
      - ./data:/app/data
      - ./config:/app/config
    depends_on:
      - app
    restart: unless-stopped
```

## 📱 Integration in Kalender-Apps

### Google Calendar

1. Öffne Google Calendar
2. Links: "Weitere Kalender" → "Über URL hinzufügen"
3. Trage ein: `http://deine-domain.de/api/export/ics`

### Apple Calendar

1. Kalender-App öffnen
2. Ablage → Neues Kalenderabonnement
3. URL eingeben: `http://deine-domain.de/api/export/ics`

### Outlook

1. Kalender öffnen
2. Kalender hinzufügen → Aus dem Internet
3. URL eingeben und Namen vergeben

## 🔍 Event-Quellen (Beispiele)

Das Projekt kann folgende Quellen nutzen:

- Frankfurt Tourismus (www.frankfurt-tourismus.de)
- Wiesbaden Marketing (www.wiesbaden.de)
- Mainz Tourismus (www.mainz-tourismus.com)
- Eventbrite (www.eventbrite.de)
- Facebook Events (über API)
- Lokale Veranstalter-Websites
- Stadtportale und Gemeinden

## 🛠️ Entwicklung

### Neuen Scraper hinzufügen

1. Erstelle neue Datei in `src/scrapers/`
2. Erbe von `BaseScraper`
3. Implementiere `scrape()` Methode
4. Registriere in `sources.yaml`

Beispiel:

```python
from .base_scraper import BaseScraper
from ..models.event import Event

class MeinStadtScraper(BaseScraper):
    def scrape(self) -> list[Event]:
        events = []
        # Scraping-Logik hier
        return events
```

### Code-Style

```bash
# Code formatieren
black src/
isort src/

# Linting
flake8 src/
pylint src/
```

## 📝 To-Do / Roadmap

- [ ] Mehr Event-Quellen integrieren
- [ ] Machine Learning für Kategorisierung
- [ ] Push-Benachrichtigungen
- [ ] Mobile App
- [ ] Mehrsprachigkeit (DE/EN)
- [ ] Favoriten-Funktion
- [ ] Social Sharing
- [ ] Export zu Google Calendar API
- [ ] Wetter-Integration
- [ ] Routenplanung-Integration

## 🤝 Contributing

Contributions sind willkommen! Bitte:

1. Fork das Repository
2. Erstelle einen Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Committe deine Änderungen (`git commit -m 'Add AmazingFeature'`)
4. Push zum Branch (`git push origin feature/AmazingFeature`)
5. Öffne einen Pull Request

## 📄 Lizenz

MIT License - siehe LICENSE Datei

## 👤 Autor

Dein Name - [@dein-twitter](https://twitter.com/dein-twitter)

Projekt Link: [https://github.com/dein-username/rhein-main-events](https://github.com/dein-username/rhein-main-events)

## 🙏 Danksagungen

- Alle Event-Veranstalter in der Region
- Open Source Libraries
- Community Contributors

## ❓ FAQ

**F: Wie oft werden die Events aktualisiert?**
A: Standardmäßig alle 6 Stunden. Konfigurierbar in settings.yaml.

**F: Kann ich eigene Event-Quellen hinzufügen?**
A: Ja! Erstelle einfach einen neuen Scraper und füge ihn zur sources.yaml hinzu.

**F: Werden historische Events gespeichert?**
A: Ja, alle Events bleiben in der Datenbank. Alte Events können gefiltert werden.

**F: Ist das Projekt DSGVO-konform?**
A: Es werden nur öffentliche Event-Daten gesammelt. Keine personenbezogenen Nutzerdaten.

## 📞 Support

Bei Fragen oder Problemen:
- GitHub Issues: [Issues öffnen](https://github.com/dein-username/rhein-main-events/issues)
- E-Mail: support@deine-domain.de

---

**Happy Event Hunting! 🎉**
