-- =============================================================================
-- advanced_analysis.sql
-- Airbnb Pricing & Revenue Analytics — Advanced Queries (Q26–Q35)
-- =============================================================================
-- Ten advanced queries using CTEs, window functions, and multi-condition
-- filters to surface pricing opportunities, segmentation insights, and
-- strategic business intelligence.
-- All queries are valid SQLite 3.25+ SQL (window functions supported).
-- =============================================================================


-- -----------------------------------------------------------------------------
-- Query 26: Potentially Underpriced Listings
-- Business question: Which active, well-reviewed listings are priced
--   significantly below the market equilibrium?
--   A negative pricing_gap means the listing's price is below its
--   neighbourhood's median.  Threshold: gap < -$50 with > 10 reviews
--   (proves genuine demand at the current price).
-- -----------------------------------------------------------------------------
SELECT
    listing_id,
    host_name,
    neighbourhood,
    neighbourhood_group                                 AS borough,
    room_type,
    COALESCE(price, 0)                                  AS current_price,
    COALESCE(pricing_gap, 0)                            AS pricing_gap,
    COALESCE(pricing_opportunity, 0)                    AS pricing_opportunity,
    COALESCE(number_of_reviews, 0)                      AS number_of_reviews,
    COALESCE(estimated_annual_revenue, 0)               AS est_annual_revenue,
    COALESCE(estimated_occupancy_rate, 0)               AS occupancy_rate,
    COALESCE(demand_score, 0)                           AS demand_score
FROM  listings
WHERE COALESCE(pricing_gap, 0) < -50
  AND COALESCE(number_of_reviews, 0) > 10
  AND price IS NOT NULL
ORDER BY pricing_gap ASC          -- most underpriced first
LIMIT 30;


-- -----------------------------------------------------------------------------
-- Query 27: Potentially Overpriced Listings
-- Business question: Which listings charge well above the market rate yet
--   struggle to attract guests (evidenced by low review counts)?
--   A pricing_gap > $100 with very few reviews suggests the price is
--   deterring bookings.
-- -----------------------------------------------------------------------------
SELECT
    listing_id,
    host_name,
    neighbourhood,
    neighbourhood_group                                 AS borough,
    room_type,
    property_type,
    COALESCE(price, 0)                                  AS current_price,
    COALESCE(pricing_gap, 0)                            AS pricing_gap,
    COALESCE(number_of_reviews, 0)                      AS number_of_reviews,
    COALESCE(estimated_annual_revenue, 0)               AS est_annual_revenue,
    COALESCE(estimated_occupancy_rate, 0)               AS occupancy_rate,
    COALESCE(availability_365, 0)                       AS availability_days   -- high = low bookings
FROM  listings
WHERE COALESCE(pricing_gap, 0) > 100
  AND COALESCE(number_of_reviews, 0) < 5
  AND price IS NOT NULL
ORDER BY pricing_gap DESC         -- most overpriced first
LIMIT 30;


-- -----------------------------------------------------------------------------
-- Query 28: Hosts with 5+ Properties — Portfolio Summary
-- Business question: What does the professional-operator segment look like?
--   Hosts with 5+ listings are likely property managers or commercial
--   operators, and understanding their metrics reveals how scale affects
--   performance.
-- -----------------------------------------------------------------------------
WITH multi_hosts AS (
    -- Identify hosts who manage 5 or more listings in the dataset
    SELECT   host_id
    FROM     listings
    GROUP BY host_id
    HAVING   COUNT(listing_id) >= 5
)
SELECT
    l.host_id,
    l.host_name,
    CASE l.host_is_superhost
        WHEN 't' THEN 'Superhost'
        WHEN 'f' THEN 'Non-Superhost'
        ELSE           'Unknown'
    END                                                         AS superhost_status,

    COUNT(l.listing_id)                                         AS portfolio_size,

    -- Geographic spread
    COUNT(DISTINCT l.neighbourhood)                             AS neighbourhoods_active,
    COUNT(DISTINCT l.room_type)                                 AS room_types_offered,

    -- Financial metrics
    ROUND(AVG(COALESCE(l.price, 0)), 2)                         AS avg_nightly_price,
    ROUND(SUM(COALESCE(l.estimated_annual_revenue, 0)), 2)      AS total_annual_revenue,
    ROUND(AVG(COALESCE(l.estimated_annual_revenue, 0)), 2)      AS avg_revenue_per_listing,
    ROUND(AVG(COALESCE(l.estimated_occupancy_rate, 0)), 4)      AS avg_occupancy_rate,

    -- Quality metrics
    ROUND(AVG(COALESCE(l.number_of_reviews, 0)), 1)             AS avg_reviews,
    ROUND(AVG(COALESCE(l.host_performance_score, 0)), 2)        AS avg_performance_score
