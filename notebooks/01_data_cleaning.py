"""
01_data_cleaning.py
--------------------
Airline Operations Analytics — Data Cleaning & Feature Engineering

Steps performed (each explained inline):
    1. Load raw data
    2. Standardize text fields (casing / whitespace)
    3. Remove duplicate records
    4. Handle missing values (column-appropriate strategies)
    5. Fix data types
    6. Detect and treat outliers (IQR method)
    7. Feature engineering (delay category, weekend flag, route, month, etc.)
    8. Save cleaned dataset for SQL / Power BI / EDA use
"""

import pandas as pd
import numpy as np

pd.set_option("display.width", 120)

RAW_PATH = "/home/claude/airline-operations-analytics/data/airline_flights_raw.csv"
CLEAN_PATH = "/home/claude/airline-operations-analytics/data/airline_flights_clean.csv"

# ---------------------------------------------------------------------------
# 1. LOAD DATA
# ---------------------------------------------------------------------------
df = pd.read_csv(RAW_PATH)
print(f"Raw shape: {df.shape}")

# ---------------------------------------------------------------------------
# 2. STANDARDIZE TEXT FIELDS
# Real-world data entry often has inconsistent casing / trailing whitespace
# (e.g. "SKYLINK AIR  " vs "SkyLink Air"). We normalize to a single format.
# ---------------------------------------------------------------------------
text_cols = ["airline", "aircraft_type", "weather_condition",
             "delay_reason", "cancellation_reason"]
for col in text_cols:
    df[col] = df[col].astype(str).str.strip().str.title()
    df[col] = df[col].replace({"Nan": np.nan})

# ---------------------------------------------------------------------------
# 3. REMOVE DUPLICATES
# We generated intentional duplicate rows to simulate a real extraction bug
# (e.g. a scheduled job that reran and double-inserted records).
# ---------------------------------------------------------------------------
before = len(df)
df = df.drop_duplicates(subset=["flight_id"], keep="first")
print(f"Removed {before - len(df)} duplicate rows based on flight_id")

# ---------------------------------------------------------------------------
# 4. HANDLE MISSING VALUES
# Strategy is column-specific — never blanket-fill everything the same way:
#   - distance_miles / ticket_price_avg: numeric, missing at random ->
#       impute with the median of the same route / overall median (robust to skew)
#   - delay_reason / cancellation_reason: missing simply means "not applicable"
#       (flight was on-time / not cancelled) -> fill with explicit label
#   - customer_satisfaction_score: missing means the passenger didn't respond
#       to the survey -> keep as NaN for satisfaction analysis (do NOT impute
#       a fake score - that would bias the insight), but flag it as its own
#       category for completion-rate reporting
# ---------------------------------------------------------------------------

# 4a. distance_miles — impute using the median distance for that exact route
df["distance_miles"] = df.groupby(
    ["origin_airport", "destination_airport"]
)["distance_miles"].transform(lambda x: x.fillna(x.median()))
# fallback for any route with all-NaN (unlikely, but defensive coding)
df["distance_miles"] = df["distance_miles"].fillna(df["distance_miles"].median())

# 4b. ticket_price_avg — impute with the median price for that airline
df["ticket_price_avg"] = df.groupby("airline")["ticket_price_avg"].transform(
    lambda x: x.fillna(x.median())
)

# 4c. delay_reason -> explicit "No Delay" label where flight wasn't delayed
df["delay_reason"] = df["delay_reason"].fillna("No Delay")

# 4d. cancellation_reason -> explicit label for non-cancelled flights
df["cancellation_reason"] = df["cancellation_reason"].fillna("Not Cancelled")

# 4e. delay minutes for cancelled flights: leave as NaN (delay is undefined
#     for a flight that never departed) — but create a separate boolean flag
df["had_valid_delay_data"] = df["departure_delay_minutes"].notna()

# 4f. customer_satisfaction_score: leave missing as NaN, add a survey-response flag
df["survey_responded"] = df["customer_satisfaction_score"].notna()

print("\nMissing values after cleaning:")
print(df.isna().sum()[df.isna().sum() > 0])

