"""
app.py
-------
Airline Operations Analytics — Streamlit Dashboard

This is the file that, once pushed to GitHub, gets deployed for free on
Streamlit Community Cloud (share.streamlit.io) to give you a public,
shareable link for your resume/LinkedIn — no server or hosting cost.

Run locally with:
    pip install -r requirements.txt
    streamlit run app.py
"""

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Airline Operations Analytics", layout="wide", page_icon="✈️")

# ---------------------------------------------------------------------------
# Load data (cached so it only re-reads the CSV once per session)
# ---------------------------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/airline_flights_clean.csv", parse_dates=["flight_date"])
    airports = pd.read_csv("data/airports_dim.csv")
    df = df.merge(airports, left_on="origin_airport", right_on="airport_code", how="left")
    return df

df = load_data()

st.title("✈️ Airline Operations Analytics Dashboard")
st.caption("End-to-end analytics project — SQL + Python + Streamlit — 12,000 flights, 6 airlines, 9 airports, 2025")

# ---------------------------------------------------------------------------
# Sidebar filters (mirrors the Power BI slicers)
# ---------------------------------------------------------------------------
st.sidebar.header("Filters")

airlines = st.sidebar.multiselect(
    "Airline", options=sorted(df["airline"].unique()), default=sorted(df["airline"].unique())
)
regions = st.sidebar.multiselect(
    "Region", options=sorted(df["region"].dropna().unique()), default=sorted(df["region"].dropna().unique())
)
date_range = st.sidebar.date_input(
    "Date range",
    value=(df["flight_date"].min(), df["flight_date"].max()),
    min_value=df["flight_date"].min(),
    max_value=df["flight_date"].max(),
)
show_cancelled = st.sidebar.checkbox("Include cancelled flights in KPI counts", value=False)

# Apply filters
mask = (
    df["airline"].isin(airlines)
    & df["region"].isin(regions)
    & (df["flight_date"] >= pd.to_datetime(date_range[0]))
    & (df["flight_date"] <= pd.to_datetime(date_range[1]))
)
filtered = df[mask]
active = filtered if show_cancelled else filtered[~filtered["cancelled"]]

# ---------------------------------------------------------------------------
# KPI cards
# ---------------------------------------------------------------------------
col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Total Flights", f"{len(filtered):,}")
col2.metric("On-Time %", f"{active['is_on_time'].mean()*100:.1f}%")
col3.metric("Cancellation Rate", f"{filtered['cancelled'].mean()*100:.1f}%")
col4.metric("Total Revenue", f"${active['revenue'].sum()/1e6:.1f}M")
col5.metric("Avg Load Factor", f"{active['load_factor'].mean()*100:.1f}%")
col6.metric("Avg Satisfaction", f"{active['customer_satisfaction_score'].mean():.2f} / 5")

st.divider()

# ---------------------------------------------------------------------------
# Row 1: Monthly revenue trend + Delay category breakdown
# ---------------------------------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    st.subheader("Monthly Revenue Trend")
    monthly = active.groupby(active["flight_date"].dt.to_period("M"))["revenue"].sum()
    monthly.index = monthly.index.astype(str)
    st.line_chart(monthly)

with c2:
    st.subheader("Delay Category Breakdown")
    cat_counts = filtered["delay_category"].value_counts()
    st.bar_chart(cat_counts)

# ---------------------------------------------------------------------------
# Row 2: Airline reliability + Regional revenue
# ---------------------------------------------------------------------------
c3, c4 = st.columns(2)

with c3:
    st.subheader("Average Departure Delay by Airline")
    airline_delay = active.groupby("airline")["departure_delay_minutes"].mean().sort_values(ascending=False)
    st.bar_chart(airline_delay)

with c4:
    st.subheader("Revenue by Region")
    region_rev = active.groupby("region")["revenue"].sum().sort_values(ascending=False)
    st.bar_chart(region_rev)

# ---------------------------------------------------------------------------
# Row 3: Top routes + Delay heatmap (day of week x month)
# ---------------------------------------------------------------------------
st.subheader("Top 10 Routes by Revenue")
top_routes = active.groupby("route")["revenue"].sum().sort_values(ascending=False).head(10)
st.bar_chart(top_routes)

st.subheader("Average Delay: Day of Week x Month")
day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
month_order = ["January","February","March","April","May","June","July","August",
               "September","October","November","December"]
pivot = active.pivot_table(index="day_of_week", columns="month_name",
                             values="departure_delay_minutes", aggfunc="mean")
pivot = pivot.reindex(index=day_order, columns=[m for m in month_order if m in pivot.columns])

fig, ax = plt.subplots(figsize=(12, 4))
im = ax.imshow(pivot.values, cmap="YlOrRd", aspect="auto")
ax.set_xticks(range(len(pivot.columns))); ax.set_xticklabels(pivot.columns, rotation=45, ha="right")
ax.set_yticks(range(len(pivot.index))); ax.set_yticklabels(pivot.index)
fig.colorbar(im, ax=ax, label="Avg Delay (min)")
st.pyplot(fig)

# ---------------------------------------------------------------------------
# Row 4: Raw data explorer
# ---------------------------------------------------------------------------
with st.expander("🔎 Explore the underlying flight data"):
    st.dataframe(
        filtered[["flight_id", "flight_date", "airline", "route", "delay_category",
                  "revenue", "load_factor", "customer_satisfaction_score"]].sort_values("flight_date"),
        use_container_width=True,
    )

st.caption("Built with Python, Pandas, and Streamlit · Data cleaned and feature-engineered per notebooks/01_data_cleaning.py")
