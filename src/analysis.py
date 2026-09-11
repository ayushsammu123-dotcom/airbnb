"""
src/analysis.py
===============
Analysis functions for the Airbnb Pricing & Revenue Analytics project.

Provides stateless, DataFrame-in / DataFrame-out functions for:
- Correlation analysis
- Neighbourhood, room-type, property-type, and host aggregations
- Pricing distribution bucketing
- A comprehensive EDA summary dictionary
- K-Means listing segmentation
- Top / underpriced / overpriced listing retrieval
- Availability-impact analysis
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_CLUSTER_NAMES: dict[int, str] = {
    0: "Budget/High-Demand",
    1: "Premium/High-Revenue",
    2: "Budget/Low-Demand",
    3: "Luxury/Niche",
}


def _safe_numeric(df: pd.DataFrame, col: str) -> pd.Series:
    """Return a numeric Series for ``col`` or a zero Series if absent."""
    if col in df.columns:
        return pd.to_numeric(df[col], errors="coerce").fillna(0)
    return pd.Series(np.zeros(len(df)), index=df.index)


# ---------------------------------------------------------------------------
# Correlation
# ---------------------------------------------------------------------------


def compute_price_correlation(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute the Pearson correlation of ``price`` with all other numeric columns.

    Parameters
    ----------
    df : pd.DataFrame
        Listings DataFrame containing at least a ``price`` column.

    Returns
    -------
    pd.DataFrame
        Single-column DataFrame with index = column name and column
        ``correlation_with_price``, sorted by absolute correlation (descending).
        Returns empty DataFrame if ``price`` is absent.

    Examples
    --------
    >>> corr = compute_price_correlation(df)
    >>> corr.head()
    """
    if "price" not in df.columns:
        logger.warning("price column not found; returning empty correlation DataFrame.")
        return pd.DataFrame()

    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.empty:
        return pd.DataFrame()

    corr_series = numeric_df.corr()["price"].drop("price", errors="ignore")
    result = (
        corr_series.rename("correlation_with_price")
        .reset_index()
        .rename(columns={"index": "feature"})
    )
    result["abs_corr"] = result["correlation_with_price"].abs()
    result = result.sort_values("abs_corr", ascending=False).drop(columns="abs_corr").reset_index(drop=True)
    return result


# ---------------------------------------------------------------------------
# Neighbourhood stats
# ---------------------------------------------------------------------------


