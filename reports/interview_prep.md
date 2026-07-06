# Interview Preparation
## Airline Operations Analytics Project — 40 Q&A (Technical + Business)

---

## Part 1: Technical Interview Questions (20)

**1. Walk me through your data cleaning process.**
I standardized inconsistent text (casing/whitespace in airline names), removed duplicate flight_id records from a simulated extraction bug, and handled missing values column-by-column rather than with one blanket rule: numeric fields like distance were imputed with route-level medians, delay/cancellation reason nulls were filled with explicit "No Delay"/"Not Cancelled" labels (since the null itself was meaningful), and satisfaction score nulls were left as NaN — imputing a fake satisfaction score would have biased the satisfaction analysis.

**2. Why didn't you just drop all missing values?**
Different nulls mean different things. A missing delay reason means "flight wasn't delayed," not "data is broken" — dropping it would delete valid on-time flights. A missing satisfaction score means the passenger didn't respond to a survey — imputing a value there would fabricate an opinion nobody gave. Blanket dropna() would have silently discarded a large share of legitimate records and distorted the analysis.

**3. How did you detect outliers, and what did you do with them?**
I used the IQR method (1.5×IQR beyond Q1/Q3) on departure delay minutes. About 20% of flights fell outside the bound. Rather than deleting them, I flagged them with a boolean column, because a 300-minute delay is a real, high-value business event (not noise) — deleting it would hide exactly the kind of severe disruption operations most needs to see.

**4. Explain a window function you used and why.**
I used RANK() OVER (PARTITION BY airline ORDER BY SUM(revenue) DESC) to rank routes by revenue within each airline. A plain GROUP BY can't do this — it would give one global ranking, not a ranking scoped to each airline. I also used a running total with SUM() OVER (ORDER BY month) to build cumulative monthly revenue, which needs to be calculated after aggregation, exactly what window functions are for.

**5. What's the difference between HAVING and WHERE, and where did you use HAVING?**
WHERE filters rows before aggregation; HAVING filters groups after aggregation. I used HAVING to find routes with average arrival delay over 25 minutes AND more than 50 flights flown — you can't filter on an aggregate like AVG() in a WHERE clause, so HAVING was required.

**6. Why did you use a CTE instead of a subquery?**
CTEs make multi-step logic readable — I built flight-level delay flags in one CTE, then aggregated them by airline in a second CTE, rather than nesting subqueries. For anyone reviewing or maintaining the query later, the CTE version reads top-to-bottom like a narrative instead of inside-out like a nested subquery.

**7. How did you join your fact and dimension tables, and why INNER vs. LEFT JOIN?**
I INNER JOINed flights to the airports dimension twice (aliased for origin and destination) when I only wanted flights with valid airport matches. I used a LEFT JOIN when listing all large hub airports and their flight counts, specifically so airports with zero flights in a given period would still appear with a 0 count instead of disappearing from the result.

**8. What feature engineering did you do in Python, and why not just do it in SQL?**
I engineered delay_category, route, load_factor, RASM, and operating_margin in Python during the cleaning step so the exact same definitions could be reused consistently across SQL, Python EDA, and Power BI — a single source of truth. I did replicate the delay_category CASE WHEN logic in SQL too, deliberately, so a stakeholder querying the database directly gets the same categories as the dashboard.

**9. What is load factor and why does it matter?**
Load factor is passengers divided by available seats — the airline industry's standard capacity-utilization metric. It matters because it separates "we flew a lot of flights" from "we filled those flights profitably." A route with high flight count but low load factor is a candidate for reduced frequency or smaller aircraft.

**10. What is RASM and why compute it instead of just total revenue?**
Revenue per Available Seat Mile normalizes revenue by both capacity and distance, so you can fairly compare a short regional route to a long-haul route on efficiency rather than raw dollar volume, which naturally favors long routes.

**11. How would you scale this pipeline for millions of rows?**
Move from CSV/Pandas to a proper warehouse (Postgres/Snowflake/BigQuery) and push the heavy aggregation into SQL rather than Pandas; use chunked reading or Dask/PySpark for the cleaning step if data no longer fits in memory; and schedule the pipeline with Airflow rather than running scripts manually.

