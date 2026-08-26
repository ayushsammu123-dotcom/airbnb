"""
src/utils.py
============
Shared utilities for the Airbnb Pricing & Revenue Analytics project.

Provides:
- Domain constants (neighbourhoods, room types, categories, color maps)
- Formatting helpers (currency, number, percentage)
- Business-logic helpers (price/occupancy category)
- Revenue metric aggregation
- Processed-data loader with graceful error handling
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Project root (two levels up from this file: src/ -> project root)
# ---------------------------------------------------------------------------
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Domain constants
# ---------------------------------------------------------------------------

NEIGHBOURHOODS: list[str] = [
    # South Delhi
    "Hauz Khas Village",
    "Greater Kailash",
    "Saket",
    "Vasant Kunj",
    "Defense Colony",
    "Green Park",
    "Chattarpur",
    # Central Delhi
    "Connaught Place",
    "Chanakyapuri",
    "Karol Bagh",
    "Paharganj",
    # Gurugram (Gurgaon)
    "Golf Course Road (DLF 5)",
    "Cyber City",
    "Sector 29",
    "Sohna Road",
    "Sushant Lok",
    # Noida & Greater Noida
    "Sector 18 Noida",
    "Sector 62 Noida",
    "Sector 137 Expressway",
    "Greater Noida (Pari Chowk)",
    # West & North Delhi
    "Aerocity (IGI Airport)",
    "Dwarka",
    "Rajouri Garden",
    "Civil Lines",
    "Rohini",
    # Faridabad & Ghaziabad
    "Indirapuram",
    "Sector 15 Faridabad",
]

ROOM_TYPES: list[str] = [
    "Entire home/apt",
    "Private room",
    "Shared room",
    "Hotel room",
]

PROPERTY_TYPES: list[str] = [
    "Apartment",
    "House",
    "Condo",
    "Loft",
    "Studio",
    "Townhouse",
    "Boutique Hotel",
    "Guesthouse",
    "Villa",
    "Hostel",
]

PRICE_CATEGORIES: list[str] = ["Budget", "Mid-Range", "Premium", "Luxury"]

# Plotly/matplotlib-friendly color map for categories and clusters
COLOR_MAP: dict[str, str] = {
    # Price categories (Green: Low/Budget -> Orange: Mid-Range -> Wine Red: High/Luxury)
    "Budget": "#10B981",        # Emerald Green (Low price)
    "Mid-Range": "#F59E0B",     # Warm Orange (Mid price)
    "Premium": "#E11D48",       # Crimson Red (Premium)
    "Luxury": "#881337",        # Deep Wine Red (Luxury)
    # Occupancy categories
    "Low": "#881337",           # Wine Red
    "Medium": "#F59E0B",        # Orange
    "High": "#10B981",          # Green
    # Host categories
    "Single-Property": "#06B6D4",
    "Multi-Property": "#8B5CF6",
    # Cluster names
    "Budget/High-Demand": "#10B981",
    "Premium/High-Revenue": "#E11D48",
    "Budget/Low-Demand": "#94A3B8",
    "Luxury/Niche": "#881337",
    # Pricing opportunity
    "Underpriced": "#10B981",   # Green
    "Fairly Priced": "#F59E0B", # Orange
    "Overpriced": "#881337",    # Wine Red
    # Delhi NCR Zones
    "South Delhi": "#FF385C",
    "Central Delhi": "#6366F1",
    "Gurugram": "#10B981",
    "Noida": "#F59E0B",
    "Greater Noida": "#06B6D4",
    "West & North Delhi": "#8B5CF6",
    "Ghaziabad": "#EC4899",
    "Faridabad": "#14B8A6",
}

# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------


def format_currency(value: float) -> str:
    """
    Format a numeric value as an INR (₹) currency string.

    Parameters
    ----------
    value : float
        Monetary value to format in INR.

    Returns
    -------
    str
        Formatted string, e.g. ``"₹1,234.50"``.
        Returns ``"N/A"`` for non-finite or None values.
    """
    try:
        return f"₹{float(value):,.2f}"
    except (TypeError, ValueError):
        return "N/A"


def format_number(value: float, decimals: int = 0) -> str:
    """
    Format a numeric value with thousands separators.
    """
    try:
        return f"{float(value):,.{decimals}f}"
    except (TypeError, ValueError):
        return "N/A"


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Format a fractional value (0-1) as a percentage string.
    """
    try:
        return f"{float(value) * 100:.{decimals}f}%"
    except (TypeError, ValueError):
        return "N/A"


# ---------------------------------------------------------------------------
# Business-logic helpers (INR Scale)
# ---------------------------------------------------------------------------


def get_price_category(price: float) -> str:
    """
    Bucket a nightly price in INR into a human-readable tier.

    Tiers (INR ₹)
    -------------
    - **Budget**    : price < ₹3,500
    - **Mid-Range** : ₹3,500 <= price < ₹8,000
    - **Premium**   : ₹8,000 <= price < ₹20,000
    - **Luxury**    : price >= ₹20,000

    Parameters
    ----------
    price : float
        Nightly listing price in INR (₹).

    Returns
    -------
    str
        One of ``"Budget"``, ``"Mid-Range"``, ``"Premium"``, ``"Luxury"``,
        or ``"Unknown"`` for invalid inputs.
    """
    try:
        p = float(price)
    except (TypeError, ValueError):
        return "Unknown"

    if p < 3500:
        return "Budget"
    if p < 8000:
        return "Mid-Range"
    if p < 20000:
        return "Premium"
    return "Luxury"