def compute_neighbourhood_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute per-neighbourhood aggregate statistics.

    Parameters
    ----------
    df : pd.DataFrame
        Listings DataFrame.

    Returns
    -------
    pd.DataFrame
        Columns: neighbourhood, listing_count, avg_price, median_price,
        avg_reviews, avg_occupancy_rate, total_revenue.
        Sorted by total_revenue descending.

    Examples
    --------
    >>> nbhd_stats = compute_neighbourhood_stats(df)
    """
    if df.empty or "neighbourhood" not in df.columns:
        return pd.DataFrame()

    agg = (
        df.assign(
            _price=_safe_numeric(df, "price"),
            _reviews=_safe_numeric(df, "number_of_reviews"),
            _occ=_safe_numeric(df, "estimated_occupancy_rate"),
            _rev=_safe_numeric(df, "estimated_annual_revenue"),
            _rpm=_safe_numeric(df, "reviews_per_month"),
        )
        .groupby("neighbourhood")
        .agg(
            listing_count=("neighbourhood", "count"),
            avg_price=("_price", "mean"),
            median_price=("_price", "median"),
            avg_reviews=("_reviews", "mean"),
            avg_reviews_per_month=("_rpm", "mean"),
            avg_occupancy_rate=("_occ", "mean"),
            total_revenue=("_rev", "sum"),
        )
        .reset_index()
    )

    # Attach borough if available
    if "neighbourhood_group" in df.columns:
        borough_map = (
            df[["neighbourhood", "neighbourhood_group"]]
            .drop_duplicates("neighbourhood")
            .set_index("neighbourhood")["neighbourhood_group"]
        )
        agg.insert(1, "neighbourhood_group", agg["neighbourhood"].map(borough_map))

    for col in ["avg_price", "median_price", "avg_reviews", "avg_reviews_per_month", "total_revenue"]:
        agg[col] = agg[col].round(2)
    agg["avg_occupancy_rate"] = agg["avg_occupancy_rate"].round(4)

    return agg.sort_values("total_revenue", ascending=False).reset_index(drop=True)


# ---------------------------------------------------------------------------
# Room-type stats
# ---------------------------------------------------------------------------


def compute_room_type_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute per-room-type aggregate statistics.

    Parameters
    ----------
    df : pd.DataFrame
        Listings DataFrame.

    Returns
    -------
    pd.DataFrame
        Columns: room_type, listing_count, pct_of_total, avg_price,
        median_price, avg_occupancy_rate, total_revenue.

    Examples
    --------
    >>> rt_stats = compute_room_type_stats(df)
    """
    if df.empty or "room_type" not in df.columns:
        return pd.DataFrame()

    agg = (
        df.assign(
            _price=_safe_numeric(df, "price"),
            _occ=_safe_numeric(df, "estimated_occupancy_rate"),
            _rev=_safe_numeric(df, "estimated_annual_revenue"),
        )
        .groupby("room_type")
        .agg(
            listing_count=("room_type", "count"),
            avg_price=("_price", "mean"),
            median_price=("_price", "median"),
            avg_occupancy_rate=("_occ", "mean"),
            total_revenue=("_rev", "sum"),
        )
        .reset_index()
    )

    total = agg["listing_count"].sum()
    agg.insert(2, "pct_of_total", ((agg["listing_count"] / total) * 100).round(2))

    for col in ["avg_price", "median_price", "total_revenue"]:
        agg[col] = agg[col].round(2)
    agg["avg_occupancy_rate"] = agg["avg_occupancy_rate"].round(4)

    return agg.sort_values("total_revenue", ascending=False).reset_index(drop=True)


# ---------------------------------------------------------------------------
# Property-type stats
# ---------------------------------------------------------------------------


