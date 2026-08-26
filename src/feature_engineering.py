"""
src/feature_engineering.py
===========================
Feature engineering for the Airbnb Pricing & Revenue Analytics project.

Transforms cleaned listing data into an enriched feature set used by the
analysis and ML layers.  All functions are stateless and return new
DataFrames / Series without modifying their inputs.

Functions
---------
engineer_features         -- Main entry-point; adds all derived columns.
compute_demand_score      -- Composite demand metric (0-100).
compute_host_performance_score -- Host-level quality score per listing (0-100).
compute_location_score    -- Neighbourhood attractiveness score per listing (0-100).
compute_price_competitiveness -- How a listing's price compares to its neighbourhood (0-100).
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from src.utils import get_price_category, get_occupancy_category

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _min_max_scale(series: pd.Series) -> pd.Series:
    """
    Min-max scale a Series to [0, 1].

    Returns a zero-filled Series of the same index if the range is zero
    (avoids division-by-zero for constant columns).

    Parameters
    ----------
    series : pd.Series
        Numeric series to scale.

    Returns
    -------
    pd.Series
        Scaled series in [0, 1].
    """
    min_val = series.min()
    max_val = series.max()
    if max_val == min_val:
        return pd.Series(np.zeros(len(series)), index=series.index)
    return (series - min_val) / (max_val - min_val)


# ---------------------------------------------------------------------------
# Main feature engineering function
# ---------------------------------------------------------------------------


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add all derived features to the cleaned listings DataFrame.

    Derived columns added
    ---------------------
    Revenue / occupancy
        - ``estimated_occupied_days``  : 365 - availability_365, clipped [0, 365]
        - ``estimated_occupancy_rate`` : estimated_occupied_days / 365
        - ``estimated_annual_revenue`` : price * estimated_occupied_days
        - ``estimated_monthly_revenue``: estimated_annual_revenue / 12
        - ``revenue_per_available_day``: estimated_annual_revenue / 365

    Categorical
        - ``price_category``   : Budget / Mid-Range / Premium / Luxury
        - ``occupancy_category``: Low / Medium / High
        - ``host_category``    : Single-Property / Multi-Property
        - ``pricing_gap``      : placeholder 0.0 (filled later by ML model)
        - ``pricing_opportunity``: Underpriced / Fairly Priced / Overpriced
          (based on pricing_gap after ML; placeholder uses 'Fairly Priced')

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned listings DataFrame.  Must contain at minimum ``price`` and
        ``availability_365``; other columns enhance quality.

    Returns
    -------
    pd.DataFrame
        New DataFrame with all original columns plus the derived features.

    Raises
    ------
    ValueError
        If the input DataFrame is empty.

    Examples
    --------
    >>> enriched = engineer_features(cleaned_df)
    >>> enriched.columns.tolist()
    [..., 'estimated_occupancy_rate', 'price_category', ...]
    """
    if df.empty:
        raise ValueError("engineer_features received an empty DataFrame.")

    out = df.copy()

    # -----------------------------------------------------------------------
    # Revenue / occupancy features
    # -----------------------------------------------------------------------
    if "availability_365" in out.columns:
        avail = pd.to_numeric(out["availability_365"], errors="coerce").fillna(182)
        out["estimated_occupied_days"] = (365 - avail).clip(0, 365)
    else:
        logger.warning("availability_365 missing; defaulting estimated_occupied_days to 0.")
        out["estimated_occupied_days"] = 0.0

    out["estimated_occupancy_rate"] = (out["estimated_occupied_days"] / 365).round(4)

    price_col = pd.to_numeric(out.get("price", pd.Series(0.0, index=out.index)), errors="coerce").fillna(0.0)
    out["estimated_annual_revenue"] = (price_col * out["estimated_occupied_days"]).round(2)
    out["estimated_monthly_revenue"] = (out["estimated_annual_revenue"] / 12).round(2)
    out["revenue_per_available_day"] = (out["estimated_annual_revenue"] / 365).round(2)

    # -----------------------------------------------------------------------
    # Price category
    # -----------------------------------------------------------------------
    out["price_category"] = price_col.apply(get_price_category)

    # -----------------------------------------------------------------------
    # Occupancy category
    # -----------------------------------------------------------------------
    out["occupancy_category"] = out["estimated_occupancy_rate"].apply(get_occupancy_category)

    # -----------------------------------------------------------------------
    # Host category
    # -----------------------------------------------------------------------
    if "host_listings_count" in out.columns:
        host_count = pd.to_numeric(out["host_listings_count"], errors="coerce").fillna(1)
        out["host_category"] = host_count.apply(
            lambda x: "Single-Property" if x == 1 else "Multi-Property"
        )
    else:
        out["host_category"] = "Single-Property"

    # -----------------------------------------------------------------------
    # Pricing gap & opportunity (placeholder; filled by forecasting module)
    # -----------------------------------------------------------------------
    out["pricing_gap"] = 0.0

    # Pricing opportunity will be re-derived once pricing_gap is populated by ML.
    # For now every listing starts as "Fairly Priced".
    out["pricing_opportunity"] = "Fairly Priced"

    logger.info(
        "engineer_features: added %d derived columns to %d rows.",
        8,  # count of new columns
        len(out),
    )
    return out


