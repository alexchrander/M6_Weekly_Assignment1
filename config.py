# config.py
# Central configuration file for the weather pipeline.
# Keeping settings here avoids hardcoding values across multiple scripts,
# following the same pattern as the Lecture 3 pipeline (config.py).

from datetime import date, timedelta

# --- Assignment Step 2: Locations ---
# We must fetch weather for:
#   1. Place of birth        → Odense
#   2. Last residence before Aalborg → Randers
#   3. Current city          → Aalborg
# Coordinates sourced from Open-Meteo documentation examples.
LOCATIONS = [
    {"name": "Odense",  "lat": 55.3959, "lon": 10.3883},
    {"name": "Randers", "lat": 56.4607, "lon": 10.0365},
    {"name": "Aalborg", "lat": 57.0488, "lon":  9.9217},
]

# --- Assignment Step 3: Weather Variables ---
# We use three daily forecast variables from the Open-Meteo API:
#   - temperature_2m_max   → maximum air temperature at 2 m height (°C)
#   - precipitation_sum    → total precipitation (rain + snow) in mm
#   - windspeed_10m_max    → maximum wind speed at 10 m height (km/h)
WEATHER_VARIABLES = [
    "temperature_2m_max",
    "precipitation_sum",
    "windspeed_10m_max",
]

# --- Forecast date ---
# The assignment requires weather data for *the next day*.
# timedelta(days=1) shifts today's date forward by one day.
TOMORROW = (date.today() + timedelta(days=1)).isoformat()  # e.g. "2026-03-23"

# --- Database path (Step 5) ---
# The SQLite database file will be created here when store_sql.py runs.
DB_PATH = "data/weather.db"

# --- Open-Meteo base URL ---
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# --- Timezone ---
# Danish timezone ensures daily aggregates align with local midnight.
TIMEZONE = "Europe/Copenhagen"