**12. How did you validate that your cleaning logic didn't distort the data?**
I printed before/after row counts and missing-value counts at each step, checked that duplicate removal used a genuine unique key (flight_id) rather than a heuristic, and cross-checked summary statistics (like average delay) before and after cleaning to confirm imputation didn't meaningfully shift the distribution.

**13. Why did you choose a box plot for aircraft type delays instead of a bar chart of averages?**
A bar chart of averages hides variability. Two aircraft types can have the same average delay but very different consistency — one tightly clustered near zero, one with wild swings. The box plot shows the median, spread (IQR), and outliers simultaneously, which is what you actually need to make a fleet-reliability decision.

**14. Why a heatmap for day-of-week vs. month instead of two separate bar charts?**
Because the real pattern is an interaction effect — e.g., a specific weekday might only be bad in certain months (holiday season). Two separate 1-D bar charts (avg by day, avg by month) would average away exactly that interaction; the 2-D heatmap preserves it.

**15. Why did you use a pie chart for cancellation reasons but not for anything else?**
Pie charts only work well for a small number of categories that sum to a meaningful 100% whole — cancellation reasons fit that (4 categories, all cancellations). I avoided pie charts for things like revenue by route (too many categories, differences too subtle to read as angles) and used bar charts instead, which are easier to compare precisely.

**16. How would you turn this into a predictive model?**
Frame it as a binary classification problem — predict is_on_time (or delay > threshold) using features like airline, route, aircraft type, weather, day of week, and month, with a logistic regression baseline and a gradient boosting model (e.g., XGBoost) for higher accuracy, and evaluate with precision/recall since delay events are the minority, imbalanced class.

**17. What data quality checks would you automate if this ran daily in production?**
Row count anomaly detection (sudden spike/drop), null-rate monitoring per column against historical baselines, referential integrity checks (every origin/destination airport code exists in the dimension table), and a "duplicate flight_id" alert—all as automated pipeline checks before data reaches the dashboard.

**18. Why store delay reason as an explicit "No Delay" label instead of leaving it null in the final dataset?**
Because in BI tools like Power BI, a blank/null category is easy to accidentally exclude in a filter or visual, silently distorting a "delay reason breakdown" chart. An explicit label makes the "no delay" case a first-class, filterable category instead of an invisible gap.

**19. What's a limitation of your dataset or approach you'd flag to a stakeholder?**
Customer satisfaction was collected independently in this dataset and shows almost no relationship with delay severity — that's a legitimate, interesting finding, but it also means the dataset likely lacks the real drivers of satisfaction (service quality, communication), so I would not present the "delay doesn't affect satisfaction" conclusion as final without a proper driver analysis.

**20. Why build the SQL, Python, and Power BI layers with the same delay_category and KPI definitions?**
Consistency of definitions across tools is one of the most common failure points in real analytics teams — if SQL calls a flight "delayed" at a different threshold than the dashboard, two people looking at "the same" number get different answers and lose trust in the data. Keeping definitions synchronized was a deliberate design choice, not an afterthought.

---

## Part 2: Business Interview Questions (20)

**1. What business problem does this project solve?**
It quantifies why on-time performance and revenue have plateaued for a multi-airline operator, and turns previously siloed operational and satisfaction data into a single view leadership can act on.

**2. Who are the stakeholders for this analysis?**
Operations leadership (delay/cancellation drivers), commercial/revenue teams (route and regional performance), fleet planning (aircraft utilization), and customer experience teams (satisfaction data).

**3. What was the single most surprising insight?**
That customer satisfaction showed almost no measurable difference between on-time and severely delayed flights — challenging the common assumption that reducing delays is the biggest lever for improving customer experience.

**4. What would you recommend the company do first, and why?**
Focus on mechanical readiness and crew scheduling before weather mitigation, since those two controllable factors account for roughly half of all cancellations — the highest-ROI, most controllable fix identified in the analysis.