# ---------------------------------------------------------------------------
# Composite scores
# ---------------------------------------------------------------------------


def compute_demand_score(df: pd.DataFrame) -> pd.Series:
    """
    Compute a composite demand score (0-100) for each listing.

    The score combines four indicators, each independently min-max normalised
    to [0, 1] before weighting:

    ======================= ======= ===========================================
    Indicator               Weight  Rationale
    ======================= ======= ===========================================
    reviews_per_month       30 %    Recent booking velocity
    number_of_reviews       20 %    Historical popularity
    estimated_occupancy_rate 30 %   Proxy for how often the listing is booked
    availability_365 (inv.) 20 %    Less availability => higher demand
    ======================= ======= ===========================================

    Parameters
    ----------
    df : pd.DataFrame
        Listings DataFrame.  Columns used (filled with 0 if absent):
        ``reviews_per_month``, ``number_of_reviews``,
        ``estimated_occupancy_rate``, ``availability_365``.

    Returns
    -------
    pd.Series
        Demand score in [0, 100], indexed like ``df``.
        Named ``"demand_score"``.

    Examples
    --------
    >>> df["demand_score"] = compute_demand_score(df)
    """
    if df.empty:
        return pd.Series(dtype=float, name="demand_score")

    def _safe_col(col: str) -> pd.Series:
        if col in df.columns:
            return pd.to_numeric(df[col], errors="coerce").fillna(0)
        return pd.Series(np.zeros(len(df)), index=df.index)

    reviews_pm = _min_max_scale(_safe_col("reviews_per_month"))
    n_reviews = _min_max_scale(_safe_col("number_of_reviews"))

    if "estimated_occupancy_rate" in df.columns:
        occupancy = _min_max_scale(_safe_col("estimated_occupancy_rate"))
    else:
        avail = _safe_col("availability_365")
        occupancy = _min_max_scale((365 - avail).clip(0, 365) / 365)

    availability_inv = 1 - _min_max_scale(_safe_col("availability_365"))

    raw_score = (
        0.30 * reviews_pm
        + 0.20 * n_reviews
        + 0.30 * occupancy
        + 0.20 * availability_inv
    )

    demand_score = (raw_score * 100).clip(0, 100).round(2)
    demand_score.name = "demand_score"
    return demand_score


def compute_host_performance_score(df: pd.DataFrame) -> pd.Series:
    """
    Compute a host performance score (0-100) for each listing row.

    The score is derived from host-level aggregates (average of each metric
    across all listings owned by the same host):
    - Average price
    - Average reviews per month
    - Average estimated occupancy rate
    - Total estimated annual revenue

    Each aggregate is independently min-max normalised across hosts, then
    averaged (equal weights) and scaled to 0-100.

    Parameters
    ----------
    df : pd.DataFrame
        Listings DataFrame.  Must contain ``host_id``.

    Returns
    -------
    pd.Series
        Host performance score per listing, indexed like ``df``.
        Named ``"host_performance_score"``.
    """
    if df.empty or "host_id" not in df.columns:
        return pd.Series(np.zeros(len(df)), index=df.index, name="host_performance_score")

    def _safe(col: str) -> pd.Series:
        if col in df.columns:
            return pd.to_numeric(df[col], errors="coerce").fillna(0)
        return pd.Series(np.zeros(len(df)), index=df.index)

    tmp = df[["host_id"]].copy()
    tmp["price"] = _safe("price")
    tmp["reviews_per_month"] = _safe("reviews_per_month")
    tmp["estimated_occupancy_rate"] = (
        _safe("estimated_occupancy_rate")
        if "estimated_occupancy_rate" in df.columns
        else (365 - _safe("availability_365")).clip(0, 365) / 365
    )
    tmp["estimated_annual_revenue"] = _safe("estimated_annual_revenue")

    host_stats = (
        tmp.groupby("host_id")
        .agg(
            avg_price=("price", "mean"),
            avg_reviews_pm=("reviews_per_month", "mean"),
            avg_occupancy=("estimated_occupancy_rate", "mean"),
            total_revenue=("estimated_annual_revenue", "sum"),
        )
        .reset_index()
    )

    for col in ["avg_price", "avg_reviews_pm", "avg_occupancy", "total_revenue"]:
        host_stats[f"{col}_norm"] = _min_max_scale(host_stats[col])

    host_stats["host_performance_score"] = (
        (
            host_stats["avg_price_norm"]
            + host_stats["avg_reviews_pm_norm"]
            + host_stats["avg_occupancy_norm"]
            + host_stats["total_revenue_norm"]
        )
        / 4
        * 100
    ).round(2)

    score_map = host_stats.set_index("host_id")["host_performance_score"]
    result = df["host_id"].map(score_map).fillna(0).rename("host_performance_score")
    return result