def get_occupancy_category(rate: float) -> str:
    """
    Classify an occupancy rate into a human-readable tier.

    Tiers
    -----
    - **Low**    : rate < 0.30
    - **Medium** : 0.30 <= rate <= 0.60
    - **High**   : rate > 0.60

    Parameters
    ----------
    rate : float
        Occupancy rate in [0, 1].

    Returns
    -------
    str
        One of ``"Low"``, ``"Medium"``, ``"High"``, or ``"Unknown"``.

    Examples
    --------
    >>> get_occupancy_category(0.25)
    'Low'
    >>> get_occupancy_category(0.75)
    'High'
    """
    try:
        r = float(rate)
    except (TypeError, ValueError):
        return "Unknown"

    if r < 0.30:
        return "Low"
    if r < 0.60:
        return "Medium"
    return "High"


# ---------------------------------------------------------------------------
# Revenue metric aggregation
# ---------------------------------------------------------------------------


def compute_revenue_metrics(df: pd.DataFrame) -> dict:
    """
    Compute top-level revenue KPIs from the processed listings DataFrame.

    Expected columns (non-exhaustive):
    - ``listing_id``              -- unique listing identifier
    - ``host_id``                 -- host identifier
    - ``price``                   -- nightly price in USD
    - ``estimated_annual_revenue``-- pre-engineered revenue column (optional)
    - ``estimated_occupancy_rate``-- pre-engineered occupancy column (optional)

    Parameters
    ----------
    df : pd.DataFrame
        Listings DataFrame, typically the cleaned + feature-engineered dataset.

    Returns
    -------
    dict
        Keys:
        ``total_listings``, ``total_hosts``, ``avg_price``, ``median_price``,
        ``total_est_annual_revenue``, ``avg_occupancy``.

    Raises
    ------
    ValueError
        If ``df`` is empty.

    Examples
    --------
    >>> metrics = compute_revenue_metrics(df)
    >>> metrics['avg_price']
    152.4
    """
    if df.empty:
        raise ValueError("Cannot compute revenue metrics on an empty DataFrame.")

    total_listings: int = (
        int(df["listing_id"].nunique()) if "listing_id" in df.columns else len(df)
    )
    total_hosts: int = (
        int(df["host_id"].nunique()) if "host_id" in df.columns else 0
    )

    price_series = (
        pd.to_numeric(df["price"], errors="coerce")
        if "price" in df.columns
        else pd.Series(dtype=float)
    )
    avg_price: float = float(price_series.mean()) if not price_series.empty else 0.0
    median_price: float = float(price_series.median()) if not price_series.empty else 0.0

    if "estimated_annual_revenue" in df.columns:
        total_est_annual_revenue: float = float(
            pd.to_numeric(df["estimated_annual_revenue"], errors="coerce").sum()
        )
    elif "availability_365" in df.columns:
        occupied = (
            365 - pd.to_numeric(df["availability_365"], errors="coerce")
        ).clip(0, 365)
        total_est_annual_revenue = float((price_series * occupied).sum())
    else:
        total_est_annual_revenue = 0.0

    if "estimated_occupancy_rate" in df.columns:
        avg_occupancy: float = float(
            pd.to_numeric(df["estimated_occupancy_rate"], errors="coerce").mean()
        )
    elif "availability_365" in df.columns:
        avg_occupancy = float(
            ((365 - pd.to_numeric(df["availability_365"], errors="coerce")) / 365).mean()
        )
    else:
        avg_occupancy = 0.0

    return {
        "total_listings": total_listings,
        "total_hosts": total_hosts,
        "avg_price": round(avg_price, 2),
        "median_price": round(median_price, 2),
        "total_est_annual_revenue": round(total_est_annual_revenue, 2),
        "avg_occupancy": round(avg_occupancy, 4),
    }


# ---------------------------------------------------------------------------
# Data loader
# ---------------------------------------------------------------------------


def load_processed_data(
    path: str = "data/processed/airbnb_cleaned.csv",
) -> pd.DataFrame:
    """
    Load the cleaned/processed Airbnb CSV into a DataFrame.

    Tries the path as-is first; if that fails, resolves it relative to
    ``PROJECT_ROOT`` so callers can use project-relative paths regardless of
    the current working directory.

    Parameters
    ----------
    path : str, optional
        Path to the processed CSV file.  May be absolute or relative to the
        project root.  Defaults to ``"data/processed/airbnb_cleaned.csv"``.

    Returns
    -------
    pd.DataFrame
        Loaded DataFrame.  Returns an empty DataFrame (with a warning) if
        the file cannot be found or parsed.

    Examples
    --------
    >>> df = load_processed_data()
    >>> df.shape
    (9800, 25)
    """
    file_path = Path(path)
    if not file_path.is_absolute():
        file_path = PROJECT_ROOT / path

    if not file_path.exists():
        logger.warning(
            "Processed data file not found: %s — returning empty DataFrame.",
            file_path,
        )
        return pd.DataFrame()

    try:
        df = pd.read_csv(file_path, low_memory=False)
        logger.info("Loaded %d rows from %s", len(df), file_path)
        return df
    except Exception as exc:  # noqa: BLE001
        logger.error(
            "Failed to read %s: %s — returning empty DataFrame.", file_path, exc
        )
        return pd.DataFrame()