FROM  listings AS l
JOIN  multi_hosts AS mh ON l.host_id = mh.host_id
GROUP BY l.host_id, l.host_name, l.host_is_superhost
ORDER BY total_annual_revenue DESC
LIMIT 25;


-- -----------------------------------------------------------------------------
-- Query 29: High Demand + High Revenue Neighbourhoods (Top Performing Areas)
-- Business question: Which neighbourhoods combine strong guest demand with
--   strong revenue generation?  These are the premium investment targets.
--   Filters for areas in the top 50th percentile of both demand and revenue.
-- -----------------------------------------------------------------------------
WITH neighbourhood_agg AS (
    SELECT
        neighbourhood,
        neighbourhood_group,
        COUNT(listing_id)                                   AS listing_count,
        ROUND(AVG(COALESCE(demand_score, 0)), 2)            AS avg_demand_score,
        ROUND(AVG(COALESCE(estimated_annual_revenue, 0)), 2) AS avg_annual_revenue,
        ROUND(SUM(COALESCE(estimated_annual_revenue, 0)), 2) AS total_annual_revenue,
        ROUND(AVG(COALESCE(price, 0)), 2)                   AS avg_price,
        ROUND(AVG(COALESCE(estimated_occupancy_rate, 0)), 4) AS avg_occupancy_rate
    FROM  listings
    WHERE neighbourhood IS NOT NULL
    GROUP BY neighbourhood, neighbourhood_group
    HAVING COUNT(listing_id) >= 10
),
city_medians AS (
    -- City-wide medians to define "above average"
    SELECT
        AVG(avg_demand_score)    AS median_demand,
        AVG(avg_annual_revenue)  AS median_revenue
    FROM neighbourhood_agg
)
SELECT
    na.neighbourhood,
    na.neighbourhood_group                      AS borough,
    na.listing_count,
    na.avg_demand_score,
    na.avg_annual_revenue,
    na.total_annual_revenue,
    na.avg_price,
    na.avg_occupancy_rate,
    -- Composite performance tier
    CASE
        WHEN na.avg_demand_score > cm.median_demand * 1.2
         AND na.avg_annual_revenue > cm.median_revenue * 1.2 THEN 'Tier 1 – Elite'
        WHEN na.avg_demand_score > cm.median_demand
         AND na.avg_annual_revenue > cm.median_revenue       THEN 'Tier 2 – Strong'
        ELSE                                                      'Tier 3 – Average'
    END                                         AS performance_tier
FROM  neighbourhood_agg AS na
CROSS JOIN city_medians AS cm
WHERE na.avg_demand_score > cm.median_demand
  AND na.avg_annual_revenue > cm.median_revenue
ORDER BY na.avg_demand_score DESC, na.avg_annual_revenue DESC;


-- -----------------------------------------------------------------------------
-- Query 30: Listing Segmentation Summary by Cluster
-- Business question: How do the ML-derived clusters differ in price, revenue,
--   and demand?  Validates that clustering meaningfully separates listing types.
-- -----------------------------------------------------------------------------
SELECT
    cluster_label,
    COALESCE(cluster_name, 'Unassigned')                        AS cluster_name,
    COUNT(listing_id)                                           AS listing_count,
    ROUND(AVG(COALESCE(price, 0)), 2)                           AS avg_price,
    ROUND(AVG(COALESCE(estimated_annual_revenue, 0)), 2)        AS avg_annual_revenue,
    ROUND(AVG(COALESCE(estimated_occupancy_rate, 0)), 4)        AS avg_occupancy_rate,
    ROUND(AVG(COALESCE(demand_score, 0)), 2)                    AS avg_demand_score,
    ROUND(AVG(COALESCE(host_performance_score, 0)), 2)          AS avg_host_performance,
    ROUND(AVG(COALESCE(location_score, 0)), 2)                  AS avg_location_score,
    ROUND(AVG(COALESCE(number_of_reviews, 0)), 1)               AS avg_reviews,
    ROUND(AVG(COALESCE(availability_365, 0)), 1)                AS avg_availability_days
FROM  listings
GROUP BY cluster_label, cluster_name
ORDER BY cluster_label;


