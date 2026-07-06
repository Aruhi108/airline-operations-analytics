# ✈️ Airline Operations Analytics

**An end-to-end data analytics project analyzing flight delays, cancellations, revenue, and customer satisfaction for a multi-airline operations network — built to mirror a real analyst engagement, from raw messy data to an executive-ready Power BI dashboard.**

---

## 📌 Project Overview

A regional airline operations group (6 airlines, 9 major U.S. airports, 12 months of flight data) wants to understand **why on-time performance has stagnated and where revenue and reliability opportunities are being missed.** This project delivers a complete analytics workflow — SQL analysis, Python cleaning/EDA, visualizations, and a Power BI dashboard — that a stakeholder could review and act on immediately.

**Dataset:** 12,000 simulated flight records (Jan–Dec 2025), intentionally generated with real-world messiness (duplicates, missing values, inconsistent text formatting) to demonstrate genuine data-cleaning skill.

---

## 🎯 Business Problem

Airline operations leadership has flagged three recurring issues in quarterly reviews:

1. On-time performance has been inconsistent across airlines and routes, but no one has quantified *where* the problem concentrates.
2. Revenue growth has plateaued, and it's unclear which routes, regions, or aircraft types are under- or over-performing.
3. Customer satisfaction survey data exists but has never been systematically connected to operational metrics (delays, cancellations, aircraft type).

### Business Objectives
- Quantify on-time performance and cancellation drivers across airlines, routes, and time.
- Identify the highest-revenue and highest-risk routes/regions.
- Evaluate fleet (aircraft type) utilization and profitability.
- Determine whether customer satisfaction is actually linked to operational reliability.
- Package findings into a dashboard operations and commercial teams can use weekly.

### Key Stakeholder Questions
- Which airline and which routes have the worst on-time performance?
- What are the top drivers of cancellations, and are they controllable (mechanical/crew) or not (weather)?
- Which regions and routes generate the most revenue, and where is capacity under-utilized?
- Does flight delay actually hurt customer satisfaction scores, or are other factors driving dissatisfaction?
- What operational and commercial actions should we prioritize next quarter?

---

## 📊 Dataset

| File | Description |
|---|---|
| `data/airline_flights_raw.csv` | Raw, uncleaned extract — 12,150 rows, includes duplicates & missing values (simulates a real source-system export) |
| `data/airline_flights_clean.csv` | Cleaned, feature-engineered dataset — 12,000 rows, 39 columns — used for all SQL/Python/Power BI analysis |
| `data/airports_dim.csv` | Airport dimension table (9 airports: code, city, region, hub size) used for SQL joins |

### Column Dictionary (cleaned dataset)

| Column | Type | Description |
|---|---|---|
| `flight_id` | string | Unique flight record identifier |
| `flight_date` | date | Date of the flight |
| `airline` | string | Operating airline (6 carriers) |
| `flight_number` | string | Airline flight number |
| `origin_airport` / `destination_airport` | string | 3-letter airport codes |
| `distance_miles` | float | Route distance |
| `aircraft_type` | string | Aircraft model operating the flight |
| `scheduled_departure` / `actual_departure` | datetime | Scheduled vs. actual departure |
| `scheduled_arrival` / `actual_arrival` | datetime | Scheduled vs. actual arrival |
| `departure_delay_minutes` / `arrival_delay_minutes` | float | Delay in minutes (negative = early) |
| `delay_reason` | string | Cause of delay (or "No Delay") |
| `cancelled` / `cancellation_reason` | bool / string | Cancellation flag and cause |
| `diverted` | bool | Whether the flight was diverted |
| `seats_available` / `passengers` | int | Capacity and actual passengers boarded |
| `ticket_price_avg` | float | Average ticket price for the flight |
| `revenue` | float | Total flight revenue (price × passengers) |
| `fuel_cost` | float | Estimated fuel cost for the flight |
| `weather_condition` | string | Weather at departure |
| `customer_satisfaction_score` | float (1–5) | Post-flight survey score (nullable — not all passengers respond) |
| `delay_category` | string | Engineered: On-Time / Minor / Moderate / Severe / Cancelled |
| `route`, `month`, `month_name`, `day_of_week`, `is_weekend`, `quarter` | — | Engineered calendar/route features |
| `load_factor` | float | Passengers ÷ seats available (capacity utilization) |
| `rasm` | float | Revenue per Available Seat Mile (industry KPI) |
| `operating_margin` | float | Revenue − fuel cost (simplified margin proxy) |
| `is_on_time` | bool | True if delay ≤ 15 minutes and not cancelled |
| `had_valid_delay_data`, `is_delay_outlier`, `survey_responded` | bool | Data-quality tracking flags created during cleaning |

