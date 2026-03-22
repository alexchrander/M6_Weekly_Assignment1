# fetch.py
# Assignment Step 2+3: Collect weather forecast data from the Open-Meteo API.
# This script is responsible *only* for fetching — storing is handled by store_sql.py,
# following the same separation of concerns as the Lecture 3 pipeline.

import requests

from config import LOCATIONS, WEATHER_VARIABLES, TOMORROW, OPEN_METEO_URL, TIMEZONE


def fetch_weather(location: dict) -> dict:
    """
    Fetch tomorrow's weather forecast for a single location from Open-Meteo.

    Open-Meteo is a free, no-key API — we just build the URL with the right
    parameters and parse the JSON response.

    Args:
        location: A dict with keys "name", "lat", "lon" (from config.LOCATIONS).

    Returns:
        A flat dict with location name, forecast date, and the three weather variables.
    """

    # Build query parameters for the Open-Meteo /v1/forecast endpoint.
    # - daily: list of variables we want (defined in config.py, Step 3)
    # - start_date / end_date: both set to TOMORROW so we get exactly one day
    # - timezone: ensures the daily values align with Danish local time
    params = {
        "latitude":   location["lat"],
        "longitude":  location["lon"],
        "daily":      WEATHER_VARIABLES,
        "timezone":   TIMEZONE,
        "start_date": TOMORROW,
        "end_date":   TOMORROW,
    }

    # Make the HTTP GET request; raise an exception if the server returns an error status
    response = requests.get(OPEN_METEO_URL, params=params, timeout=30)
    response.raise_for_status()

    # The API returns a nested JSON object — the daily forecast values live under "daily"
    daily = response.json()["daily"]

    # Each variable is a list with one value per requested day.
    # Since we only requested TOMORROW, index [0] gives us that single day's value.
    return {
        "location": location["name"],
        "date":     daily["time"][0],               # e.g. "2026-03-23"
        "temp_max": daily["temperature_2m_max"][0], # °C
        "precip":   daily["precipitation_sum"][0],  # mm
        "wind_max": daily["windspeed_10m_max"][0],  # km/h
    }


def fetch_all_locations() -> list[dict]:
    """
    Loop over all locations defined in config.py (Step 2) and fetch weather for each.
    Returns a list of forecast dicts ready to be passed to store_sql.py.
    """
    results = []

    for location in LOCATIONS:
        print(f"  Fetching weather for {location['name']}...")
        data = fetch_weather(location)
        print(f"    → {data}")
        results.append(data)

    return results


# Allow running this script directly for a quick sanity check:
#   python fetch.py
# This will print the raw forecasts without storing anything in the database.
if __name__ == "__main__":
    forecasts = fetch_all_locations()
    print(f"\nFetched {len(forecasts)} forecasts for {TOMORROW}")