-- =============================================================================
-- pricing_analysis.sql
-- Airbnb Pricing & Revenue Analytics — Pricing Queries (Q6–Q15)
-- =============================================================================
-- Ten queries covering nightly-price patterns across neighbourhoods, room
-- types, property types, and host segments.  Includes competitiveness
-- analysis and identification of under- and over-priced listings.
-- =============================================================================


-- -----------------------------------------------------------------------------
-- Query 6: Top 10 Neighbourhoods by Average Nightly Price
-- Business question: Where are the priciest places to stay?
--   Reports average, approximate median, and standard deviation to surface
--   both central tendency and price spread within each neighbourhood.
-- -----------------------------------------------------------------------------
SELECT
    neighbourhood,
    neighbourhood_group                                         AS borough,
    COUNT(listing_id)                                           AS listing_count,
    ROUND(AVG(COALESCE(price, 0)), 2)                           AS avg_price,
    ROUND(MIN(COALESCE(price, 0)), 2)                           AS min_price,
    ROUND(MAX(COALESCE(price, 0)), 2)                           AS max_price,
    ROUND(
        SQRT(AVG(price * price) - AVG(price) * AVG(price)),
        2
    )                                                           AS price_std_dev
FROM  listings
WHERE price IS NOT NULL
  AND neighbourhood IS NOT NULL
GROUP BY neighbourhood, neighbourhood_group
HAVING COUNT(listing_id) >= 5           -- require minimum sample size
ORDER BY avg_price DESC
LIMIT 10;


-- -----------------------------------------------------------------------------
-- Query 7: Average and Median Price by Room Type
-- Business question: How much of the price premium is explained by room type
--   alone?  Separates entire homes from private/shared rooms.
-- -----------------------------------------------------------------------------
SELECT
    room_type,
    COUNT(listing_id)                               AS listing_count,
    ROUND(AVG(COALESCE(price, 0)), 2)               AS avg_price,
    ROUND(MIN(COALESCE(price, 0)), 2)               AS min_price,
    ROUND(MAX(COALESCE(price, 0)), 2)               AS max_price,
    ROUND(AVG(COALESCE(availability_365, 0)), 1)    AS avg_availability_days,
    ROUND(AVG(COALESCE(number_of_reviews, 0)), 1)   AS avg_reviews
FROM  listings
WHERE room_type IS NOT NULL
GROUP BY room_type
ORDER BY avg_price DESC;


-- -----------------------------------------------------------------------------
-- Query 8: Price Distribution Buckets
-- Business question: How is pricing spread across the market?
--   Buckets reveal whether supply is concentrated in budget, mid-range,
--   or luxury tiers, guiding positioning decisions.
-- -----------------------------------------------------------------------------
SELECT
    -- Assign each listing to a price tier
    CASE
        WHEN price < 50              THEN 'Under $50'
        WHEN price BETWEEN 50  AND 99  THEN '$50 – $99'
        WHEN price BETWEEN 100 AND 199 THEN '$100 – $199'
        WHEN price BETWEEN 200 AND 299 THEN '$200 – $299'
        WHEN price BETWEEN 300 AND 499 THEN '$300 – $499'
        ELSE                              '$500+'
    END                                                         AS price_bucket,

    COUNT(listing_id)                                           AS listing_count,
    ROUND(
        100.0 * COUNT(listing_id) / (
            SELECT COUNT(*) FROM listings WHERE price IS NOT NULL
        ),
        2
    )                                                           AS pct_of_total,
    ROUND(AVG(COALESCE(number_of_reviews, 0)), 1)               AS avg_reviews,
    ROUND(AVG(COALESCE(availability_365, 0)), 1)                AS avg_availability_days,
    ROUND(AVG(COALESCE(estimated_annual_revenue, 0)), 2)        AS avg_annual_revenue
FROM  listings
WHERE price IS NOT NULL
GROUP BY price_bucket
ORDER BY MIN(price);


