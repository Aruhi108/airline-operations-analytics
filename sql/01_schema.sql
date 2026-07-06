-- ============================================================================
-- 01_schema.sql
-- Airline Operations Analytics — Table Definitions
-- Compatible with PostgreSQL / MySQL (minor syntax tweaks may be needed
-- for BOOLEAN handling on MySQL <8.0, noted inline).
-- ============================================================================

DROP TABLE IF EXISTS flights;
DROP TABLE IF EXISTS airports;

-- Dimension table: airport reference data
CREATE TABLE airports (
    airport_code   VARCHAR(3)  PRIMARY KEY,
    city           VARCHAR(50) NOT NULL,
    region         VARCHAR(20) NOT NULL,
    hub_size       VARCHAR(10) NOT NULL   -- 'Large' or 'Medium'
);

-- Fact table: one row per scheduled flight (cleaned version, post Python ETL)
CREATE TABLE flights (
    flight_id                     VARCHAR(10) PRIMARY KEY,
    flight_date                   DATE        NOT NULL,
    airline                       VARCHAR(30) NOT NULL,
    flight_number                 VARCHAR(10),
    origin_airport                VARCHAR(3)  NOT NULL REFERENCES airports(airport_code),
    destination_airport           VARCHAR(3)  NOT NULL REFERENCES airports(airport_code),
    distance_miles                NUMERIC(6,1),
    aircraft_type                 VARCHAR(30),
    scheduled_departure            TIMESTAMP,
    actual_departure                TIMESTAMP,
    scheduled_arrival               TIMESTAMP,
    actual_arrival                  TIMESTAMP,
    departure_delay_minutes        NUMERIC(6,1),
    arrival_delay_minutes          NUMERIC(6,1),
    delay_reason                  VARCHAR(30),
    cancelled                     BOOLEAN,       -- MySQL: use TINYINT(1)
    cancellation_reason           VARCHAR(30),
    diverted                      BOOLEAN,       -- MySQL: use TINYINT(1)
    seats_available                INT,
    passengers                    INT,
    ticket_price_avg               NUMERIC(8,2),
    revenue                       NUMERIC(10,2),
    fuel_cost                     NUMERIC(10,2),
    weather_condition              VARCHAR(20),
    customer_satisfaction_score    NUMERIC(2,1),
    delay_category                VARCHAR(20)     -- engineered in Python (On-Time/Minor/Major)
);

-- Helpful indexes for the query patterns used throughout this project
CREATE INDEX idx_flights_date      ON flights (flight_date);
CREATE INDEX idx_flights_airline   ON flights (airline);
CREATE INDEX idx_flights_origin    ON flights (origin_airport);
CREATE INDEX idx_flights_dest      ON flights (destination_airport);
