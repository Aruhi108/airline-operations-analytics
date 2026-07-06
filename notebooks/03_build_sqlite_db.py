"""
03_build_sqlite_db.py
-----------------------
Builds airline_ops.db (SQLite) from the cleaned CSVs so the project can be
connected to directly from Power BI, Tableau, or the Streamlit app — instead
of everyone re-running the SQL schema by hand.
"""

import sqlite3
import pandas as pd

DATA_DIR = "/home/claude/airline-operations-analytics/data"
DB_PATH = f"{DATA_DIR}/airline_ops.db"

flights = pd.read_csv(f"{DATA_DIR}/airline_flights_clean.csv")
airports = pd.read_csv(f"{DATA_DIR}/airports_dim.csv")

conn = sqlite3.connect(DB_PATH)

airports.to_sql("airports", conn, if_exists="replace", index=False)
flights.to_sql("flights", conn, if_exists="replace", index=False)

# Recreate the same indexes used in sql/01_schema.sql for query performance
cur = conn.cursor()
cur.execute("CREATE INDEX IF NOT EXISTS idx_flights_date ON flights (flight_date)")
cur.execute("CREATE INDEX IF NOT EXISTS idx_flights_airline ON flights (airline)")
cur.execute("CREATE INDEX IF NOT EXISTS idx_flights_origin ON flights (origin_airport)")
cur.execute("CREATE INDEX IF NOT EXISTS idx_flights_dest ON flights (destination_airport)")
conn.commit()

# Quick sanity check — run one of the project's real SQL queries against it
check = pd.read_sql("""
    SELECT airline, COUNT(*) AS total_flights,
           ROUND(AVG(departure_delay_minutes),1) AS avg_departure_delay
    FROM flights
    WHERE cancelled = 0
    GROUP BY airline
    ORDER BY avg_departure_delay DESC
""", conn)
print(check)

conn.close()
print(f"\nSQLite database written to: {DB_PATH}")
