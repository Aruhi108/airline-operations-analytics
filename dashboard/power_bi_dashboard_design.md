# Power BI Dashboard Design Specification
## Airline Operations Analytics — Executive Dashboard

**Data source:** `data/airline_flights_clean.csv` (+ `airports_dim.csv` joined on `origin_airport` / `destination_airport`)
**Refresh cadence (recommended):** Weekly, or nightly if connected to a live operational database.
**Pages:** 1 Overview page + 1 Drill-down "Route & Delay Detail" page.

---

## Page 1: Executive Overview

### 1. KPI Cards (top row, 6 cards)
| Card | Measure | Purpose |
|---|---|---|
| Total Flights | `COUNT(flight_id)` | Baseline volume context for every other metric |
| On-Time Performance % | `AVG(is_on_time)` | Headline operational health metric leadership tracks weekly |
| Cancellation Rate % | `AVG(cancelled)` | Flags service reliability risk at a glance |
| Total Revenue | `SUM(revenue)` | Core commercial KPI |
| Avg Load Factor | `AVG(load_factor)` | Capacity utilization efficiency |
| Avg Customer Satisfaction | `AVG(customer_satisfaction_score)` | Connects operations to customer experience |

*Purpose:* gives an executive the "state of the business" in under 5 seconds before drilling into anything else.

### 2. Monthly Trends (line/area chart)
- **X-axis:** Month (flight_date hierarchy)
- **Y-axis (dual):** Total Revenue (line) + On-Time % (secondary axis line)
- **Purpose:** shows whether revenue and reliability move together or diverge — e.g., a month with revenue growth but declining on-time % signals capacity strain.

### 3. Category Analysis — Delay Category Breakdown (stacked bar or donut)
- **Dimension:** `delay_category` (On-Time/Minor/Moderate/Severe/Cancelled)
- **Measure:** Flight count, % of total
- **Purpose:** moves the conversation beyond "average delay" to the actual distribution of outcomes — critical since delays are right-skewed (see EDA histogram).

### 4. Regional Analysis (map or bar chart)
- **Dimension:** `region` (from airports_dim, joined on origin_airport)
- **Measure:** Revenue, Flight Count, Avg Delay
- **Purpose:** identifies which regions are commercially strongest and where reliability issues concentrate geographically.

### 5. Customer Analysis (scatter or combo chart)
- **X-axis:** `delay_category` · **Y-axis:** Avg `customer_satisfaction_score` · **Size:** flight volume
- **Purpose:** directly tests (and visually communicates) whether delay severity is actually moving satisfaction — a key finding of this project is that it largely isn't, which is itself a valuable, decision-relevant insight.

### 6. Filters / Slicers (side panel)
- Date range (flight_date)
- Airline (multi-select)
- Region
- Aircraft type
- Delay category
- Cancelled flag (Yes/No)

*Purpose:* lets any stakeholder — ops manager, regional lead, fleet planner — self-serve their own slice without needing a new report built for them.

### 7. Top Products (Top Routes) — horizontal bar chart
- **Dimension:** `route` (origin-destination)
- **Measure:** Revenue, ranked descending, Top 10
- **Purpose:** the "top products" equivalent for an airline is its top revenue-generating routes — informs which routes deserve schedule/capacity protection.

### 8. Revenue Analysis (column chart with drill-down)
- **Dimension:** Airline → drill down to Route
- **Measure:** `SUM(revenue)`, `SUM(revenue) / SUM(seats_available * distance_miles)` (RASM)
- **Purpose:** separates "which airline sells the most tickets" from "which airline monetizes capacity most efficiently."

### 9. Profit Analysis (waterfall or column chart)
- **Measure:** `operating_margin` = Revenue − Fuel Cost, by airline and by month
- **Purpose:** a simplified profitability lens — reveals whether high-revenue airlines/routes are also the most profitable once fuel cost is netted out.

---

## Page 2: Route & Delay Detail (drill-down)

- **Delay heatmap:** Day of Week × Month matrix visual (mirrors `05_delay_heatmap_day_month.png`) — pinpoints exactly when delays cluster.
- **Aircraft type delay box-plot equivalent:** Power BI doesn't natively support box plots — implemented via a certified custom visual ("Box and Whisker Chart") or approximated with a banded column chart showing P25/P50/P75 delay by aircraft type.
- **Route table:** detailed, sortable table with route, flights flown, avg delay, cancellation rate, revenue — supports the "chronically unreliable routes" investigation from the SQL HAVING query.
- **Weather impact chart:** Avg delay by weather_condition — tests whether uncontrollable (weather) or controllable (mechanical/crew) factors dominate.

---

## Design Notes
- **Color convention:** Green = On-Time/Healthy, Amber = Minor issue, Red = Severe/Cancelled — applied consistently across all visuals for instant pattern recognition.
- **Tooltips:** every visual includes a tooltip page showing the underlying flight count so no one mistakes a percentage for a large or small sample.
- **Consistency with SQL/Python:** the `delay_category` field, `load_factor`, and `RASM` measures are calculated identically to the Python feature engineering (see `notebooks/01_data_cleaning.py`) and the SQL CASE WHEN logic (see `sql/02_analysis_queries.sql`) — ensuring a single source of truth across every layer of the project.
