-- ============================================================================
-- 02_analysis_queries.sql
-- Airline Operations Analytics — Business SQL Analysis
-- Each query is preceded by: the stakeholder question, and the query itself.
-- Assumes the CLEANED flights table (post Python ETL, loaded via 03 script).
-- ============================================================================


-- ----------------------------------------------------------------------------
-- Q1. SELECT + WHERE
-- Business question: "Show me all flights on SkyLink Air that were cancelled
--                      in Q3 2025, so Ops can review root causes."
-- ----------------------------------------------------------------------------
SELECT flight_id, flight_date, origin_airport, destination_airport,
       cancellation_reason
FROM flights
WHERE airline = 'SkyLink Air'
  AND cancelled = TRUE
  AND flight_date BETWEEN '2025-07-01' AND '2025-09-30'
ORDER BY flight_date;


-- ----------------------------------------------------------------------------
-- Q2. GROUP BY + ORDER BY + Aggregate Functions
-- Business question: "Which airline has the highest average departure delay?"
-- Purpose: identify operational underperformers for management review.
-- ----------------------------------------------------------------------------
SELECT
    airline,
    COUNT(*)                              AS total_flights,
    ROUND(AVG(departure_delay_minutes),1) AS avg_departure_delay,
    ROUND(SUM(revenue),0)                 AS total_revenue
FROM flights
WHERE cancelled = FALSE
GROUP BY airline
ORDER BY avg_departure_delay DESC;


-- ----------------------------------------------------------------------------
-- Q3. GROUP BY + HAVING
-- Business question: "Which routes are chronically unreliable — average
--                      delay over 25 minutes AND more than 50 flights flown
--                      (so we ignore statistically insignificant routes)?"
-- ----------------------------------------------------------------------------
SELECT
    origin_airport,
    destination_airport,
    COUNT(*)                              AS flights_flown,
    ROUND(AVG(arrival_delay_minutes),1)   AS avg_arrival_delay
FROM flights
WHERE cancelled = FALSE
GROUP BY origin_airport, destination_airport
HAVING COUNT(*) > 50 AND AVG(arrival_delay_minutes) > 25
ORDER BY avg_arrival_delay DESC;


-- ----------------------------------------------------------------------------
-- Q4. CASE WHEN
-- Business question: "Bucket every flight into a delay-severity category so
--                      leadership can see the SHAPE of the delay problem,
--                      not just the average."
-- ----------------------------------------------------------------------------
SELECT
    flight_id,
    departure_delay_minutes,
    CASE
        WHEN cancelled = TRUE                        THEN 'Cancelled'
        WHEN departure_delay_minutes <= 0             THEN 'On-Time / Early'
        WHEN departure_delay_minutes BETWEEN 1 AND 15 THEN 'Minor Delay'
        WHEN departure_delay_minutes BETWEEN 16 AND 60 THEN 'Moderate Delay'
        ELSE 'Severe Delay'
    END AS delay_category
FROM flights;


-- ----------------------------------------------------------------------------
-- Q5. JOIN (INNER JOIN, twice — origin and destination)
-- Business question: "Show flight volume and revenue by ORIGIN CITY and
--                      REGION, not just airport code, for a regional
--                      performance review."
-- ----------------------------------------------------------------------------
SELECT
    o.city    AS origin_city,
    o.region  AS origin_region,
    d.city    AS destination_city,
    COUNT(*)              AS flights_flown,
    ROUND(SUM(f.revenue),0) AS total_revenue
FROM flights f
INNER JOIN airports o ON f.origin_airport      = o.airport_code
INNER JOIN airports d ON f.destination_airport = d.airport_code
WHERE f.cancelled = FALSE
GROUP BY o.city, o.region, d.city
ORDER BY total_revenue DESC
LIMIT 15;


-- ----------------------------------------------------------------------------
-- Q6. LEFT JOIN
-- Business question: "List every large hub airport and its flight count,
--                      including hubs that may have zero originating
--                      flights in a given slice (edge-case safe reporting)."
-- ----------------------------------------------------------------------------
SELECT
    a.airport_code,
    a.city,
    a.hub_size,
    COUNT(f.flight_id) AS flights_originating
FROM airports a
LEFT JOIN flights f ON a.airport_code = f.origin_airport
                   AND f.flight_date BETWEEN '2025-01-01' AND '2025-01-31'
WHERE a.hub_size = 'Large'
GROUP BY a.airport_code, a.city, a.hub_size
ORDER BY flights_originating DESC;


