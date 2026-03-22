# store_sql.py
# Assignment Step 4+5: Store the fetched weather data in a local SQLite database.
# This script follows the same pattern as store_sql.py from Lecture 3 —
# it is responsible *only* for database logic, keeping fetch.py focused on the API.

import sqlite3
from pathlib import Path

from config import DB_PATH


def init_db() -> sqlite3.Connection:
    """
    Initialise the SQLite database and create the forecasts table if it doesn't exist.
    
    The database file is created at DB_PATH (defined in config.py).
    We use Path().mkdir() to ensure the parent directory (data/) exists first.

    Returns:
        An open sqlite3.Connection to weather.db.
    """
    # Create the data/ directory if it doesn't already exist
    db_path = Path(DB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create the forecasts table if it doesn't already exist.
    # The assignment (Step 5) requires at minimum:
    #   - location name
    #   - forecast date
    #   - selected weather variables (temp, precip, wind)
    # We also add a fetched_at timestamp so we can track when each row was inserted.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS forecasts (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            location    TEXT NOT NULL,
            date        TEXT NOT NULL,
            temp_max    REAL,
            precip      REAL,
            wind_max    REAL,
            fetched_at  TEXT DEFAULT (datetime('now'))
        )
    """)

    conn.commit()
    return conn


def store_forecasts(conn: sqlite3.Connection, forecasts: list[dict]) -> int:
    """
    Insert weather forecast records into the forecasts table.

    Uses INSERT OR REPLACE to avoid duplicate rows if the pipeline runs
    multiple times on the same day for the same location — same approach
    as store_sql.py in Lecture 3 (INSERT OR IGNORE on unique URL).

    Args:
        conn:      An open sqlite3.Connection (from init_db).
        forecasts: List of forecast dicts returned by fetch.fetch_all_locations().

    Returns:
        Number of rows successfully inserted.
    """
    cursor = conn.cursor()
    inserted = 0

    for forecast in forecasts:
        # DELETE any existing row for the same location + date before inserting,
        # so re-running the pipeline on the same day always gives fresh data.
        cursor.execute(
            "DELETE FROM forecasts WHERE location = ? AND date = ?",
            (forecast["location"], forecast["date"]),
        )

        # Insert the new forecast row with all required fields
        cursor.execute("""
            INSERT INTO forecasts (location, date, temp_max, precip, wind_max)
            VALUES (:location, :date, :temp_max, :precip, :wind_max)
        """, forecast)

        inserted += cursor.rowcount

    conn.commit()
    return inserted


# Allow running this script directly to verify the DB is set up correctly:
#   python store_sql.py
if __name__ == "__main__":
    conn = init_db()
    print(f"Database initialised at: {DB_PATH}")
    conn.close()