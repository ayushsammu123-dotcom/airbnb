-- =============================================================================
-- schema.sql
-- Airbnb Pricing & Revenue Analytics — Database Schema
-- =============================================================================
-- Creates all core tables and supporting indexes for the analytics pipeline.
-- All tables use CREATE TABLE IF NOT EXISTS for idempotent execution.
-- =============================================================================

PRAGMA journal_mode = WAL;       -- Better concurrent read performance
PRAGMA foreign_keys  = ON;       -- Enforce referential integrity

-- ---------------------------------------------------------------------------
-- TABLE: listings
-- Primary fact table.  One row per Airbnb listing scraped from the source
-- dataset.  Revenue & scoring columns are derived/computed by the pipeline.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS listings (
    -- ── Identifiers ──────────────────────────────────────────────────────────
    listing_id                      INTEGER     PRIMARY KEY,
    host_id                         INTEGER     NOT NULL,

    -- ── Host information ─────────────────────────────────────────────────────
    host_name                       TEXT,
    host_is_superhost               TEXT,           -- 't' / 'f'
    host_listings_count             INTEGER,
    calculated_host_listings_count  INTEGER,

    -- ── Location ─────────────────────────────────────────────────────────────
    neighbourhood                   TEXT,
    neighbourhood_group             TEXT,
    latitude                        REAL,
    longitude                       REAL,

    -- ── Listing attributes ───────────────────────────────────────────────────
    room_type                       TEXT,
    property_type                   TEXT,
    price                           REAL,
    minimum_nights                  INTEGER,
    maximum_nights                  INTEGER,
    instant_bookable                TEXT,           -- 't' / 'f'
    license                         TEXT,

    -- ── Review metrics ───────────────────────────────────────────────────────
    number_of_reviews               INTEGER,
    reviews_per_month               REAL,
    review_rate_number              REAL,
    number_of_reviews_ltm           INTEGER,        -- last twelve months
    last_review                     TEXT,           -- ISO-8601 date string

    -- ── Availability ─────────────────────────────────────────────────────────
    availability_365                INTEGER,

    -- ── Estimated revenue (computed by pipeline) ─────────────────────────────
    estimated_occupied_days         REAL,
    estimated_occupancy_rate        REAL,
    estimated_annual_revenue        REAL,
    estimated_monthly_revenue       REAL,
    revenue_per_available_day       REAL,

    -- ── Categorical labels (computed by pipeline) ────────────────────────────
    price_category                  TEXT,
    occupancy_category              TEXT,
    host_category                   TEXT,
    cluster_label                   INTEGER,
    cluster_name                    TEXT,

    -- ── Scoring metrics (computed by pipeline) ───────────────────────────────
    demand_score                    REAL,
    host_performance_score          REAL,
    location_score                  REAL,
    price_competitiveness_score     REAL,
    pricing_gap                     REAL,           -- actual_price - market_median
    pricing_opportunity             REAL            -- potential revenue uplift
);


-- ---------------------------------------------------------------------------
-- TABLE: hosts
-- Dimension table aggregating per-host metrics.  Populated by the pipeline
-- after the listings table is loaded.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS hosts (
    host_id                     INTEGER     PRIMARY KEY,
    host_name                   TEXT,
    host_is_superhost           TEXT,
    host_listings_count         INTEGER,
    total_estimated_revenue     REAL,
    avg_price                   REAL,
    avg_reviews                 REAL,
    performance_score           REAL
);


-- ---------------------------------------------------------------------------
-- TABLE: neighbourhood_stats
-- Pre-aggregated neighbourhood-level summary used for dashboarding and
-- quick lookups without expensive GROUP BY queries at runtime.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS neighbourhood_stats (
    neighbourhood           TEXT,
    neighbourhood_group     TEXT,
    listing_count           INTEGER,
    avg_price               REAL,
    median_price            REAL,
    total_revenue           REAL,
    avg_occupancy           REAL,
    avg_demand_score        REAL,

    PRIMARY KEY (neighbourhood, neighbourhood_group)
);


