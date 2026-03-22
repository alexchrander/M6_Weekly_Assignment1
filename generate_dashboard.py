# generate_dashboard.py
# Assignment Step 6+8: Generate a bilingual poem using the Groq API based on
# the weather data stored in SQLite, then publish the result to docs/index.html
# for GitHub Pages.
# Follows the same pattern as generate_dashboard.py from Lecture 4.

import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

from config import DB_PATH

# Load environment variables from .env file if it exists.
# Locally this picks up GROQ_API_KEY from .env.
# In GitHub Actions the secret is injected directly, so load_dotenv() is a no-op there.
load_dotenv()


# --- Paths ---
# docs/ is the folder GitHub Pages serves from (Step 8)
DOCS_DIR = Path("docs")
OUTPUT_HTML = DOCS_DIR / "index.html"


def load_forecasts(conn: sqlite3.Connection) -> list[dict]:
    """
    Read the most recent forecast rows from the SQLite database.
    We select the latest date available to ensure we always show tomorrow's data,
    even if older rows exist from previous pipeline runs.

    Returns:
        A list of forecast dicts, one per location.
    """
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name
    cursor = conn.cursor()

    # Fetch only the rows for the most recent forecast date
    cursor.execute("""
        SELECT location, date, temp_max, precip, wind_max
        FROM forecasts
        WHERE date = (SELECT MAX(date) FROM forecasts)
        ORDER BY location
    """)

    # Convert sqlite3.Row objects to plain dicts for easier use downstream
    return [dict(row) for row in cursor.fetchall()]


def build_prompt(forecasts: list[dict]) -> str:
    """
    Build the prompt we send to the Groq LLM (Step 6).
    The assignment requires the poem to:
      - Compare the weather in the three locations
      - Describe the differences
      - Suggest where it would be nicest to be tomorrow
      - Be written in two languages (English + Danish)
    """
    # Format each location's forecast as a readable line for the prompt
    lines = []
    for f in forecasts:
        lines.append(
            f"- {f['location']} on {f['date']}: "
            f"max temperature {f['temp_max']}°C, "
            f"precipitation {f['precip']} mm, "
            f"max wind speed {f['wind_max']} km/h"
        )
    weather_summary = "\n".join(lines)

    return f"""You are a creative poet. Based on the following weather forecasts for tomorrow, write a short bilingual poem that:
- Compares the weather in the three locations: Odense, Randers, and Aalborg
- Describes the differences vividly
- Suggests where it would be nicest to be tomorrow
- Is written first in English, then in Danish

Separate the two versions with a line containing only "---".

Weather data:
{weather_summary}

Write the poem now."""


def generate_poem(prompt: str) -> str:
    """
    Call the Groq API with the weather prompt and return the generated poem.

    The GROQ_API_KEY is read from the environment — locally from a .env file,
    and in GitHub Actions from a repository secret (Step 7).
    """
    # Groq client automatically reads GROQ_API_KEY from the environment
    client = Groq(api_key=os.environ["GROQ_API_KEY"])

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",  # Fast, capable open-source model available on Groq
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,         # Higher temperature = more creative/varied output
        max_tokens=600,
    )

    return response.choices[0].message.content.strip()


def build_weather_table(forecasts: list[dict]) -> str:
    """
    Build an HTML table showing the raw weather data for each location.
    This satisfies the optional 'weather information' display in Step 8.
    """
    rows = ""
    for f in forecasts:
        rows += f"""
        <tr>
            <td>{f['location']}</td>
            <td>{f['date']}</td>
            <td>{f['temp_max']} °C</td>
            <td>{f['precip']} mm</td>
            <td>{f['wind_max']} km/h</td>
        </tr>"""

    return f"""
    <table>
        <thead>
            <tr>
                <th>Location</th>
                <th>Date</th>
                <th>Max Temp</th>
                <th>Precipitation</th>
                <th>Max Wind</th>
            </tr>
        </thead>
        <tbody>{rows}
        </tbody>
    </table>"""


def write_html(forecasts: list[dict], poem: str) -> None:
    """
    Write the final docs/index.html file that GitHub Pages will serve (Step 8).
    The page displays the bilingual poem and a weather data table.
    The file is overwritten on every pipeline run so it always shows fresh data.
    """
    # Split the poem into English and Danish sections on the "---" separator
    parts = poem.split("---")
    english = parts[0].strip() if len(parts) > 0 else poem
    danish  = parts[1].strip() if len(parts) > 1 else ""

    # Convert newlines to <br> tags so line breaks render correctly in HTML
    english_html = english.replace("\n", "<br>")
    danish_html  = danish.replace("\n", "<br>")

    weather_table = build_weather_table(forecasts)
    forecast_date = forecasts[0]["date"] if forecasts else "N/A"

    # Ensure the docs/ directory exists before writing
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Weather Pipeline Dashboard</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 860px;
            margin: 40px auto;
            padding: 0 20px;
            background: #f5f7fa;
            color: #2f2f2f;
        }}
        h1 {{ color: #2c5f8a; }}
        h2 {{ color: #3a7abd; margin-top: 40px; }}
        .poem-box {{
            background: white;
            border-left: 4px solid #3a7abd;
            border-radius: 6px;
            padding: 20px 28px;
            margin: 16px 0;
            line-height: 1.8;
            box-shadow: 0 2px 6px rgba(0,0,0,0.07);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 6px;
            overflow: hidden;
            box-shadow: 0 2px 6px rgba(0,0,0,0.07);
        }}
        th {{
            background: #2c5f8a;
            color: white;
            padding: 10px 14px;
            text-align: left;
        }}
        td {{
            padding: 10px 14px;
            border-bottom: 1px solid #eee;
        }}
        tr:last-child td {{ border-bottom: none; }}
        .footer {{
            margin-top: 40px;
            color: #888;
            font-size: 0.9rem;
        }}
    </style>
</head>
<body>
    <h1>🌤 Weather Pipeline Dashboard</h1>
    <p>Automated daily weather forecast and poem for <strong>{forecast_date}</strong>,
    generated by GitHub Actions.</p>

    <h2>📝 Poem (English)</h2>
    <div class="poem-box">{english_html}</div>

    <h2>📝 Digt (Dansk)</h2>
    <div class="poem-box">{danish_html}</div>

    <h2>📊 Weather Data</h2>
    {weather_table}

    <p class="footer">
        Pipeline: Open-Meteo API → SQLite → Groq LLM → GitHub Pages<br>
        Locations: Odense · Randers · Aalborg
    </p>
</body>
</html>"""

    OUTPUT_HTML.write_text(html, encoding="utf-8")


def generate_dashboard() -> None:
    """
    Main function called by run_pipeline.py.
    Orchestrates loading data, generating the poem, and writing the HTML.
    """
    # Load the latest forecasts from the database
    conn = sqlite3.connect(DB_PATH)
    forecasts = load_forecasts(conn)
    conn.close()

    if not forecasts:
        raise RuntimeError("No forecast data found in the database. Run fetch.py first.")

    # Build the prompt and call Groq to generate the bilingual poem
    prompt = build_prompt(forecasts)
    print("  Calling Groq API...")
    poem = generate_poem(prompt)
    print(f"  Poem generated ({len(poem)} characters)")

    # Write the final HTML page
    write_html(forecasts, poem)


# Allow running this script directly for testing:
#   python generate_dashboard.py
if __name__ == "__main__":
    generate_dashboard()
    print(f"Dashboard written to {OUTPUT_HTML}")