**5. How would you prioritize the 8 recommendations you made?**
I'd prioritize by combination of impact and controllability: mechanical/crew fixes and targeted route reviews first (high impact, controllable), then survey response-rate improvements (foundational data fix), then regional capacity investigation (revenue upside, needs more validation) last.

**6. How would you measure whether your recommendations worked?**
Track the same KPIs before/after: on-time %, cancellation rate by cause, delay minutes on the flagged routes, and survey response rate — with a defined review cadence (e.g., quarterly) against this baseline.

**7. Why focus on specific routes rather than airline-wide policy changes?**
Because the data shows delay problems concentrate in a small number of specific routes/hubs rather than being uniform across an airline — a blanket airline-wide policy would spend resources on routes that aren't actually problems.

**8. How confident are you in the finding that weather isn't the dominant delay driver?**
Reasonably confident directionally, given the consistent pattern across weather categories, but I'd flag it as a hypothesis to validate with real weather-severity data (this project uses simplified weather categories) before it drives major budget decisions.

**9. What's the business risk of ignoring the mechanical/crew cancellation finding?**
Continued preventable cancellations that erode customer trust and generate compensation costs, while the company potentially over-invests in weather-related contingency planning that addresses a smaller share of the actual problem.

**10. How does this analysis tie operational performance to revenue?**
Through the RASM and route revenue analysis — it shows which routes are both reliable and profitable versus routes that may be high-volume but low-yield, letting commercial teams make schedule/capacity decisions with both dimensions in view simultaneously.

**11. Why look at regional revenue differences?**
To identify whether the Midwest's lower revenue reflects genuinely lower demand or under-scheduled capacity — an important distinction because the fix (marketing vs. scheduling) is completely different depending on the cause.

**12. What would you tell a regional manager whose route is on the "chronically delayed" list?**
That the flag is based on statistically meaningful volume (50+ flights, not a handful of outliers), and the recommended next step is a root-cause review with ground operations at the connecting hub, not to assume it's simply weather-driven.

**13. How would you explain "load factor" to a non-technical executive?**
It's the percentage of seats actually filled with paying passengers on a flight — a load factor of 80% means, on average, 8 out of every 10 seats were occupied.

**14. Why does customer satisfaction matter if it doesn't correlate with delays here?**
Because it still matters for retention and brand reputation — the finding doesn't mean satisfaction is unimportant, it means delay reduction alone won't move it, so investment should instead go toward identifying the real drivers (service, communication, comfort).

**15. How would you pitch the ROI of fixing the top 5 delayed routes?**
Frame it around cost avoidance (missed connections, compensation, crew overtime from delay cascades) and reputational upside, using the flight volume on those specific routes to size the potential number of passengers affected per year.

**16. What would you say if a stakeholder challenged your outlier-handling decision (keeping them, not deleting them)?**
I'd explain that a severe delay is a real event with real business cost — deleting it to make the average look better would hide the exact problem the business needs visibility into; flagging instead of deleting preserves both the signal and analytical transparency.

**17. How would this dashboard change an operations manager's weekly routine?**
Instead of manually pulling ad hoc reports, they'd open one dashboard, filter to their region/airline, and immediately see which routes are underperforming and why — turning a reactive, request-driven process into a proactive, self-serve one.

**18. What's the business case for closing the survey response-rate gap?**
With only 76% of flights currently generating satisfaction data, a quarter of the customer experience picture is invisible — closing that gap increases confidence in any satisfaction-based decision the business makes downstream.

**19. If the company had budget for only ONE initiative from this analysis, which would you recommend?**
The mechanical/crew reliability initiative — it's the most controllable, directly reduces cancellations (a hard customer-facing failure), and doesn't require new data collection to act on immediately.

**20. How does this project reflect how you'd operate as a data analyst on our team?**
I don't stop at "here's a chart" — I connect each finding to a specific, prioritized business action, flag the limits of my own data honestly (like the satisfaction/delay finding), and build for consistency across tools so different teams trust the same numbers.