-- -----------------------------------------------------------------------------
-- Query 31: Recency Proxy — Recent vs Old Last-Review Date Comparison
-- Business question: Do listings with recent activity (reviewed in the last
--   year) differ meaningfully in price, occupancy, and revenue from those
--   with stale reviews (older than 1 year)?  Acts as a YoY proxy because
--   the dataset has no booking time-series.
--   NOTE: SQLite date arithmetic uses DATE('now', '-N years').
-- -----------------------------------------------------------------------------
SELECT
    CASE
        WHEN last_review >= DATE('now', '-6 months')  THEN 'Active – Last 6 Months'
        WHEN last_review >= DATE('now', '-1 year')    THEN 'Active – Last 6–12 Months'
        WHEN last_review >= DATE('now', '-2 years')   THEN 'Stale – 1–2 Years Ago'
        WHEN last_review IS NOT NULL                  THEN 'Stale – 2+ Years Ago'
        ELSE                                               'Never Reviewed'
    END                                                         AS recency_bucket,

    COUNT(listing_id)                                           AS listing_count,
    ROUND(AVG(COALESCE(price, 0)), 2)                           AS avg_price,
    ROUND(AVG(COALESCE(number_of_reviews, 0)), 1)               AS avg_reviews,
    ROUND(AVG(COALESCE(reviews_per_month, 0)), 2)               AS avg_reviews_per_month,
    ROUND(AVG(COALESCE(estimated_occupancy_rate, 0)), 4)        AS avg_occupancy_rate,
    ROUND(AVG(COALESCE(estimated_annual_revenue, 0)), 2)        AS avg_annual_revenue,
    ROUND(AVG(COALESCE(availability_365, 0)), 1)                AS avg_availability_days
FROM  listings
GROUP BY recency_bucket
ORDER BY MIN(COALESCE(last_review, '0000-00-00')) DESC;


-- -----------------------------------------------------------------------------
-- Query 32: Superhost Portfolio Analysis — Multi vs Single Property Superhosts
-- Business question: Among superhosts only, does running multiple properties
--   compound revenue or dilute quality (reflected in reviews)?
-- -----------------------------------------------------------------------------
WITH superhost_listings AS (
    SELECT
        host_id,
        host_name,
        COUNT(listing_id) AS num_properties
    FROM  listings
    WHERE host_is_superhost = 't'
    GROUP BY host_id, host_name
)
SELECT
    CASE
        WHEN sl.num_properties = 1 THEN 'Single-Property Superhost'
        WHEN sl.num_properties <= 4 THEN 'Small Portfolio (2–4)'
        ELSE                             'Large Portfolio (5+)'
    END                                                         AS superhost_type,

    COUNT(DISTINCT l.host_id)                                   AS host_count,
    COUNT(l.listing_id)                                         AS listing_count,
    ROUND(AVG(COALESCE(l.price, 0)), 2)                         AS avg_price,
    ROUND(AVG(COALESCE(l.number_of_reviews, 0)), 1)             AS avg_reviews,
    ROUND(AVG(COALESCE(l.reviews_per_month, 0)), 2)             AS avg_reviews_per_month,
    ROUND(AVG(COALESCE(l.estimated_annual_revenue, 0)), 2)      AS avg_annual_revenue,
    ROUND(AVG(COALESCE(l.estimated_occupancy_rate, 0)), 4)      AS avg_occupancy_rate,
    ROUND(AVG(COALESCE(l.host_performance_score, 0)), 2)        AS avg_performance_score
FROM  listings AS l
JOIN  superhost_listings AS sl ON l.host_id = sl.host_id
WHERE l.host_is_superhost = 't'
GROUP BY superhost_type
ORDER BY avg_annual_revenue DESC;


-- -----------------------------------------------------------------------------
-- Query 33: Demand Score Distribution by Neighbourhood Group (Borough)
-- Business question: How is guest demand distributed across boroughs?
--   Breaks demand into Low / Medium / High / Very High tiers to show
--   which boroughs have the most consistently attractive listings.
-- -----------------------------------------------------------------------------
SELECT
    neighbourhood_group                                         AS borough,
    COUNT(listing_id)                                           AS total_listings,
    ROUND(AVG(COALESCE(demand_score, 0)), 2)                    AS avg_demand_score,
    ROUND(MIN(COALESCE(demand_score, 0)), 2)                    AS min_demand_score,
    ROUND(MAX(COALESCE(demand_score, 0)), 2)                    AS max_demand_score,

    -- Tier counts
    SUM(CASE WHEN COALESCE(demand_score, 0) < 25                THEN 1 ELSE 0 END) AS low_demand_count,
    SUM(CASE WHEN COALESCE(demand_score, 0) BETWEEN 25 AND 49.99 THEN 1 ELSE 0 END) AS medium_demand_count,
    SUM(CASE WHEN COALESCE(demand_score, 0) BETWEEN 50 AND 74.99 THEN 1 ELSE 0 END) AS high_demand_count,
    SUM(CASE WHEN COALESCE(demand_score, 0) >= 75               THEN 1 ELSE 0 END) AS very_high_demand_count,

    -- Percentage in high+ tiers
    ROUND(
        100.0 * SUM(CASE WHEN COALESCE(demand_score, 0) >= 50 THEN 1 ELSE 0 END)
        / COUNT(listing_id),
        1
    )                                                           AS pct_high_or_above
