"""
00_generate_dataset.py
-----------------------
Generates a realistic, intentionally MESSY airline operations dataset
(nulls, duplicates, outliers, mixed types) so the project can demonstrate
genuine data-cleaning work in Python, exactly like a real analyst would face.

Domain    : Airline Operations Analytics
Grain     : One row = one scheduled flight
Time span : 12 months (2025-01-01 to 2025-12-31)
Size      : ~12,000 flight records, 9 airports, 6 airlines
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)

# ---------------------------------------------------------------------------
# 1. Reference / dimension data
# ---------------------------------------------------------------------------
airlines = ["SkyLink Air", "BlueWing Airlines", "Falcon Jet", "Horizon Airways",
            "Coastal Express", "Summit Airlines"]

# airport code -> (city, state/region, hub_size)
airports = {
    "JFK": ("New York", "Northeast", "Large"),
    "LAX": ("Los Angeles", "West", "Large"),
    "ORD": ("Chicago", "Midwest", "Large"),
    "ATL": ("Atlanta", "South", "Large"),
    "DFW": ("Dallas", "South", "Large"),
    "DEN": ("Denver", "West", "Medium"),
    "SEA": ("Seattle", "West", "Medium"),
    "MIA": ("Miami", "South", "Medium"),
    "BOS": ("Boston", "Northeast", "Medium"),
}
airport_codes = list(airports.keys())

aircraft_types = ["Airbus A320", "Boeing 737", "Boeing 787", "Embraer E190", "Airbus A321"]

delay_reasons = ["Weather", "Air Traffic Control", "Airline Operations",
                 "Late Aircraft Arrival", "Security", None]  # None = no delay reason logged

weather_conditions = ["Clear", "Rain", "Snow", "Storm", "Fog", "Windy"]

cancellation_reasons = ["Weather", "Mechanical Issue", "Crew Unavailability", "Air Traffic Control"]

# ---------------------------------------------------------------------------
# 2. Build route list (avoid same origin/destination)
# ---------------------------------------------------------------------------
routes = []
for o in airport_codes:
    for d in airport_codes:
        if o != d:
            routes.append((o, d))

# approximate great-circle-ish distances (miles) - simplified static lookup
base_coords = {
    "JFK": (40.64, -73.78), "LAX": (33.94, -118.41), "ORD": (41.98, -87.90),
    "ATL": (33.64, -84.43), "DFW": (32.90, -97.04), "DEN": (39.86, -104.67),
    "SEA": (47.45, -122.31), "MIA": (25.80, -80.29), "BOS": (42.36, -71.01),
}

def haversine(o, d):
    from math import radians, sin, cos, sqrt, atan2
    lat1, lon1 = base_coords[o]
    lat2, lon2 = base_coords[d]
    R = 3958.8
    dlat, dlon = radians(lat2 - lat1), radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    return round(R * 2 * atan2(sqrt(a), sqrt(1-a)), 0)

route_distance = {(o, d): haversine(o, d) for o, d in routes}

# ---------------------------------------------------------------------------
# 3. Generate flight records
# ---------------------------------------------------------------------------
N = 12000
start_date = datetime(2025, 1, 1)
records = []

for i in range(N):
    flight_id = f"FL{100000+i}"
    airline = np.random.choice(airlines)
    origin, destination = routes[np.random.randint(len(routes))]
    distance = route_distance[(origin, destination)]
    aircraft = np.random.choice(aircraft_types)

    flight_date = start_date + timedelta(days=int(np.random.randint(0, 365)))
    sched_dep_hour = np.random.randint(5, 23)
    sched_dep_minute = np.random.choice([0, 15, 30, 45])
    scheduled_departure = flight_date.replace(hour=sched_dep_hour, minute=sched_dep_minute)

    # flight duration roughly proportional to distance (approx 500 mph + taxi time)
    flight_minutes = max(45, distance / 7.5 + np.random.randint(-10, 15))
    scheduled_arrival = scheduled_departure + timedelta(minutes=flight_minutes)

    # ---- delays (right-skewed, with some heavy outliers) ----
    is_delayed = np.random.random() < 0.28
    if is_delayed:
        dep_delay = int(np.random.exponential(scale=35))
        dep_delay = min(dep_delay, 480)  # cap extreme outlier at 8 hrs
        reason = np.random.choice(delay_reasons[:-1])
    else:
        dep_delay = np.random.choice([0, 0, 0, -5, -3, 2])  # small early/on-time noise
        reason = None

    arr_delay = dep_delay + np.random.randint(-10, 10)

    # ---- cancellations (small %) ----
    cancelled = np.random.random() < 0.018
    cancel_reason = np.random.choice(cancellation_reasons) if cancelled else None
    if cancelled:
        dep_delay, arr_delay, reason = np.nan, np.nan, None

    diverted = (not cancelled) and (np.random.random() < 0.004)

    actual_departure = scheduled_departure + timedelta(minutes=0 if cancelled or pd.isna(dep_delay) else int(dep_delay))
    actual_arrival = scheduled_arrival + timedelta(minutes=0 if cancelled or pd.isna(arr_delay) else int(arr_delay))

    seats = np.random.choice([140, 160, 180, 220, 250])
    load_factor = np.clip(np.random.normal(0.80, 0.12), 0.35, 1.0)
    passengers = 0 if cancelled else int(seats * load_factor)

    ticket_price = np.random.normal(220 + distance * 0.09, 40)
    ticket_price = max(59, round(ticket_price, 2))
    revenue = round(ticket_price * passengers, 2)
    fuel_cost = round(distance * np.random.uniform(9.5, 13.5), 2)

    satisfaction = np.random.randint(1, 6) if not cancelled else np.nan
    # introduce missingness in satisfaction survey responses (common in real surveys)
    if np.random.random() < 0.22:
        satisfaction = np.nan

    weather = np.random.choice(weather_conditions, p=[0.55, 0.18, 0.08, 0.05, 0.09, 0.05])

    records.append({
        "flight_id": flight_id,
        "flight_date": flight_date.strftime("%Y-%m-%d"),
        "airline": airline,
        "flight_number": f"{airline[:2].upper()}{np.random.randint(100,999)}",
        "origin_airport": origin,
        "destination_airport": destination,
        "distance_miles": distance,
        "aircraft_type": aircraft,
        "scheduled_departure": scheduled_departure.strftime("%Y-%m-%d %H:%M"),
        "actual_departure": None if cancelled else actual_departure.strftime("%Y-%m-%d %H:%M"),
        "scheduled_arrival": scheduled_arrival.strftime("%Y-%m-%d %H:%M"),
        "actual_arrival": None if cancelled else actual_arrival.strftime("%Y-%m-%d %H:%M"),
        "departure_delay_minutes": dep_delay,
        "arrival_delay_minutes": arr_delay,
        "delay_reason": reason,
        "cancelled": cancelled,
        "cancellation_reason": cancel_reason,
        "diverted": diverted,
        "seats_available": seats,
        "passengers": passengers,
        "ticket_price_avg": ticket_price,
        "revenue": revenue,
        "fuel_cost": fuel_cost,
        "weather_condition": weather,
        "customer_satisfaction_score": satisfaction,
    })

df = pd.DataFrame(records)

# ---------------------------------------------------------------------------
# 4. Inject realistic messiness: duplicates, inconsistent text, stray nulls
# ---------------------------------------------------------------------------
dup_rows = df.sample(150, random_state=1)
df = pd.concat([df, dup_rows], ignore_index=True)

# inconsistent casing/whitespace in a text column (common real-world issue)
mask = df.sample(frac=0.03, random_state=2).index
df.loc[mask, "airline"] = df.loc[mask, "airline"].str.upper() + "  "

# a few stray missing distances / prices (data entry gaps)
mask2 = df.sample(frac=0.01, random_state=3).index
df.loc[mask2, "distance_miles"] = np.nan
mask3 = df.sample(frac=0.008, random_state=4).index
df.loc[mask3, "ticket_price_avg"] = np.nan

# shuffle rows so duplicates aren't neatly at the bottom
df = df.sample(frac=1, random_state=5).reset_index(drop=True)

# ---------------------------------------------------------------------------
# 5. Save RAW (messy) dataset -> this is what the Python notebook will clean
# ---------------------------------------------------------------------------
df.to_csv("/home/claude/airline-operations-analytics/data/airline_flights_raw.csv", index=False)

# ---------------------------------------------------------------------------
# 6. Airport dimension table (used for SQL JOIN demonstrations)
# ---------------------------------------------------------------------------
airport_df = pd.DataFrame([
    {"airport_code": code, "city": v[0], "region": v[1], "hub_size": v[2]}
    for code, v in airports.items()
])
airport_df.to_csv("/home/claude/airline-operations-analytics/data/airports_dim.csv", index=False)

print("Raw flights dataset shape:", df.shape)
print("Airports dimension shape:", airport_df.shape)
print(df.isna().sum())
