"""
02_eda_visualizations.py
-------------------------
Airline Operations Analytics — Exploratory Data Analysis & Visualizations

Produces:
  - Matplotlib PNGs (static, for README / reports)
  - Plotly HTML (interactive, for portfolio web embedding)
All saved to /images
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Plotly is optional: this script runs fully with just matplotlib (used in
# this sandboxed environment). On a normal machine with internet access,
# `pip install plotly` and the interactive HTML charts below will also be
# generated for the portfolio / web embedding.
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("[info] plotly not installed — skipping interactive HTML charts. "
          "Run `pip install plotly` to enable them.")

plt.style.use("seaborn-v0_8-whitegrid")
IMG = "/home/claude/airline-operations-analytics/images"

df = pd.read_csv(
    "/home/claude/airline-operations-analytics/data/airline_flights_clean.csv",
    parse_dates=["flight_date", "scheduled_departure", "actual_departure",
                 "scheduled_arrival", "actual_arrival"]
)

not_cancelled = df[~df["cancelled"]]

# ============================================================================
# 1. LINE CHART — Monthly revenue trend
# Insight: reveals seasonality in demand/revenue across the year, informing
# staffing and pricing strategy.
# ============================================================================
monthly = not_cancelled.groupby(df["flight_date"].dt.to_period("M")).agg(
    revenue=("revenue", "sum"),
    flights=("flight_id", "count")
).reset_index()
monthly["flight_date"] = monthly["flight_date"].astype(str)

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(monthly["flight_date"], monthly["revenue"] / 1e6, marker="o", color="#1f4e79", linewidth=2)
ax.set_title("Monthly Revenue Trend — 2025", fontsize=14, fontweight="bold")
ax.set_ylabel("Revenue ($ Millions)")
ax.set_xlabel("Month")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f"{IMG}/01_monthly_revenue_trend.png", dpi=150)
plt.close()

# Interactive Plotly version
if PLOTLY_AVAILABLE:
    fig2 = px.line(monthly, x="flight_date", y="revenue", markers=True,
                   title="Monthly Revenue Trend — 2025",
                   labels={"flight_date": "Month", "revenue": "Revenue ($)"})
    fig2.write_html(f"{IMG}/01_monthly_revenue_trend.html")

# ============================================================================
# 2. BAR CHART — Average delay by airline
# Insight: ranks airlines by operational reliability, a key stakeholder ask.
# ============================================================================
airline_delay = not_cancelled.groupby("airline")["departure_delay_minutes"].mean().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(airline_delay.index, airline_delay.values, color="#c0392b")
ax.set_title("Average Departure Delay by Airline", fontsize=14, fontweight="bold")
ax.set_ylabel("Avg Delay (minutes)")
plt.xticks(rotation=20)
plt.tight_layout()
plt.savefig(f"{IMG}/02_avg_delay_by_airline.png", dpi=150)
plt.close()

if PLOTLY_AVAILABLE:
    fig2 = px.bar(airline_delay.reset_index(), x="airline", y="departure_delay_minutes",
                  title="Average Departure Delay by Airline",
                  labels={"departure_delay_minutes": "Avg Delay (min)", "airline": "Airline"},
                  color="departure_delay_minutes", color_continuous_scale="Reds")
    fig2.write_html(f"{IMG}/02_avg_delay_by_airline.html")

# ============================================================================
# 3. HISTOGRAM — Distribution of departure delays
# Insight: shows the right-skewed nature of delays (most flights on-time,
# long tail of severe delays) — informs why AVERAGE alone is misleading.
# ============================================================================
delay_data = not_cancelled["departure_delay_minutes"].dropna()
delay_data = delay_data[delay_data <= 180]  # trim extreme tail for readability

fig, ax = plt.subplots(figsize=(10, 5))
ax.hist(delay_data, bins=40, color="#2980b9", edgecolor="white")
ax.set_title("Distribution of Departure Delays", fontsize=14, fontweight="bold")
ax.set_xlabel("Delay (minutes)")
ax.set_ylabel("Number of Flights")
plt.tight_layout()
plt.savefig(f"{IMG}/03_delay_distribution_histogram.png", dpi=150)
plt.close()

# ============================================================================
# 4. BOX PLOT — Delay spread by aircraft type
# Insight: compares variability (not just average) in delays across fleet
# types — useful for fleet-investment / maintenance-scheduling decisions.
# ============================================================================
fig, ax = plt.subplots(figsize=(10, 5))
aircraft_groups = [not_cancelled[not_cancelled["aircraft_type"] == a]["departure_delay_minutes"].dropna().clip(upper=150)
                   for a in not_cancelled["aircraft_type"].unique()]
ax.boxplot(aircraft_groups, labels=not_cancelled["aircraft_type"].unique(), showfliers=True)
ax.set_title("Departure Delay Spread by Aircraft Type", fontsize=14, fontweight="bold")
ax.set_ylabel("Delay (minutes)")
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig(f"{IMG}/04_delay_boxplot_by_aircraft.png", dpi=150)
plt.close()

# ============================================================================
# 5. HEATMAP — Avg delay by Day of Week x Month
# Insight: pinpoints exactly WHEN operational problems cluster (e.g. holiday
# travel weeks, specific weekdays) for targeted staffing/resourcing.
# ============================================================================
pivot = not_cancelled.pivot_table(
    index="day_of_week", columns="month_name", values="departure_delay_minutes", aggfunc="mean"
)
day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
month_order = ["January","February","March","April","May","June","July","August",
               "September","October","November","December"]
pivot = pivot.reindex(index=day_order, columns=month_order)

fig, ax = plt.subplots(figsize=(12, 6))
im = ax.imshow(pivot.values, cmap="YlOrRd", aspect="auto")
ax.set_xticks(range(len(month_order)))
ax.set_xticklabels(month_order, rotation=45, ha="right")
ax.set_yticks(range(len(day_order)))
ax.set_yticklabels(day_order)
ax.set_title("Average Departure Delay: Day of Week x Month", fontsize=14, fontweight="bold")
fig.colorbar(im, ax=ax, label="Avg Delay (minutes)")
plt.tight_layout()
plt.savefig(f"{IMG}/05_delay_heatmap_day_month.png", dpi=150)
plt.close()

if PLOTLY_AVAILABLE:
    fig2 = px.imshow(pivot, color_continuous_scale="YlOrRd",
                      title="Average Departure Delay: Day of Week x Month",
                      labels=dict(color="Avg Delay (min)"))
    fig2.write_html(f"{IMG}/05_delay_heatmap_day_month.html")

# ============================================================================
# 6. PIE CHART — Cancellation reasons share
# Insight: only appropriate here because cancellations are a small, discrete
# set of categories that sum to a meaningful whole (100% of cancellations).
# ============================================================================
cancelled_df = df[df["cancelled"]]
reason_counts = cancelled_df["cancellation_reason"].value_counts()

fig, ax = plt.subplots(figsize=(7, 7))
ax.pie(reason_counts.values, labels=reason_counts.index, autopct="%1.1f%%",
       colors=["#e74c3c", "#e67e22", "#f1c40f", "#3498db"], startangle=90)
ax.set_title("Share of Flight Cancellations by Reason", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(f"{IMG}/06_cancellation_reasons_pie.png", dpi=150)
plt.close()

# ============================================================================
# 7. SCATTER PLOT — Distance vs. Ticket Price (with load factor as color)
# Insight: validates pricing strategy (does price scale sensibly with
# distance?) and reveals whether high-demand (high load factor) routes are
# being priced accordingly.
# ============================================================================
sample = not_cancelled.sample(min(2000, len(not_cancelled)), random_state=1)

fig, ax = plt.subplots(figsize=(10, 6))
sc = ax.scatter(sample["distance_miles"], sample["ticket_price_avg"],
                 c=sample["load_factor"], cmap="viridis", alpha=0.6, s=20)
ax.set_title("Ticket Price vs. Flight Distance (colored by Load Factor)", fontsize=14, fontweight="bold")
ax.set_xlabel("Distance (miles)")
ax.set_ylabel("Avg Ticket Price ($)")
fig.colorbar(sc, ax=ax, label="Load Factor")
plt.tight_layout()
plt.savefig(f"{IMG}/07_price_vs_distance_scatter.png", dpi=150)
plt.close()

if PLOTLY_AVAILABLE:
    fig2 = px.scatter(sample, x="distance_miles", y="ticket_price_avg", color="load_factor",
                        title="Ticket Price vs. Flight Distance (colored by Load Factor)",
                        labels={"distance_miles": "Distance (miles)", "ticket_price_avg": "Avg Ticket Price ($)"},
                        color_continuous_scale="Viridis", opacity=0.6)
    fig2.write_html(f"{IMG}/07_price_vs_distance_scatter.html")

# ============================================================================
# 8. BAR CHART — Top 10 routes by revenue
# ============================================================================
top_routes = not_cancelled.groupby("route")["revenue"].sum().sort_values(ascending=False).head(10)

fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(top_routes.index[::-1], top_routes.values[::-1] / 1e6, color="#27ae60")
ax.set_title("Top 10 Routes by Total Revenue", fontsize=14, fontweight="bold")
ax.set_xlabel("Revenue ($ Millions)")
plt.tight_layout()
plt.savefig(f"{IMG}/08_top10_routes_revenue.png", dpi=150)
plt.close()

# ============================================================================
# 9. Load factor by region (interactive plotly bar - for Power BI parity)
# ============================================================================
airports_dim = pd.read_csv("/home/claude/airline-operations-analytics/data/airports_dim.csv")
merged = not_cancelled.merge(airports_dim, left_on="origin_airport", right_on="airport_code")
region_lf = merged.groupby("region")["load_factor"].mean().sort_values(ascending=False).reset_index()

if PLOTLY_AVAILABLE:
    fig2 = px.bar(region_lf, x="region", y="load_factor", title="Average Load Factor by Region",
                   labels={"load_factor": "Avg Load Factor", "region": "Region"},
                   color="load_factor", color_continuous_scale="Blues")
    fig2.write_html(f"{IMG}/09_load_factor_by_region.html")

print("All visualizations generated successfully in /images")
print("\nQuick summary stats:")
print(f"Total flights (incl. cancelled): {len(df):,}")
print(f"Cancelled: {df['cancelled'].sum():,} ({df['cancelled'].mean()*100:.1f}%)")
print(f"On-time performance: {not_cancelled['is_on_time'].mean()*100:.1f}%")
print(f"Total revenue: ${not_cancelled['revenue'].sum():,.0f}")
print(f"Avg load factor: {not_cancelled['load_factor'].mean()*100:.1f}%")