FROM  listings
WHERE neighbourhood_group IS NOT NULL
GROUP BY neighbourhood_group
ORDER BY avg_demand_score DESC;


-- -----------------------------------------------------------------------------
-- Query 34: Price Quartile vs Average Demand Score
-- Business question: Is there a positive or negative relationship between
--   nightly price and guest demand?  Uses window functions to assign price
--   quartiles and then groups to reveal the trend.
-- -----------------------------------------------------------------------------
WITH price_quartiles AS (
    SELECT
        listing_id,
        price,
        demand_score,
        estimated_annual_revenue,
        number_of_reviews,
        -- Assign quartile using NTILE window function
        NTILE(4) OVER (ORDER BY price) AS price_quartile
    FROM listings
    WHERE price IS NOT NULL
      AND price > 0
)
SELECT
    price_quartile,
    CASE price_quartile
        WHEN 1 THEN 'Q1 – Lowest Prices'
        WHEN 2 THEN 'Q2 – Lower-Mid Prices'
        WHEN 3 THEN 'Q3 – Upper-Mid Prices'
        WHEN 4 THEN 'Q4 – Highest Prices'
    END                                                         AS price_quartile_label,

    COUNT(listing_id)                                           AS listing_count,
    ROUND(MIN(price), 2)                                        AS min_price,
    ROUND(MAX(price), 2)                                        AS max_price,
    ROUND(AVG(price), 2)                                        AS avg_price,
    ROUND(AVG(COALESCE(demand_score, 0)), 2)                    AS avg_demand_score,
    ROUND(AVG(COALESCE(estimated_annual_revenue, 0)), 2)        AS avg_annual_revenue,
    ROUND(AVG(COALESCE(number_of_reviews, 0)), 1)               AS avg_reviews
FROM  price_quartiles
GROUP BY price_quartile
ORDER BY price_quartile;


-- -----------------------------------------------------------------------------
-- Query 35: Business Opportunity Map
-- Business question: Which neighbourhoods represent the best expansion
--   opportunity — strong latent demand (high avg_demand_score) but pricing
--   below the city median (meaning hosts haven't yet capitalised on that demand)?
--   These are prime targets for new hosts or for existing hosts to raise rates.
-- -----------------------------------------------------------------------------
WITH city_median_price AS (
    -- City-wide median price as the reference benchmark
    SELECT ROUND(AVG(price), 2) AS city_median
    FROM (
        SELECT price
        FROM   listings
        WHERE  price IS NOT NULL
        ORDER  BY price
        LIMIT  2 - (SELECT COUNT(*) FROM listings WHERE price IS NOT NULL) % 2
        OFFSET (SELECT (COUNT(*) - 1) / 2 FROM listings WHERE price IS NOT NULL)
    )
),
neighbourhood_profile AS (
    SELECT
        neighbourhood,
        neighbourhood_group,
        COUNT(listing_id)                                   AS listing_count,
        ROUND(AVG(COALESCE(demand_score, 0)), 2)            AS avg_demand_score,
        ROUND(AVG(COALESCE(price, 0)), 2)                   AS avg_price,
        ROUND(AVG(COALESCE(estimated_annual_revenue, 0)), 2) AS avg_annual_revenue,
        ROUND(AVG(COALESCE(estimated_occupancy_rate, 0)), 4) AS avg_occupancy_rate
    FROM  listings
    WHERE neighbourhood IS NOT NULL
    GROUP BY neighbourhood, neighbourhood_group
    HAVING COUNT(listing_id) >= 10
)
SELECT
    np.neighbourhood,
    np.neighbourhood_group                          AS borough,
    np.listing_count,
    np.avg_demand_score,
    np.avg_price,
    cm.city_median                                  AS city_median_price,
    ROUND(cm.city_median - np.avg_price, 2)         AS price_gap_below_median,  -- positive = underpriced
    np.avg_annual_revenue,
    np.avg_occupancy_rate,

    -- Opportunity score: higher demand gap + bigger price gap = bigger opportunity
    ROUND(
        (np.avg_demand_score / 100.0)
        * ((cm.city_median - np.avg_price) / cm.city_median),
        4
    )                                               AS opportunity_index

FROM  neighbourhood_profile AS np
CROSS JOIN city_median_price AS cm
WHERE np.avg_demand_score > (
          -- Keep only neighbourhoods with above-average demand
          SELECT AVG(avg_demand_score)
          FROM   neighbourhood_profile
      )
  AND np.avg_price < cm.city_median   -- and below-median pricing
ORDER BY opportunity_index DESC
LIMIT 20;
