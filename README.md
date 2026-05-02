# 🌏 Asia-Pacific Digital Trade Regulatory Tool

> An open-source tool built for the **UNESCAP Global Hackathon 2026** — "Where Code Meets Law"
>
> Automatically scrapes, analyzes, and maps digital trade regulations across 20 Asia-Pacific economies using Claude AI.

---

## One-line setup

```bash
git clone https://github.com/YOUR_USERNAME/aptrade.git && cd aptrade && bash start.sh
```

That's it. The script handles everything — dependencies, API check, scraping, analysis, database, and launching the dashboard.

---

## What this does

Most trade regulation research is done by hand — lawyers reading hundreds of PDFs across dozens of countries. This tool automates that entire pipeline:

1. **Scrapes** official government and UN sources for digital trade law documents
2. **Extracts** structured information using Claude AI (topics, strictness, key laws)
3. **Stores** everything in a local SQLite database — no cloud needed
4. **Serves** a visual dashboard where policymakers can explore and compare

---

## Project structure

```
aptrade/
│
├── start.sh                  ← Run this. Does everything.
│
├── backend/
│   ├── scraper.py            ← Fetches regulation documents from the web
│   ├── extractor.py          ← Claude AI reads and tags each document
│   ├── database.py           ← Builds the SQLite database
│   └── server.py             ← Flask API server (talks to the frontend)
│
├── frontend/
│   ├── index.html            ← Main HTML page
│   ├── css/
│   │   └── style.css         ← All styling
│   └── js/
│       ├── explorer.js       ← Country explorer tab
│       ├── pipeline.js       ← Pipeline finder tab
│       ├── guide.js          ← Beginner guide tab
│       └── glossary.js       ← Glossary tab
│
├── scripts/
│   └── seed_samples.py       ← Loads built-in sample data (no scraping needed)
│
├── data/                     ← Auto-created. Stores scraped docs + database
│
├── requirements.txt
└── .env.example              ← Copy to .env and add your API key
```

---

## Manual setup (if you prefer step by step)

**Requirements:** Python 3.8+, pip

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/aptrade.git
cd aptrade

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your Claude API key
cp .env.example .env
# Open .env and paste your key — get one free at https://console.anthropic.com

# 4. Run the scraper (downloads regulation documents)
python backend/scraper.py

# 5. Run the AI extractor (reads + tags each document)
python backend/extractor.py

# 6. Build the database
python backend/database.py

# 7. Start the server
python backend/server.py
# → Open http://localhost:5000
```

---

## Want to skip scraping?

Use sample data instead — no API key needed for this step:

```bash
python scripts/seed_samples.py
python backend/server.py
```

---

## Adding more countries

Open `backend/scraper.py` and add an entry to the `SOURCES` list:

```python
{
    "country": "South Korea",
    "organization": "KISA",
    "topic": "Digital Trade & Data Protection",
    "url": "https://www.kisa.or.kr/..."
}
```

The rest of the pipeline picks it up automatically.

---

## API endpoints

The Flask server exposes a simple REST API the frontend uses:

| Endpoint | Description |
|----------|-------------|
| `GET /api/countries` | All countries + scores |
| `GET /api/country/<name>` | One country's full profile |
| `GET /api/topics` | All regulatory topic names |
| `GET /api/compare/<topic>` | All countries for one topic |
| `GET /api/pipeline?src=X&dst=Y` | Pipeline routes between two countries |

---

## Tech stack

- **Python 3** — scraping, AI extraction, API server
- **Claude AI (claude-sonnet-4-20250514)** — reads legal text, outputs structured JSON
- **SQLite** — lightweight local database, no setup needed
- **Flask** — lightweight Python web server
- **Vanilla JS + HTML/CSS** — no build tools, works in any browser

---

## Data sources

All data comes from official public sources:

- UNESCAP RDTII (Regional Digital Trade Integration Index) 2025
- WTO e-commerce work programme documents
- UNCTAD Digital Economy Reports
- National government ministry websites (IMDA, ETDA, MEITY, etc.)

---

## License

MIT — free to use, modify, and share. Please credit UNESCAP and this project.

---

## Built for

**UNESCAP Global Hackathon 2026** — "Where Code Meets Law"
Partners: World Trade Organization · World Bank · Maynooth University