-- -----------------------------------------------------------------------------
-- Query 9: Superhost vs Non-Superhost Comparison
-- Business question: Does superhost status translate to higher prices, better
--   reviews, higher occupancy, and more revenue?
--   Uses CASE to label the boolean flag for readability.
-- -----------------------------------------------------------------------------
SELECT
    CASE host_is_superhost
        WHEN 't' THEN 'Superhost'
        WHEN 'f' THEN 'Non-Superhost'
        ELSE           'Unknown'
    END                                                         AS host_type,

    COUNT(listing_id)                                           AS listing_count,
    ROUND(AVG(COALESCE(price, 0)), 2)                           AS avg_price,
    ROUND(AVG(COALESCE(number_of_reviews, 0)), 1)               AS avg_reviews,
    ROUND(AVG(COALESCE(reviews_per_month, 0)), 2)               AS avg_reviews_per_month,
    ROUND(AVG(COALESCE(estimated_occupancy_rate, 0)), 4)        AS avg_occupancy_rate,
    ROUND(AVG(COALESCE(estimated_annual_revenue, 0)), 2)        AS avg_annual_revenue,
    ROUND(AVG(COALESCE(availability_365, 0)), 1)                AS avg_availability_days
FROM  listings
GROUP BY host_is_superhost
ORDER BY avg_price DESC;


-- -----------------------------------------------------------------------------
-- Query 10: Price vs Review Correlation — Avg Price by Review Count Bucket
-- Business question: Do higher-priced listings receive fewer reviews (because
--   they are booked less)?  Or does review count track independently of price?
--   Groups by review-count bands to approximate a correlation view.
-- -----------------------------------------------------------------------------
SELECT
    CASE
        WHEN number_of_reviews = 0        THEN '0 reviews'
        WHEN number_of_reviews BETWEEN 1  AND 10  THEN '1–10'
        WHEN number_of_reviews BETWEEN 11 AND 50  THEN '11–50'
        WHEN number_of_reviews BETWEEN 51 AND 100 THEN '51–100'
        WHEN number_of_reviews BETWEEN 101 AND 200 THEN '101–200'
        ELSE                                          '200+'
    END                                                         AS review_bucket,

    COUNT(listing_id)                                           AS listing_count,
    ROUND(AVG(COALESCE(price, 0)), 2)                           AS avg_price,
    ROUND(AVG(COALESCE(availability_365, 0)), 1)                AS avg_availability_days,
    ROUND(AVG(COALESCE(estimated_annual_revenue, 0)), 2)        AS avg_annual_revenue
FROM  listings
WHERE price IS NOT NULL
GROUP BY review_bucket
ORDER BY MIN(COALESCE(number_of_reviews, 0));


-- -----------------------------------------------------------------------------
-- Query 11: High-Demand Neighbourhoods with Below-Average Prices
-- Business question: Where are the best bargains for guests and the best
--   pricing opportunities for hosts?
--   Identifies neighbourhoods where demand_score > 70 yet average price sits
--   below the city-wide average — a signal of underpricing.
-- -----------------------------------------------------------------------------
WITH city_avg_price AS (
    -- Compute city-wide average once and reuse in the main query
    SELECT ROUND(AVG(price), 2) AS city_avg
    FROM   listings
    WHERE  price IS NOT NULL
)
SELECT
    l.neighbourhood,
    l.neighbourhood_group                           AS borough,
    COUNT(l.listing_id)                             AS listing_count,
    ROUND(AVG(l.demand_score), 1)                   AS avg_demand_score,
    ROUND(AVG(l.price), 2)                          AS avg_price,
    c.city_avg                                      AS city_avg_price,
    ROUND(c.city_avg - AVG(l.price), 2)             AS price_gap_below_city_avg
FROM  listings AS l
CROSS JOIN city_avg_price AS c
WHERE l.demand_score > 70
  AND l.price IS NOT NULL
  AND l.neighbourhood IS NOT NULL
GROUP BY l.neighbourhood, l.neighbourhood_group, c.city_avg
HAVING AVG(l.price) < c.city_avg
ORDER BY avg_demand_score DESC, price_gap_below_city_avg DESC;


-- -----------------------------------------------------------------------------
-- Query 12: Top 20 Most Expensive Listings
-- Business question: Who occupies the luxury tier and what do those listings
--   look like in terms of reviews, availability, and estimated revenue?
-- -----------------------------------------------------------------------------
SELECT
    listing_id,
    host_name,
    neighbourhood,
    neighbourhood_group                         AS borough,
    room_type,
    property_type,
    COALESCE(price, 0)                          AS price,
    COALESCE(minimum_nights, 0)                 AS minimum_nights,
    COALESCE(number_of_reviews, 0)              AS number_of_reviews,
    COALESCE(availability_365, 0)               AS availability_days,
    COALESCE(estimated_annual_revenue, 0)       AS est_annual_revenue