**Size:** 12,000 rows × 39 columns (post-cleaning) · **Grain:** one row = one scheduled flight

---

## 🛠️ Tools Used
- **SQL** (PostgreSQL syntax) — querying, joins, CTEs, window functions
- **Python** (Pandas, NumPy) — data cleaning, feature engineering, EDA
- **Matplotlib & Plotly** — static and interactive visualizations
- **Power BI** — executive dashboard design
- **Git/GitHub** — version control and portfolio hosting

---

## 🔄 Workflow

```
Raw CSV (messy)  →  Python Cleaning & Feature Engineering  →  Cleaned CSV
                                    │
                 ┌──────────────────┼───────────────────┐
                 ▼                  ▼                   ▼
           SQL Analysis        EDA & Charts        Power BI Dashboard
        (business queries)   (matplotlib/plotly)   (interactive report)
                 │                  │                   │
                 └──────────────────┴───────────────────┘
                                    ▼
                     Business Insights & Recommendations
```

1. **`notebooks/00_generate_dataset.py`** — generates the realistic raw dataset (simulates a source-system export)
2. **`notebooks/01_data_cleaning.py`** — cleans, standardizes, and feature-engineers the data
3. **`notebooks/02_eda_visualizations.py`** — runs EDA and produces all charts in `/images`
4. **`sql/01_schema.sql`** & **`sql/02_analysis_queries.sql`** — schema + 10 business SQL queries
5. **`dashboard/power_bi_dashboard_design.md`** — full Power BI dashboard specification
6. **`reports/business_insights_and_recommendations.md`** — findings and recommendations
7. **`reports/interview_prep.md`** — 40 interview Q&A for presenting this project

---

## 📈 Results (Headline KPIs)

| Metric | Value |
|---|---|
| Total flights analyzed | 12,000 |
| Overall on-time performance (≤15 min) | **82.5%** |
| Cancellation rate | **1.8%** (211 flights) |
| Total revenue (non-cancelled flights) | **$614.0M** |
| Average load factor (capacity utilization) | **79.6%** |
| Average customer satisfaction | **3.0 / 5** |
| Survey response rate | **76.4%** |

Full breakdown of findings: see [`reports/business_insights_and_recommendations.md`](reports/business_insights_and_recommendations.md).

---

## 🖥️ Dashboard Preview

The Power BI dashboard (design spec in `/dashboard`) includes KPI cards, monthly trends, regional and category breakdowns, top routes, and interactive slicers. Static chart previews generated from this analysis are in `/images`:

- `01_monthly_revenue_trend.png` — revenue seasonality
- `02_avg_delay_by_airline.png` — airline reliability ranking
- `05_delay_heatmap_day_month.png` — delay hot-spots by day/month
- `08_top10_routes_revenue.png` — top revenue-generating routes

*(Interactive `.html` Plotly versions are also generated when `plotly` is installed — see Installation below.)*

---

## ⚙️ Installation & Setup

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/airline-operations-analytics.git
cd airline-operations-analytics

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the pipeline in order
python notebooks/00_generate_dataset.py     # generates raw data
python notebooks/01_data_cleaning.py        # cleans & engineers features
python notebooks/02_eda_visualizations.py   # generates charts into /images

# 5. Load sql/01_schema.sql and sql/02_analysis_queries.sql into
#    PostgreSQL (or adapt lightly for MySQL/SQLite) to run the SQL analysis.

