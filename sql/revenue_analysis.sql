-- =============================================================================
-- revenue_analysis.sql
-- Airbnb Pricing & Revenue Analytics — Revenue Queries (Q16–Q25)
-- =============================================================================
-- Ten queries focused on estimated annual and monthly revenue patterns
-- across neighbourhoods, individual listings, hosts, room types, property
-- types, and host/booking segments.
-- All COALESCE calls default NULL revenue figures to 0.
-- =============================================================================


-- -----------------------------------------------------------------------------
-- Query 16: Top 10 Neighbourhoods by Total Estimated Annual Revenue
-- Business question: Which neighbourhoods generate the most total platform
--   revenue, and which combination of supply and price drives that?
-- -----------------------------------------------------------------------------
SELECT
    neighbourhood,
    neighbourhood_group                                         AS borough,
    COUNT(listing_id)                                           AS listing_count,
    ROUND(SUM(COALESCE(estimated_annual_revenue, 0)), 2)        AS total_annual_revenue,
    ROUND(AVG(COALESCE(estimated_annual_revenue, 0)), 2)        AS avg_annual_revenue,
    ROUND(AVG(COALESCE(price, 0)), 2)                           AS avg_price,
    ROUND(AVG(COALESCE(estimated_occupancy_rate, 0)), 4)        AS avg_occupancy_rate
FROM  listings
WHERE neighbourhood IS NOT NULL
GROUP BY neighbourhood, neighbourhood_group
ORDER BY total_annual_revenue DESC
LIMIT 10;


-- -----------------------------------------------------------------------------
-- Query 17: Top 20 Highest-Revenue Individual Listings
-- Business question: Which specific listings are the strongest revenue
--   performers, and what characteristics do they share?
-- -----------------------------------------------------------------------------
SELECT
    listing_id,
    host_name,
    neighbourhood,
    neighbourhood_group                                 AS borough,
    room_type,
    property_type,
    COALESCE(price, 0)                                  AS nightly_price,
    COALESCE(estimated_occupancy_rate, 0)               AS occupancy_rate,
    COALESCE(estimated_occupied_days, 0)                AS occupied_days,
    COALESCE(estimated_annual_revenue, 0)               AS annual_revenue,
    COALESCE(estimated_monthly_revenue, 0)              AS monthly_revenue,
    COALESCE(revenue_per_available_day, 0)              AS rev_per_available_day
FROM  listings
WHERE estimated_annual_revenue IS NOT NULL
ORDER BY estimated_annual_revenue DESC
LIMIT 20;


-- -----------------------------------------------------------------------------
-- Query 18: Top 10 Hosts by Total Estimated Annual Revenue
-- Business question: Who are the platform's highest-earning hosts?
--   Includes portfolio size and superhost status to understand whether
--   revenue concentration comes from scale or premium positioning.
-- -----------------------------------------------------------------------------
SELECT
    host_id,
    host_name,
    CASE host_is_superhost
        WHEN 't' THEN 'Superhost'
        WHEN 'f' THEN 'Non-Superhost'
        ELSE           'Unknown'
    END                                                         AS host_type,
    COUNT(listing_id)                                           AS listing_count,
    ROUND(SUM(COALESCE(estimated_annual_revenue, 0)), 2)        AS total_annual_revenue,
    ROUND(AVG(COALESCE(estimated_annual_revenue, 0)), 2)        AS avg_revenue_per_listing,
    ROUND(AVG(COALESCE(price, 0)), 2)                           AS avg_nightly_price,
    ROUND(AVG(COALESCE(estimated_occupancy_rate, 0)), 4)        AS avg_occupancy_rate
FROM  listings
GROUP BY host_id, host_name, host_is_superhost
ORDER BY total_annual_revenue DESC
LIMIT 10;