# ---------------------------------------------------------------------------
# 5. FIX DATA TYPES
# ---------------------------------------------------------------------------
df["flight_date"] = pd.to_datetime(df["flight_date"])
df["scheduled_departure"] = pd.to_datetime(df["scheduled_departure"])
df["actual_departure"] = pd.to_datetime(df["actual_departure"])
df["scheduled_arrival"] = pd.to_datetime(df["scheduled_arrival"])
df["actual_arrival"] = pd.to_datetime(df["actual_arrival"])
df["cancelled"] = df["cancelled"].astype(bool)
df["diverted"] = df["diverted"].astype(bool)
df["seats_available"] = df["seats_available"].astype(int)
df["passengers"] = df["passengers"].astype(int)

# ---------------------------------------------------------------------------
# 6. OUTLIER DETECTION (IQR method) — applied to departure_delay_minutes
# We DON'T silently drop outliers here (a 300-minute delay is a real,
# important business event, not noise). Instead we FLAG them for visibility,
# and cap only clearly impossible data-entry errors (negative distances etc.)
# ---------------------------------------------------------------------------
valid_delays = df.loc[df["had_valid_delay_data"], "departure_delay_minutes"]
Q1, Q3 = valid_delays.quantile(0.25), valid_delays.quantile(0.75)
IQR = Q3 - Q1
lower_bound, upper_bound = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR

df["is_delay_outlier"] = False
df.loc[df["had_valid_delay_data"], "is_delay_outlier"] = (
    (df.loc[df["had_valid_delay_data"], "departure_delay_minutes"] < lower_bound) |
    (df.loc[df["had_valid_delay_data"], "departure_delay_minutes"] > upper_bound)
)
n_outliers = df["is_delay_outlier"].sum()
print(f"\nOutlier bounds (IQR method): [{lower_bound:.1f}, {upper_bound:.1f}] minutes")
print(f"Flagged {n_outliers} flights ({n_outliers/len(df)*100:.1f}%) as delay outliers"
      f" — kept in dataset, flagged for transparency, not deleted.")

# Defensive fix: distance/price can never be negative or zero (impossible values)
df.loc[df["distance_miles"] <= 0, "distance_miles"] = np.nan
df["distance_miles"] = df["distance_miles"].fillna(df["distance_miles"].median())

# ---------------------------------------------------------------------------
# 7. FEATURE ENGINEERING
# ---------------------------------------------------------------------------

# 7a. Delay category (mirrors the SQL CASE WHEN logic — kept consistent
#     across SQL / Python / Power BI for a single source of truth)
def categorize_delay(row):
    if row["cancelled"]:
        return "Cancelled"
    d = row["departure_delay_minutes"]
    if pd.isna(d):
        return "Unknown"
    if d <= 0:
        return "On-Time / Early"
    elif d <= 15:
        return "Minor Delay"
    elif d <= 60:
        return "Moderate Delay"
    else:
        return "Severe Delay"

df["delay_category"] = df.apply(categorize_delay, axis=1)

# 7b. Route (combined origin-destination for route-level grouping)
df["route"] = df["origin_airport"] + "-" + df["destination_airport"]

# 7c. Calendar features
df["month"] = df["flight_date"].dt.month
df["month_name"] = df["flight_date"].dt.month_name()
df["day_of_week"] = df["flight_date"].dt.day_name()
df["is_weekend"] = df["flight_date"].dt.dayofweek >= 5
df["quarter"] = df["flight_date"].dt.quarter

# 7d. Load factor (capacity utilization) — key airline KPI
df["load_factor"] = (df["passengers"] / df["seats_available"]).round(3)

# 7e. Revenue per available seat mile (RASM) — a real industry KPI
df["rasm"] = (df["revenue"] / (df["seats_available"] * df["distance_miles"])).round(4)

# 7f. Profitability proxy (revenue - fuel cost; a simplified margin indicator)
df["operating_margin"] = df["revenue"] - df["fuel_cost"]

# 7g. On-time performance flag (industry standard: <15 min late = "on-time")
df["is_on_time"] = (df["departure_delay_minutes"].fillna(0) <= 15) & (~df["cancelled"])

print("\nEngineered columns added:",
      ["delay_category", "route", "month", "month_name", "day_of_week",
       "is_weekend", "quarter", "load_factor", "rasm", "operating_margin", "is_on_time"])

# ---------------------------------------------------------------------------
# 8. SAVE CLEANED DATASET
# ---------------------------------------------------------------------------
df.to_csv(CLEAN_PATH, index=False)
print(f"\nCleaned dataset saved: {CLEAN_PATH}")
print(f"Final shape: {df.shape}")