def compute_location_score(df: pd.DataFrame) -> pd.Series:
    """
    Compute a location attractiveness score (0-100) per listing.

    The score is based on neighbourhood-level aggregates:
    - Average estimated annual revenue
    - Average reviews per month
    - Average estimated occupancy rate

    Each is min-max normalised across neighbourhoods, averaged equally, and
    scaled to 0-100.

    Parameters
    ----------
    df : pd.DataFrame
        Listings DataFrame.  Should contain ``neighbourhood``.

    Returns
    -------
    pd.Series
        Location score per listing, indexed like ``df``.
        Named ``"location_score"``.
    """
    if df.empty:
        return pd.Series(dtype=float, name="location_score")

    neighbourhood_col = (
        "neighbourhood" if "neighbourhood" in df.columns else None
    )
    if neighbourhood_col is None:
        logger.warning("neighbourhood column not found; returning zero location scores.")
        return pd.Series(np.zeros(len(df)), index=df.index, name="location_score")

    def _safe(col: str) -> pd.Series:
        if col in df.columns:
            return pd.to_numeric(df[col], errors="coerce").fillna(0)
        return pd.Series(np.zeros(len(df)), index=df.index)

    tmp = df[[neighbourhood_col]].copy()
    tmp["estimated_annual_revenue"] = _safe("estimated_annual_revenue")
    tmp["reviews_per_month"] = _safe("reviews_per_month")
    tmp["estimated_occupancy_rate"] = (
        _safe("estimated_occupancy_rate")
        if "estimated_occupancy_rate" in df.columns
        else (365 - _safe("availability_365")).clip(0, 365) / 365
    )

    nbhd_stats = (
        tmp.groupby(neighbourhood_col)
        .agg(
            avg_revenue=("estimated_annual_revenue", "mean"),
            avg_reviews_pm=("reviews_per_month", "mean"),
            avg_occupancy=("estimated_occupancy_rate", "mean"),
        )
        .reset_index()
    )

    for col in ["avg_revenue", "avg_reviews_pm", "avg_occupancy"]:
        nbhd_stats[f"{col}_norm"] = _min_max_scale(nbhd_stats[col])

    nbhd_stats["location_score"] = (
        (
            nbhd_stats["avg_revenue_norm"]
            + nbhd_stats["avg_reviews_pm_norm"]
            + nbhd_stats["avg_occupancy_norm"]
        )
        / 3
        * 100
    ).round(2)

    score_map = nbhd_stats.set_index(neighbourhood_col)["location_score"]
    result = df[neighbourhood_col].map(score_map).fillna(0).rename("location_score")
    return result


def compute_price_competitiveness(df: pd.DataFrame) -> pd.Series:
    """
    Score how competitively a listing is priced relative to its neighbourhood.

    The score is computed as::

        raw = (neighbourhood_median_price - listing_price) / neighbourhood_median_price

    A positive raw value means the listing is cheaper than the neighbourhood
    median (more competitive).  This is then min-max scaled to [0, 100]:
    - 100 = maximally competitive (far below median)
    -   0 = least competitive (far above median)

    If a neighbourhood has only one listing, it receives a neutral score of 50.

    Parameters
    ----------
    df : pd.DataFrame
        Listings DataFrame.  Must contain ``price`` and ``neighbourhood``.

    Returns
    -------
    pd.Series
        Price competitiveness score per listing, indexed like ``df``.
        Named ``"price_competitiveness"``.
    """
    if df.empty or "price" not in df.columns:
        return pd.Series(dtype=float, name="price_competitiveness")

    neighbourhood_col = (
        "neighbourhood" if "neighbourhood" in df.columns else None
    )
    if neighbourhood_col is None:
        logger.warning("neighbourhood column not found; returning neutral competitiveness.")
        return pd.Series(np.full(len(df), 50.0), index=df.index, name="price_competitiveness")

    price_num = pd.to_numeric(df["price"], errors="coerce").fillna(0)

    nbhd_median = (
        df.assign(_price=price_num)
        .groupby(neighbourhood_col)["_price"]
        .median()
    )
    median_mapped = df[neighbourhood_col].map(nbhd_median).fillna(price_num.median())

    # Positive => listing cheaper than neighbourhood median => more competitive
    raw = (median_mapped - price_num) / median_mapped.replace(0, np.nan)
    raw = raw.fillna(0)

    scaled = _min_max_scale(raw) * 100
    scaled = scaled.clip(0, 100).round(2)
    scaled.name = "price_competitiveness"
    return scaled
