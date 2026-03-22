# M6 Weekly Assignment 1 — Automated Weather Pipeline

A small end-to-end MLOps pipeline that collects daily weather forecasts, stores them in a SQL database, generates a bilingual poem using an LLM, and publishes the result as a public website using GitHub Pages.

🌐 **Live dashboard:** [https://alexchrander.github.io/M6_Weekly_Assignment1/](https://alexchrander.github.io/M6_Weekly_Assignment1/)

---

## What it does

1. Fetches tomorrow's weather forecast for **Odense, Randers, and Aalborg** from the [Open-Meteo API](https://open-meteo.com/)
2. Stores the forecast data in a local **SQLite database**
3. Generates a **bilingual poem** (English + Danish) comparing the three locations using the **Groq LLM API**
4. Publishes the poem and weather data to a **GitHub Pages website**
5. Runs automatically every day at **20:00 Danish time** via **GitHub Actions**

---

## Project structure

```
├── .github/
│   └── workflows/
│       └── weather_pipeline.yml  # GitHub Actions workflow (Step 7)
├── docs/
│   └── index.html                # Generated dashboard served by GitHub Pages (Step 8)
├── data/
│   └── weather.db                # SQLite database with forecast data (Step 5)
├── config.py                     # Shared settings: locations, variables, paths
├── fetch.py                      # Fetches weather data from Open-Meteo API (Step 2+3)
├── store_sql.py                  # Stores forecast data in SQLite (Step 4+5)
├── generate_dashboard.py         # Calls Groq API and writes docs/index.html (Step 6+8)
├── run_pipeline.py               # Orchestrates the full pipeline (Step 7)
└── requirements.txt              # Python dependencies
```

---

## Pipeline overview

```
Open-Meteo API → fetch.py → store_sql.py → weather.db
                                                ↓
                                   generate_dashboard.py
                                         ↓         ↓
                                     Groq API   docs/index.html
                                                    ↓
                                            GitHub Pages
```

---

## Technologies used

| Component | Technology |
|---|---|
| Weather data | Open-Meteo API (free, no key required) |
| Database | SQLite |
| LLM | Groq API (llama-3.3-70b-versatile) |
| Automation | GitHub Actions |
| Publishing | GitHub Pages |

---

## Author

Alexander Christiansen — MSc student 2nd semester in Business Data Science, Aalborg University