def compute_property_type_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute per-property-type aggregate statistics.

    Parameters
    ----------
    df : pd.DataFrame
        Listings DataFrame.

    Returns
    -------
    pd.DataFrame
        Columns: property_type, listing_count, pct_of_total, avg_price,
        avg_occupancy_rate, total_revenue.
        Sorted by listing_count descending.

    Examples
    --------
    >>> pt_stats = compute_property_type_stats(df)
    """
    if df.empty or "property_type" not in df.columns:
        return pd.DataFrame()

    agg = (
        df.assign(
            _price=_safe_numeric(df, "price"),
            _occ=_safe_numeric(df, "estimated_occupancy_rate"),
            _rev=_safe_numeric(df, "estimated_annual_revenue"),
        )
        .groupby("property_type")
        .agg(
            listing_count=("property_type", "count"),
            avg_price=("_price", "mean"),
            median_price=("_price", "median"),
            avg_occupancy_rate=("_occ", "mean"),
            total_revenue=("_rev", "sum"),
        )
        .reset_index()
    )

    total = agg["listing_count"].sum()
    agg.insert(2, "pct_of_total", ((agg["listing_count"] / total) * 100).round(2))

    for col in ["avg_price", "median_price", "total_revenue"]:
        agg[col] = agg[col].round(2)
    agg["avg_occupancy_rate"] = agg["avg_occupancy_rate"].round(4)

    return agg.sort_values("listing_count", ascending=False).reset_index(drop=True)


# ---------------------------------------------------------------------------
# Host stats
# ---------------------------------------------------------------------------


def compute_host_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute per-host aggregate statistics.

    Parameters
    ----------
    df : pd.DataFrame
        Listings DataFrame.  Must contain ``host_id``.

    Returns
    -------
    pd.DataFrame
        Columns: host_id, host_name, listing_count, avg_price,
        avg_reviews_per_month, avg_occupancy_rate, total_annual_revenue,
        is_superhost.
        Sorted by total_annual_revenue descending.

    Examples
    --------
    >>> host_stats = compute_host_stats(df)
    """
    if df.empty or "host_id" not in df.columns:
        return pd.DataFrame()

    agg_dict: dict[str, Any] = {
        "listing_count": ("host_id", "count"),
        "avg_price": ("price", "mean") if "price" in df.columns else ("host_id", "count"),
        "avg_reviews_per_month": ("reviews_per_month", "mean") if "reviews_per_month" in df.columns else ("host_id", "count"),
        "avg_occupancy_rate": ("estimated_occupancy_rate", "mean") if "estimated_occupancy_rate" in df.columns else ("host_id", "count"),
        "total_annual_revenue": ("estimated_annual_revenue", "sum") if "estimated_annual_revenue" in df.columns else ("host_id", "count"),
    }
    if "host_name" in df.columns:
        agg_dict["host_name"] = ("host_name", "first")
    if "host_is_superhost" in df.columns:
        agg_dict["is_superhost"] = ("host_is_superhost", "first")

    agg = df.groupby("host_id").agg(**agg_dict).reset_index()

    for col in ["avg_price", "avg_reviews_per_month", "total_annual_revenue"]:
        if col in agg.columns:
            agg[col] = agg[col].round(2)
    if "avg_occupancy_rate" in agg.columns:
        agg["avg_occupancy_rate"] = agg["avg_occupancy_rate"].round(4)

    sort_col = "total_annual_revenue" if "total_annual_revenue" in agg.columns else "listing_count"
    return agg.sort_values(sort_col, ascending=False).reset_index(drop=True)


# ---------------------------------------------------------------------------
# Pricing distribution
# ---------------------------------------------------------------------------