-- ----------------------------------------------------------------------------
-- Q7. Common Table Expression (CTE)
-- Business question: "For each airline, what % of its flights are severely
--                      delayed (>60 min)? Build this step-by-step and reuse
--                      the intermediate result cleanly."
-- ----------------------------------------------------------------------------
WITH flight_status AS (
    SELECT
        airline,
        flight_id,
        CASE WHEN departure_delay_minutes > 60 THEN 1 ELSE 0 END AS is_severe_delay
    FROM flights
    WHERE cancelled = FALSE
),
airline_summary AS (
    SELECT
        airline,
        COUNT(*)              AS total_flights,
        SUM(is_severe_delay)  AS severe_delay_flights
    FROM flight_status
    GROUP BY airline
)
SELECT
    airline,
    total_flights,
    severe_delay_flights,
    ROUND(100.0 * severe_delay_flights / total_flights, 2) AS pct_severe_delay
FROM airline_summary
ORDER BY pct_severe_delay DESC;


-- ----------------------------------------------------------------------------
-- Q8. Window Functions (RANK, running total)
-- Business question: "Rank routes by revenue WITHIN each airline, and show
--                      a running (cumulative) monthly revenue trend for the
--                      whole business."
-- ----------------------------------------------------------------------------

-- 8a. Rank top routes per airline (partitioned ranking)
SELECT
    airline,
    origin_airport,
    destination_airport,
    ROUND(SUM(revenue),0) AS route_revenue,
    RANK() OVER (
        PARTITION BY airline
        ORDER BY SUM(revenue) DESC
    ) AS revenue_rank_within_airline
FROM flights
WHERE cancelled = FALSE
GROUP BY airline, origin_airport, destination_airport;

-- 8b. Running (cumulative) monthly revenue — classic window function use case
WITH monthly_revenue AS (
    SELECT
        DATE_TRUNC('month', flight_date) AS month,
        SUM(revenue)                     AS monthly_revenue
    FROM flights
    WHERE cancelled = FALSE
    GROUP BY DATE_TRUNC('month', flight_date)
)
SELECT
    month,
    monthly_revenue,
    SUM(monthly_revenue) OVER (ORDER BY month) AS cumulative_revenue,
    ROUND(AVG(monthly_revenue) OVER (
        ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 0) AS rolling_3mo_avg_revenue
FROM monthly_revenue
ORDER BY month;


-- ----------------------------------------------------------------------------
-- Q9. Aggregate Functions + CASE (Load Factor / capacity utilization)
-- Business question: "What is our average seat load factor by aircraft
--                      type, and which aircraft are under-utilized
--                      (<70% load factor on average)?"
-- ----------------------------------------------------------------------------
SELECT
    aircraft_type,
    COUNT(*)                                            AS flights_flown,
    ROUND(AVG(passengers * 1.0 / seats_available), 2)   AS avg_load_factor,
    CASE
        WHEN AVG(passengers * 1.0 / seats_available) < 0.70 THEN 'Under-utilized'
        WHEN AVG(passengers * 1.0 / seats_available) < 0.85 THEN 'Healthy'
        ELSE 'High-demand'
    END AS utilization_flag
FROM flights
WHERE cancelled = FALSE
GROUP BY aircraft_type
ORDER BY avg_load_factor;


-- ----------------------------------------------------------------------------
-- Q10. CTE + Window Function combined (customer satisfaction deep-dive)
-- Business question: "Identify the bottom 3 routes by customer satisfaction
--                      for each region, so regional managers get a
--                      targeted, ranked list instead of one giant table."
-- ----------------------------------------------------------------------------
WITH route_satisfaction AS (
    SELECT
        o.region,
        f.origin_airport,
        f.destination_airport,
        ROUND(AVG(f.customer_satisfaction_score), 2) AS avg_satisfaction,
        COUNT(*) AS flights_flown
    FROM flights f
    JOIN airports o ON f.origin_airport = o.airport_code
    WHERE f.cancelled = FALSE AND f.customer_satisfaction_score IS NOT NULL
    GROUP BY o.region, f.origin_airport, f.destination_airport
    HAVING COUNT(*) >= 20
),
ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY region
            ORDER BY avg_satisfaction ASC
        ) AS satisfaction_rank
    FROM route_satisfaction
)
SELECT region, origin_airport, destination_airport, avg_satisfaction, flights_flown
FROM ranked
WHERE satisfaction_rank <= 3
ORDER BY region, satisfaction_rank;