FROM  listings
WHERE price IS NOT NULL
ORDER BY price DESC
LIMIT 20;


-- -----------------------------------------------------------------------------
-- Query 13: Top 20 Cheapest Viable Listings
-- Business question: Which affordable listings still have strong social proof?
--   Filters out ghost listings (price <= $20 or fewer than 5 reviews) so only
--   genuinely active budget options are shown.
-- -----------------------------------------------------------------------------
SELECT
    listing_id,
    host_name,
    neighbourhood,
    neighbourhood_group                         AS borough,
    room_type,
    property_type,
    COALESCE(price, 0)                          AS price,
    COALESCE(number_of_reviews, 0)              AS number_of_reviews,
    COALESCE(reviews_per_month, 0)              AS reviews_per_month,
    COALESCE(availability_365, 0)               AS availability_days,
    COALESCE(estimated_annual_revenue, 0)       AS est_annual_revenue
FROM  listings
WHERE price > 20
  AND number_of_reviews > 5
ORDER BY price ASC
LIMIT 20;


-- -----------------------------------------------------------------------------
-- Query 14: Average Minimum Nights by Neighbourhood
-- Business question: Where do hosts require the longest minimum stay?
--   Long minimums reduce booking flexibility and may suppress demand.
--   Useful for comparing neighbourhood flexibility policies.
-- -----------------------------------------------------------------------------
SELECT
    neighbourhood,
    neighbourhood_group                             AS borough,
    COUNT(listing_id)                               AS listing_count,
    ROUND(AVG(COALESCE(minimum_nights, 0)), 1)      AS avg_minimum_nights,
    ROUND(MIN(COALESCE(minimum_nights, 0)), 0)      AS min_minimum_nights,
    ROUND(MAX(COALESCE(minimum_nights, 0)), 0)      AS max_minimum_nights,
    ROUND(AVG(COALESCE(price, 0)), 2)               AS avg_price
FROM  listings
WHERE neighbourhood IS NOT NULL
GROUP BY neighbourhood, neighbourhood_group
ORDER BY avg_minimum_nights DESC
LIMIT 30;


-- -----------------------------------------------------------------------------
-- Query 15: Price Competitiveness by Neighbourhood
-- Business question: For each neighbourhood, how many listings are priced
--   above vs below the local median?  Surfaces the internal competitive
--   landscape within each area.
-- -----------------------------------------------------------------------------
WITH neighbourhood_medians AS (
    -- Compute per-neighbourhood median price
    SELECT
        neighbourhood,
        AVG(price) AS median_price      -- approximation using avg of middle rows
    FROM (
        SELECT
            neighbourhood,
            price,
            ROW_NUMBER() OVER (PARTITION BY neighbourhood ORDER BY price) AS rn,
            COUNT(*)    OVER (PARTITION BY neighbourhood)                 AS cnt
        FROM listings
        WHERE price IS NOT NULL
          AND neighbourhood IS NOT NULL
    )
    WHERE rn IN ((cnt + 1) / 2, (cnt + 2) / 2)   -- grab middle 1–2 rows
    GROUP BY neighbourhood
)
SELECT
    l.neighbourhood,
    l.neighbourhood_group                                       AS borough,
    COUNT(l.listing_id)                                         AS total_listings,
    ROUND(nm.median_price, 2)                                   AS neighbourhood_median_price,
    SUM(CASE WHEN l.price > nm.median_price THEN 1 ELSE 0 END)  AS listings_above_median,
    SUM(CASE WHEN l.price <= nm.median_price THEN 1 ELSE 0 END) AS listings_at_or_below_median,
    ROUND(
        100.0 * SUM(CASE WHEN l.price > nm.median_price THEN 1 ELSE 0 END)
        / COUNT(l.listing_id),
        1
    )                                                           AS pct_above_median
FROM  listings AS l
JOIN  neighbourhood_medians AS nm
   ON l.neighbourhood = nm.neighbourhood
WHERE l.price IS NOT NULL
GROUP BY l.neighbourhood, l.neighbourhood_group, nm.median_price
ORDER BY total_listings DESC
LIMIT 30;
