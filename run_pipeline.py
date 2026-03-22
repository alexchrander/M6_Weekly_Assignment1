# run_pipeline.py
# The main orchestrator script for the weather pipeline.
# This is the single entry point that the GitHub Actions workflow will call (Step 7).
# It runs the full pipeline in sequence:
#   1. Fetch weather data from Open-Meteo (fetch.py)
#   2. Store the data in SQLite (store_sql.py)
#   3. Generate the poem and update the dashboard (generate_dashboard.py)
# This follows the same orchestration pattern as run_pipeline.py in Lecture 3.

from fetch import fetch_all_locations
from store_sql import init_db, store_forecasts
from generate_dashboard import generate_dashboard


def main() -> None:
    print("=" * 60)
    print("Weather Pipeline — Odense / Randers / Aalborg")
    print("=" * 60)

    # --- Step 1: Fetch weather data from Open-Meteo ---
    # fetch_all_locations() calls the API for each location in config.LOCATIONS
    # and returns a list of forecast dicts (one per location).
    print("\n[1/3] Fetching weather forecasts...")
    forecasts = fetch_all_locations()
    print(f"  Fetched {len(forecasts)} forecasts")

    # --- Step 2: Store the data in SQLite ---
    # init_db() creates the database and table if they don't exist.
    # store_forecasts() inserts the fetched records into the forecasts table.
    print("\n[2/3] Storing forecasts in SQLite database...")
    conn = init_db()
    inserted = store_forecasts(conn, forecasts)
    conn.close()
    print(f"  Inserted {inserted} row(s) into weather.db")

    # --- Step 3: Generate poem and update dashboard ---
    # generate_dashboard() reads from the DB, calls the Groq API for a poem,
    # and writes the result to docs/index.html for GitHub Pages (Step 8).
    print("\n[3/3] Generating poem and updating dashboard...")
    generate_dashboard()
    print("  Dashboard written to docs/index.html")

    print("\n" + "=" * 60)
    print("Pipeline complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()