# 6. Open dashboard/power_bi_dashboard_design.md for the Power BI build spec,
#    or import data/airline_flights_clean.csv directly into Power BI Desktop.
```

---

## 🌐 Making It Public: Power BI, Tableau & a Live Streamlit Dashboard

This project is set up three different ways so you can pick what fits your resume/portfolio best — and the Streamlit route gives you an actual public **link**, not just a file.

### Option 1 — Power BI Desktop (Windows, free)
1. Download **Power BI Desktop** from Microsoft.
2. **Get Data → More → Database → SQLite database** → point it to `data/airline_ops.db` (already built and included — tables: `flights`, `airports`).
   - Alternatively: **Get Data → Text/CSV** → `data/airline_flights_clean.csv`.
3. Build visuals following `dashboard/power_bi_dashboard_design.md` — it lists every chart, field, and the business reason for each.
4. **Publish** (Home → Publish) to Power BI Service if you have a free Microsoft/Power BI account — this gives you a shareable report link.

### Option 2 — Tableau Public (free, no login needed for viewers)
1. Download **Tableau Public**.
2. Connect to a CSV — use the ready-made summary exports in `reports/exports/`:
   - `monthly_revenue.csv`, `top_routes.csv`, `airline_summary.csv`, `region_summary.csv`
   - or connect directly to `data/airline_flights_clean.csv` for full flight-level detail.
3. Build 4–5 sheets (bar charts, a map using region/city, a KPI text card), then combine into one **Dashboard** tab.
4. **Publish to Tableau Public** — you'll get a public URL you can drop straight into your resume/LinkedIn, no download required for anyone viewing it.

### Option 3 — Live Streamlit Dashboard (free public link, no server needed)
This is the one that gets you an actual **clickable URL** people can open immediately.

1. Push this whole folder to a **public GitHub repo** (see steps below if you haven't already).
2. Go to **[share.streamlit.io](https://share.streamlit.io)** and sign in with your GitHub account.
3. Click **New app** → select your repo → set the main file path to **`app.py`** → Deploy.
4. In a minute or two you'll get a public link like:
   `https://your-username-airline-operations-analytics.streamlit.app`
5. That link is what goes on your resume/LinkedIn/GitHub README — anyone can open it and interact with the real dashboard (filters, KPI cards, charts), no install needed on their end.

`app.py` (included in this project) is a working Streamlit app already built against `data/airline_flights_clean.csv` and `data/airports_dim.csv` — it has KPI cards, filters (airline/region/date), a monthly revenue trend, delay-category breakdown, airline reliability ranking, regional revenue, top routes, and a delay heatmap. Run it locally first to confirm it works before deploying:
```bash
pip install -r requirements.txt
streamlit run app.py
```

### Getting the project onto GitHub (needed for Option 3, optional for 1 & 2)
```bash
cd airline-operations-analytics
git init
git add .
git commit -m "Initial commit: end-to-end airline analytics project"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/airline-operations-analytics.git
git push -u origin main
```
Or upload the folder contents via the GitHub website: **New repository → uploading an existing file** → drag in the unzipped folder.


- Connect to a live flight-status API for real-time on-time performance tracking.
- Add a predictive model (e.g., logistic regression / gradient boosting) to forecast delay probability per flight.
- Incorporate weather API data instead of simulated weather categories.
- Build a customer-satisfaction driver analysis (regression / feature importance) to identify what *actually* moves satisfaction scores.
- Automate the pipeline with Airflow and schedule nightly refreshes into Power BI via a Postgres backend.

---

## 📁 Project Structure

```
airline-operations-analytics/
│
├── data/
│   ├── airline_flights_raw.csv
│   ├── airline_flights_clean.csv
│   ├── airports_dim.csv
│   └── airline_ops.db          # SQLite version — for Power BI / Tableau / app.py
├── sql/
│   ├── 01_schema.sql
│   └── 02_analysis_queries.sql
├── notebooks/
│   ├── 00_generate_dataset.py
│   ├── 01_data_cleaning.py
│   ├── 02_eda_visualizations.py
│   └── 03_build_sqlite_db.py
├── dashboard/
│   └── power_bi_dashboard_design.md
├── images/
│   ├── 01_monthly_revenue_trend.png
│   ├── 02_avg_delay_by_airline.png
│   ├── 03_delay_distribution_histogram.png
│   ├── 04_delay_boxplot_by_aircraft.png
│   ├── 05_delay_heatmap_day_month.png
│   ├── 06_cancellation_reasons_pie.png
│   ├── 07_price_vs_distance_scatter.png
│   └── 08_top10_routes_revenue.png
├── reports/
│   ├── business_insights_and_recommendations.md
│   ├── resume_and_linkedin_content.md
│   ├── interview_prep.md
│   └── exports/                 # ready-made CSVs for Tableau Public
│       ├── monthly_revenue.csv
│       ├── top_routes.csv
│       ├── airline_summary.csv
│       └── region_summary.csv
├── app.py                       # Streamlit dashboard — deployable for a live public link
├── README.md
├── requirements.txt
├── .gitignore
└── LICENSE
```

---

## 👤 Author
Prepared as a portfolio project by a Data Analyst, designed to demonstrate SQL, Python, and BI dashboard skills across a realistic airline-operations business case.
