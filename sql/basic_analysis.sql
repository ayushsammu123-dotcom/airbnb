-- =============================================================================
-- basic_analysis.sql
-- Airbnb Pricing & Revenue Analytics — Basic / Exploratory Queries (Q1–Q5)
-- =============================================================================
-- Five foundational queries that answer the first round of business questions:
-- dataset size, neighbourhood popularity, room-type split, property types,
-- and top-reviewed listings.
-- All queries are self-contained and can be run individually or together.
-- =============================================================================


-- -----------------------------------------------------------------------------
-- Query 1: High-Level Dataset Summary
-- Business question: What is the overall size and health of the dataset?
--   Covers total listing count, unique host count, average and approximate
--   median nightly price, and average availability across the year.
--   COALESCE guards against NULL prices or availability values.
-- -----------------------------------------------------------------------------
SELECT
    COUNT(listing_id)                                           AS total_listings,
    COUNT(DISTINCT host_id)                                     AS total_hosts,

    -- Average nightly price (rounded for readability)
    ROUND(AVG(COALESCE(price, 0)), 2)                           AS avg_price,

    -- Approximate median via subquery (SQLite has no built-in MEDIAN())
    -- Selects the middle value(s) after ordering by price.
    (
        SELECT ROUND(AVG(price), 2)
        FROM (
            SELECT price
            FROM   listings
            WHERE  price IS NOT NULL
            ORDER  BY price
            LIMIT  2 - (SELECT COUNT(*) FROM listings WHERE price IS NOT NULL) % 2
            OFFSET (SELECT (COUNT(*) - 1) / 2 FROM listings WHERE price IS NOT NULL)
        )
    )                                                           AS median_price,

    -- Average days available per year
    ROUND(AVG(COALESCE(availability_365, 0)), 1)                AS avg_availability_days,

    -- Percentage of listings that have at least one review
    ROUND(
        100.0 * SUM(CASE WHEN number_of_reviews > 0 THEN 1 ELSE 0 END)
        / COUNT(listing_id),
        1
    )                                                           AS pct_with_reviews

FROM listings;


-- -----------------------------------------------------------------------------
-- Query 2: Top 10 Neighbourhoods by Listing Count
-- Business question: Which neighbourhoods have the most supply and how does
--   price and guest satisfaction vary across them?
--   Useful for identifying over-saturated vs underserved areas.
-- -----------------------------------------------------------------------------
SELECT
    neighbourhood,
    neighbourhood_group                             AS borough,
    COUNT(listing_id)                               AS listing_count,
    ROUND(AVG(COALESCE(price, 0)), 2)               AS avg_price,
    ROUND(AVG(COALESCE(number_of_reviews, 0)), 1)   AS avg_reviews,
    ROUND(AVG(COALESCE(reviews_per_month, 0)), 2)   AS avg_reviews_per_month,
    ROUND(AVG(COALESCE(availability_365, 0)), 1)    AS avg_availability_days
FROM  listings
WHERE neighbourhood IS NOT NULL
GROUP BY neighbourhood, neighbourhood_group
ORDER BY listing_count DESC
LIMIT 10;


-- -----------------------------------------------------------------------------
-- Query 3: Room Type Distribution — Count and Percentage of Total
-- Business question: What share of inventory belongs to each room type?
--   Knowing the split helps investors understand competition level and
--   guests understand accommodation choices available to them.
-- -----------------------------------------------------------------------------
SELECT
    room_type,
    COUNT(listing_id)                                           AS listing_count,
    ROUND(
        100.0 * COUNT(listing_id) / (SELECT COUNT(*) FROM listings),
        2
    )                                                           AS pct_of_total,
    ROUND(AVG(COALESCE(price, 0)), 2)                           AS avg_price,
    ROUND(AVG(COALESCE(number_of_reviews, 0)), 1)               AS avg_reviews,
    ROUND(AVG(COALESCE(availability_365, 0)), 1)                AS avg_availability_days
FROM  listings
WHERE room_type IS NOT NULL
GROUP BY room_type
ORDER BY listing_count DESC;


-- -----------------------------------------------------------------------------
-- Query 4: Most Common Property Types with Average Price
-- Business question: Which property formats (apartment, house, condo, etc.)
--   dominate the platform, and how does property type influence nightly price?
--   Filtered to property types with at least 10 listings for statistical
--   significance, and NULLs coalesced to 0 for safety.
-- -----------------------------------------------------------------------------
SELECT
    property_type,
    COUNT(listing_id)                               AS listing_count,
    ROUND(AVG(COALESCE(price, 0)), 2)               AS avg_price,
    ROUND(MIN(COALESCE(price, 0)), 2)               AS min_price,
    ROUND(MAX(COALESCE(price, 0)), 2)               AS max_price,
    ROUND(AVG(COALESCE(number_of_reviews, 0)), 1)   AS avg_reviews
FROM  listings
WHERE property_type IS NOT NULL
GROUP BY property_type
HAVING COUNT(listing_id) >= 10          -- exclude rare / miscoded types
ORDER BY listing_count DESC
LIMIT 25;


-- -----------------------------------------------------------------------------
-- Query 5: Listings with Highest Review Counts (Top 20)
-- Business question: Which individual listings have accumulated the most
--   social proof?  High review counts proxy for booking frequency and guest
--   trust.  Includes key metrics so we can cross-reference price and
--   availability with popularity.
-- -----------------------------------------------------------------------------
SELECT
    listing_id,
    host_name,
    neighbourhood,
    neighbourhood_group                         AS borough,
    room_type,
    COALESCE(price, 0)                          AS price,
    number_of_reviews,
    COALESCE(reviews_per_month, 0)              AS reviews_per_month,
    COALESCE(availability_365, 0)               AS availability_days,
    COALESCE(estimated_annual_revenue, 0)       AS est_annual_revenue
FROM  listings
WHERE number_of_reviews IS NOT NULL
ORDER BY number_of_reviews DESC
LIMIT 20;