-- -----------------------------------------------------------------------------
-- Query 19: Average Estimated Annual Revenue by Room Type
-- Business question: Which room type produces the highest expected annual
--   return, and does higher price fully offset lower occupancy (or vice versa)?
-- -----------------------------------------------------------------------------
SELECT
    room_type,
    COUNT(listing_id)                                           AS listing_count,
    ROUND(AVG(COALESCE(estimated_annual_revenue, 0)), 2)        AS avg_annual_revenue,
    ROUND(AVG(COALESCE(estimated_monthly_revenue, 0)), 2)       AS avg_monthly_revenue,
    ROUND(AVG(COALESCE(price, 0)), 2)                           AS avg_nightly_price,
    ROUND(AVG(COALESCE(estimated_occupancy_rate, 0)), 4)        AS avg_occupancy_rate,
    ROUND(AVG(COALESCE(estimated_occupied_days, 0)), 1)         AS avg_occupied_days,
    ROUND(AVG(COALESCE(revenue_per_available_day, 0)), 2)       AS avg_rev_per_available_day
FROM  listings
WHERE room_type IS NOT NULL
GROUP BY room_type
ORDER BY avg_annual_revenue DESC;


-- -----------------------------------------------------------------------------
-- Query 20: Average Estimated Annual Revenue by Property Type
-- Business question: Do certain property formats (entire homes, boutique
--   hotels, etc.) command a revenue premium beyond what price alone explains?
-- -----------------------------------------------------------------------------
SELECT
    property_type,
    COUNT(listing_id)                                           AS listing_count,
    ROUND(AVG(COALESCE(estimated_annual_revenue, 0)), 2)        AS avg_annual_revenue,
    ROUND(AVG(COALESCE(price, 0)), 2)                           AS avg_nightly_price,
    ROUND(AVG(COALESCE(estimated_occupancy_rate, 0)), 4)        AS avg_occupancy_rate
FROM  listings
WHERE property_type IS NOT NULL
GROUP BY property_type
HAVING COUNT(listing_id) >= 10      -- exclude property types with tiny samples
ORDER BY avg_annual_revenue DESC
LIMIT 20;


-- -----------------------------------------------------------------------------
-- Query 21: Revenue Potential by Host Category (Single vs Multi-Property)
-- Business question: Do multi-property hosts (operators / property managers)
--   generate more revenue per listing than single-property hosts (individuals)?
-- -----------------------------------------------------------------------------
SELECT
    COALESCE(host_category, 'Unknown')                          AS host_category,
    COUNT(listing_id)                                           AS listing_count,
    COUNT(DISTINCT host_id)                                     AS host_count,
    ROUND(AVG(COALESCE(estimated_annual_revenue, 0)), 2)        AS avg_annual_revenue,
    ROUND(AVG(COALESCE(price, 0)), 2)                           AS avg_nightly_price,
    ROUND(AVG(COALESCE(estimated_occupancy_rate, 0)), 4)        AS avg_occupancy_rate,
    ROUND(AVG(COALESCE(number_of_reviews, 0)), 1)               AS avg_reviews
FROM  listings
GROUP BY host_category
ORDER BY avg_annual_revenue DESC;


-- -----------------------------------------------------------------------------
-- Query 22: Revenue by Occupancy Category
-- Business question: How much does occupancy tier drive total revenue?
--   Demonstrates whether filling more nights (high occupancy) compensates
--   for lower per-night rates.
-- -----------------------------------------------------------------------------
SELECT
    COALESCE(occupancy_category, 'Unknown')                     AS occupancy_category,
    COUNT(listing_id)                                           AS listing_count,
    ROUND(AVG(COALESCE(estimated_annual_revenue, 0)), 2)        AS avg_annual_revenue,
    ROUND(AVG(COALESCE(estimated_occupied_days, 0)), 1)         AS avg_occupied_days,
    ROUND(AVG(COALESCE(estimated_occupancy_rate, 0)), 4)        AS avg_occupancy_rate,
    ROUND(AVG(COALESCE(price, 0)), 2)                           AS avg_nightly_price,
    ROUND(SUM(COALESCE(estimated_annual_revenue, 0)), 2)        AS total_annual_revenue