-- ---------------------------------------------------------------------------
-- TABLE: cleaning_report
-- Audit log written by the ETL / cleaning pipeline on each run.
-- Tracks data quality metrics over time.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cleaning_report (
    id                  INTEGER     PRIMARY KEY AUTOINCREMENT,
    run_date            TEXT        NOT NULL,   -- ISO-8601 datetime of pipeline run
    original_rows       INTEGER,
    final_rows          INTEGER,
    duplicates_removed  INTEGER,
    invalids_removed    INTEGER,
    outliers_handled    INTEGER,
    missing_before      INTEGER,
    missing_after       INTEGER
);


-- =============================================================================
-- INDEXES
-- Chosen to accelerate the most common analytical query patterns:
--   • Filtering / grouping by neighbourhood and neighbourhood_group
--   • Filtering by host, room type, property type
--   • Range queries on price, revenue, and score columns
--   • Sorting on review and availability columns
-- =============================================================================

-- Host-level lookups
CREATE INDEX IF NOT EXISTS idx_listings_host_id
    ON listings (host_id);

-- Location-based grouping (most dashboards group at neighbourhood level)
CREATE INDEX IF NOT EXISTS idx_listings_neighbourhood
    ON listings (neighbourhood);

CREATE INDEX IF NOT EXISTS idx_listings_neighbourhood_group
    ON listings (neighbourhood_group);

-- Composite index for queries that filter by borough then neighbourhood
CREATE INDEX IF NOT EXISTS idx_listings_location
    ON listings (neighbourhood_group, neighbourhood);

-- Room / property type filtering
CREATE INDEX IF NOT EXISTS idx_listings_room_type
    ON listings (room_type);

CREATE INDEX IF NOT EXISTS idx_listings_property_type
    ON listings (property_type);

-- Price range queries and sorting
CREATE INDEX IF NOT EXISTS idx_listings_price
    ON listings (price);

-- Revenue sorting and range queries
CREATE INDEX IF NOT EXISTS idx_listings_annual_revenue
    ON listings (estimated_annual_revenue);

-- Demand and scoring queries
CREATE INDEX IF NOT EXISTS idx_listings_demand_score
    ON listings (demand_score);

CREATE INDEX IF NOT EXISTS idx_listings_pricing_gap
    ON listings (pricing_gap);

-- Superhost / instant-bookable flag filtering
CREATE INDEX IF NOT EXISTS idx_listings_superhost
    ON listings (host_is_superhost);

CREATE INDEX IF NOT EXISTS idx_listings_instant_bookable
    ON listings (instant_bookable);

-- Review-count based filtering
CREATE INDEX IF NOT EXISTS idx_listings_reviews
    ON listings (number_of_reviews);

-- Last-review date for recency queries
CREATE INDEX IF NOT EXISTS idx_listings_last_review
    ON listings (last_review);

-- Cluster-based segmentation queries
CREATE INDEX IF NOT EXISTS idx_listings_cluster
    ON listings (cluster_label);

-- Price category label (used in distribution queries)
CREATE INDEX IF NOT EXISTS idx_listings_price_category
    ON listings (price_category);

-- Composite: neighbourhood + price — common join pattern in pricing analysis
CREATE INDEX IF NOT EXISTS idx_listings_nbhood_price
    ON listings (neighbourhood, price);

-- hosts dimension table indexes
CREATE INDEX IF NOT EXISTS idx_hosts_superhost
    ON hosts (host_is_superhost);

CREATE INDEX IF NOT EXISTS idx_hosts_revenue
    ON hosts (total_estimated_revenue);

-- neighbourhood_stats dimension table index
CREATE INDEX IF NOT EXISTS idx_nbstats_group
    ON neighbourhood_stats (neighbourhood_group);