def compute_pricing_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute the count of listings in each price bin.

    Bins (USD): 0-50, 50-100, 100-150, 150-200, 200-300, 300-500, 500+

    Parameters
    ----------
    df : pd.DataFrame
        Listings DataFrame with a ``price`` column.

    Returns
    -------
    pd.DataFrame
        Columns: price_bin, listing_count, pct_of_total.

    Examples
    --------
    >>> dist = compute_pricing_distribution(df)
    """
    if df.empty or "price" not in df.columns:
        return pd.DataFrame()

    price_series = pd.to_numeric(df["price"], errors="coerce").dropna()
    bins = [0, 50, 100, 150, 200, 300, 500, float("inf")]
    labels = ["$0-50", "$50-100", "$100-150", "$150-200", "$200-300", "$300-500", "$500+"]
    cut = pd.cut(price_series, bins=bins, labels=labels, right=False)
    counts = cut.value_counts().sort_index()
    result = pd.DataFrame(
        {
            "price_bin": counts.index.astype(str),
            "listing_count": counts.values,
        }
    )
    result["pct_of_total"] = ((result["listing_count"] / result["listing_count"].sum()) * 100).round(2)
    return result.reset_index(drop=True)


# ---------------------------------------------------------------------------
# EDA summary
# ---------------------------------------------------------------------------


def run_eda_summary(df: pd.DataFrame) -> dict:
    """
    Run a comprehensive exploratory-data-analysis pass and return a summary dict.

    Sections
    --------
    - ``shape``            : rows, columns
    - ``price_stats``      : describe() on ``price``
    - ``missing_pct``      : % missing per column (top-20)
    - ``neighbourhood``    : top-10 by listing count
    - ``room_type``        : distribution
    - ``property_type``    : top-10 by listing count
    - ``host``             : multi-property % and total unique hosts
    - ``revenue``          : total, mean, median annual revenue
    - ``occupancy``        : mean occupancy rate

    Parameters
    ----------
    df : pd.DataFrame
        The enriched listings DataFrame.

    Returns
    -------
    dict
        Nested summary dictionary ready for rendering or logging.
    """
    if df.empty:
        return {"error": "Empty DataFrame"}

    summary: dict[str, Any] = {}

    # Shape
    summary["shape"] = {"rows": len(df), "columns": len(df.columns)}

    # Price stats
    if "price" in df.columns:
        price_num = pd.to_numeric(df["price"], errors="coerce")
        desc = price_num.describe()
        summary["price_stats"] = {k: round(v, 2) for k, v in desc.items()}

    # Missing
    missing = (df.isna().sum() / len(df) * 100).round(2)
    missing = missing[missing > 0].sort_values(ascending=False).head(20)
    summary["missing_pct"] = missing.to_dict()

    # Neighbourhood top-10
    if "neighbourhood" in df.columns:
        top_nbhd = (
            df["neighbourhood"].value_counts().head(10).rename("listing_count")
        )
        summary["neighbourhood"] = top_nbhd.to_dict()

    # Room type
    if "room_type" in df.columns:
        summary["room_type"] = df["room_type"].value_counts().to_dict()

    # Property type top-10
    if "property_type" in df.columns:
        summary["property_type"] = df["property_type"].value_counts().head(10).to_dict()

    # Host stats
    if "host_id" in df.columns:
        total_hosts = int(df["host_id"].nunique())
        multi_prop = int((df["host_listings_count"] > 1).sum()) if "host_listings_count" in df.columns else 0
        summary["host"] = {
            "total_unique_hosts": total_hosts,
            "multi_property_listings": multi_prop,
            "multi_property_pct": round(multi_prop / len(df) * 100, 2),
        }

    # Revenue
    if "estimated_annual_revenue" in df.columns:
        rev = pd.to_numeric(df["estimated_annual_revenue"], errors="coerce")
        summary["revenue"] = {
            "total": round(float(rev.sum()), 2),
            "mean": round(float(rev.mean()), 2),
            "median": round(float(rev.median()), 2),
        }

    # Occupancy
    if "estimated_occupancy_rate" in df.columns:
        occ = pd.to_numeric(df["estimated_occupancy_rate"], errors="coerce")
        summary["occupancy"] = {
            "mean": round(float(occ.mean()), 4),
            "median": round(float(occ.median()), 4),
        }

    return summary


# ---------------------------------------------------------------------------
# K-Means segmentation
# ---------------------------------------------------------------------------


def segment_listings_kmeans(df: pd.DataFrame, n_clusters: int = 4) -> pd.DataFrame:
    """
    Segment listings into business-meaningful clusters using K-Means.

    Features used (columns must exist; missing ones are filled with 0):
    - ``price``
    - ``estimated_annual_revenue``
    - ``demand_score``
    - ``estimated_occupancy_rate``

    Cluster labels are post-hoc assigned by matching each cluster centroid to
    a business-friendly name based on relative price and demand rank:

    ======================= ============================================
    Name                    Typical profile
    ======================= ============================================
    Budget/High-Demand      Low price, high demand/occupancy
    Premium/High-Revenue    High price, high revenue
    Budget/Low-Demand       Low price, low demand
    Luxury/Niche            Very high price, moderate/niche demand
    ======================= ============================================

    Parameters
    ----------
    df : pd.DataFrame
        Enriched listings DataFrame.
    n_clusters : int, optional
        Number of K-Means clusters (default ``4``).

    Returns
    -------
    pd.DataFrame
        Original DataFrame with two added columns:
        ``cluster_label`` (int) and ``cluster_name`` (str).

    Examples
    --------
    >>> segmented = segment_listings_kmeans(df)
    >>> segmented["cluster_name"].value_counts()
    """
    if df.empty:
        out = df.copy()
        out["cluster_label"] = pd.Series(dtype=int)
        out["cluster_name"] = pd.Series(dtype=str)
        return out

    feature_cols = [
        "price",
        "estimated_annual_revenue",
        "demand_score",
        "estimated_occupancy_rate",
    ]
    X_df = pd.DataFrame(
        {col: _safe_numeric(df, col) for col in feature_cols},
        index=df.index,
    ).fillna(0)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_df)

    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = km.fit_predict(X_scaled)

    # Assign business-friendly names based on centroid rank
    centroids = pd.DataFrame(
        scaler.inverse_transform(km.cluster_centers_),
        columns=feature_cols,
    )
    # Rank clusters by price (col 0) and demand_score (col 2)
    centroids["price_rank"] = centroids["price"].rank()
    centroids["demand_rank"] = centroids["demand_score"].rank()

    # Assign names heuristically based on relative position
    name_map: dict[int, str] = {}
    sorted_by_price = centroids["price_rank"].argsort().values  # indices sorted by ascending price
    sorted_by_demand = centroids["demand_rank"].argsort().values[::-1]  # desc demand

    if n_clusters == 4:
        # Lowest price & highest demand -> Budget/High-Demand
        # Highest price -> Luxury/Niche
        # Second highest price -> Premium/High-Revenue
        # Remaining -> Budget/Low-Demand
        price_sorted = centroids["price"].sort_values()
        idx_luxury = int(price_sorted.index[-1])
        idx_premium = int(price_sorted.index[-2])
        remaining = [i for i in range(n_clusters) if i not in (idx_luxury, idx_premium)]
        # Between the two remaining, higher demand -> Budget/High-Demand
        demand_remaining = centroids.loc[remaining, "demand_score"]
        idx_high_demand = int(demand_remaining.idxmax())
        idx_low_demand = int(demand_remaining.idxmin())
        name_map = {
            idx_high_demand: "Budget/High-Demand",
            idx_premium: "Premium/High-Revenue",
            idx_low_demand: "Budget/Low-Demand",
            idx_luxury: "Luxury/Niche",
        }
    else:
        # Generic fallback for non-4 cluster counts
        for i in range(n_clusters):
            name_map[i] = _CLUSTER_NAMES.get(i, f"Cluster {i}")

    out = df.copy()
    out["cluster_label"] = labels
    out["cluster_name"] = out["cluster_label"].map(name_map).fillna("Unknown")
    logger.info(
        "segment_listings_kmeans: assigned %d clusters to %d listings.",
        n_clusters,
        len(out),
    )
    return out


# ---------------------------------------------------------------------------
# Top / underpriced / overpriced
# ---------------------------------------------------------------------------


def get_top_listings(
    df: pd.DataFrame,
    metric: str = "estimated_annual_revenue",
    n: int = 20,
) -> pd.DataFrame:
    """
    Return the top-n listings sorted by the specified metric.

    Parameters
    ----------
    df : pd.DataFrame
        Enriched listings DataFrame.
    metric : str, optional
        Column name to sort by (default ``"estimated_annual_revenue"``).
    n : int, optional
        Number of rows to return (default ``20``).

    Returns
    -------
    pd.DataFrame
        Top-n listings sorted descending by ``metric``.
        Returns empty DataFrame if ``metric`` column is absent.
    """
    if df.empty or metric not in df.columns:
        logger.warning("get_top_listings: metric '%s' not in DataFrame.", metric)
        return pd.DataFrame()
    return (
        df.sort_values(metric, ascending=False)
        .head(n)
        .reset_index(drop=True)
    )


def get_underpriced_listings(
    df: pd.DataFrame,
    threshold: float = -50.0,
) -> pd.DataFrame:
    """
    Return listings where the pricing gap is below ``threshold`` (underpriced).

    A negative ``pricing_gap`` means the actual price is lower than the
    model's predicted fair price.

    Parameters
    ----------
    df : pd.DataFrame
        Enriched listings DataFrame with a ``pricing_gap`` column.
    threshold : float, optional
        Gap value below which a listing is considered underpriced (default ``-50``).

    Returns
    -------
    pd.DataFrame
        Filtered listing rows sorted by pricing_gap ascending (most underpriced first).
    """
    if "pricing_gap" not in df.columns:
        logger.warning("pricing_gap column not found; returning empty DataFrame.")
        return pd.DataFrame()
    mask = pd.to_numeric(df["pricing_gap"], errors="coerce") < threshold
    return df.loc[mask].sort_values("pricing_gap").reset_index(drop=True)


def get_overpriced_listings(
    df: pd.DataFrame,
    threshold: float = 50.0,
) -> pd.DataFrame:
    """
    Return listings where the pricing gap exceeds ``threshold`` (overpriced).

    A positive ``pricing_gap`` means the actual price is higher than the
    model's predicted fair price.

    Parameters
    ----------
    df : pd.DataFrame
        Enriched listings DataFrame with a ``pricing_gap`` column.
    threshold : float, optional
        Gap value above which a listing is considered overpriced (default ``50``).

    Returns
    -------
    pd.DataFrame
        Filtered listing rows sorted by pricing_gap descending (most overpriced first).
    """
    if "pricing_gap" not in df.columns:
        logger.warning("pricing_gap column not found; returning empty DataFrame.")
        return pd.DataFrame()
    mask = pd.to_numeric(df["pricing_gap"], errors="coerce") > threshold
    return df.loc[mask].sort_values("pricing_gap", ascending=False).reset_index(drop=True)


# ---------------------------------------------------------------------------
# Availability impact
# ---------------------------------------------------------------------------


def compute_availability_impact(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyse how availability levels affect estimated annual revenue.

    Listings are bucketed into four availability quartiles:
    - Very Low   (0-91 days available)
    - Low        (91-182 days available)
    - Medium     (182-273 days available)
    - High       (273-365 days available)

    Returns per-bucket aggregate statistics.

    Parameters
    ----------
    df : pd.DataFrame
        Enriched listings DataFrame.  Uses ``availability_365`` and
        ``estimated_annual_revenue``.

    Returns
    -------
    pd.DataFrame
        Columns: availability_bucket, listing_count, avg_availability,
        avg_revenue, median_revenue, avg_occupancy_rate, avg_price.
    """
    if df.empty or "availability_365" not in df.columns:
        return pd.DataFrame()

    avail = pd.to_numeric(df["availability_365"], errors="coerce").fillna(182)
    bins = [0, 91, 182, 273, 366]
    labels = ["Very Low (0-91)", "Low (91-182)", "Medium (182-273)", "High (273-365)"]
    avail_bucket = pd.cut(avail, bins=bins, labels=labels, right=False, include_lowest=True)

    tmp = df.copy()
    tmp["_avail_bucket"] = avail_bucket
    tmp["_avail_num"] = avail
    tmp["_rev"] = _safe_numeric(df, "estimated_annual_revenue")
    tmp["_occ"] = _safe_numeric(df, "estimated_occupancy_rate")
    tmp["_price"] = _safe_numeric(df, "price")

    agg = (
        tmp.groupby("_avail_bucket", observed=True)
        .agg(
            listing_count=("_avail_bucket", "count"),
            avg_availability=("_avail_num", "mean"),
            avg_revenue=("_rev", "mean"),
            median_revenue=("_rev", "median"),
            avg_occupancy_rate=("_occ", "mean"),
            avg_price=("_price", "mean"),
        )
        .reset_index()
        .rename(columns={"_avail_bucket": "availability_bucket"})
    )

    for col in ["avg_availability", "avg_revenue", "median_revenue", "avg_price"]:
        agg[col] = agg[col].round(2)
    agg["avg_occupancy_rate"] = agg["avg_occupancy_rate"].round(4)

    return agg