FROM  listings
GROUP BY occupancy_category
ORDER BY avg_annual_revenue DESC;


-- -----------------------------------------------------------------------------
-- Query 23: Monthly Revenue Distribution — Avg Monthly Revenue by Neighbourhood
-- Business question: Which neighbourhoods yield the highest month-by-month
--   earnings?  Useful for hosts deciding where to invest or for seasonal
--   revenue planning.
-- -----------------------------------------------------------------------------
SELECT
    neighbourhood,
    neighbourhood_group                                         AS borough,
    COUNT(listing_id)                                           AS listing_count,
    ROUND(AVG(COALESCE(estimated_monthly_revenue, 0)), 2)       AS avg_monthly_revenue,
    ROUND(MIN(COALESCE(estimated_monthly_revenue, 0)), 2)       AS min_monthly_revenue,
    ROUND(MAX(COALESCE(estimated_monthly_revenue, 0)), 2)       AS max_monthly_revenue,
    ROUND(AVG(COALESCE(price, 0)), 2)                           AS avg_nightly_price,
    ROUND(AVG(COALESCE(estimated_occupancy_rate, 0)), 4)        AS avg_occupancy_rate
FROM  listings
WHERE neighbourhood IS NOT NULL
GROUP BY neighbourhood, neighbourhood_group
HAVING COUNT(listing_id) >= 5
ORDER BY avg_monthly_revenue DESC
LIMIT 20;


-- -----------------------------------------------------------------------------
-- Query 24: Instant Bookable vs Non-Instant — Revenue Comparison
-- Business question: Does enabling instant booking increase revenue by
--   reducing friction, or do manually-approved listings charge enough of a
--   premium to offset lower conversion?
-- -----------------------------------------------------------------------------
SELECT
    CASE instant_bookable
        WHEN 't' THEN 'Instant Bookable'
        WHEN 'f' THEN 'Request to Book'
        ELSE           'Unknown'
    END                                                         AS booking_type,

    COUNT(listing_id)                                           AS listing_count,
    ROUND(AVG(COALESCE(estimated_annual_revenue, 0)), 2)        AS avg_annual_revenue,
    ROUND(AVG(COALESCE(estimated_monthly_revenue, 0)), 2)       AS avg_monthly_revenue,
    ROUND(AVG(COALESCE(price, 0)), 2)                           AS avg_nightly_price,
    ROUND(AVG(COALESCE(estimated_occupancy_rate, 0)), 4)        AS avg_occupancy_rate,
    ROUND(AVG(COALESCE(number_of_reviews, 0)), 1)               AS avg_reviews
FROM  listings
GROUP BY instant_bookable
ORDER BY avg_annual_revenue DESC;


-- -----------------------------------------------------------------------------
-- Query 25: Revenue by Neighbourhood Group (Borough Level)
-- Business question: At the highest geographic level, which borough dominates
--   total Airbnb revenue, and how does that decompose into price vs occupancy?
-- -----------------------------------------------------------------------------
SELECT
    neighbourhood_group                                         AS borough,
    COUNT(listing_id)                                           AS listing_count,
    COUNT(DISTINCT host_id)                                     AS host_count,
    ROUND(SUM(COALESCE(estimated_annual_revenue, 0)), 2)        AS total_annual_revenue,
    ROUND(AVG(COALESCE(estimated_annual_revenue, 0)), 2)        AS avg_annual_revenue,
    ROUND(AVG(COALESCE(estimated_monthly_revenue, 0)), 2)       AS avg_monthly_revenue,
    ROUND(AVG(COALESCE(price, 0)), 2)                           AS avg_nightly_price,
    ROUND(AVG(COALESCE(estimated_occupancy_rate, 0)), 4)        AS avg_occupancy_rate,
    ROUND(AVG(COALESCE(estimated_occupied_days, 0)), 1)         AS avg_occupied_days
FROM  listings
WHERE neighbourhood_group IS NOT NULL
GROUP BY neighbourhood_group
ORDER BY total_annual_revenue DESC;
