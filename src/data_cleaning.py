"""
src/data_cleaning.py
====================
Full data-cleaning pipeline for the Airbnb Pricing & Revenue Analytics project.

The ``DataCleaner`` class encapsulates every cleaning step and accumulates a
rich report dictionary so downstream consumers (dashboards, logs) can inspect
exactly what was removed or imputed.

The module-level ``clean_data()`` function is the standard entry-point:
it loads raw data, cleans it, saves the result, and returns both the cleaned
DataFrame and the report.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import pandas as pd
import numpy as np

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Project root
# ---------------------------------------------------------------------------
_PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent


class DataCleaner:
    """
    Orchestrates a multi-step cleaning pipeline for raw Airbnb listing data.

    Each private ``_clean_*`` / ``_remove_*`` / ``_normalize_*`` method
    performs one focused transformation and updates ``self.report`` with
    before/after statistics.  Call ``clean()`` to execute the full sequence.

    Parameters
    ----------
    df : pd.DataFrame
        Raw listings DataFrame as loaded from CSV.

    Attributes
    ----------
    df : pd.DataFrame
        The working DataFrame (mutated in-place by each step).
    report : dict
        Cleaning statistics accumulated across all steps.

    Examples
    --------
    >>> cleaner = DataCleaner(raw_df)
    >>> clean_df = cleaner.clean()
    >>> print(cleaner.generate_report())
    """

    def __init__(self, df: pd.DataFrame) -> None:
        self.df: pd.DataFrame = df.copy()
        self.report: dict[str, Any] = {
            "initial_rows": len(df),
            "initial_columns": len(df.columns),
            "steps": {},
        }

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def clean(self) -> pd.DataFrame:
        """
        Execute the full cleaning pipeline in the correct order.

        Steps (in order):
        1. Remove invalid IDs
        2. Remove duplicates
        3. Clean data types (parse dates, coerce numerics)
        4. Clean prices (remove zeros/negatives, cap outliers)
        5. Clean coordinates (validate lat/lon)
        6. Handle missing values (impute medians / modes)
        7. Normalise categoricals (consistent casing)

        Returns
        -------
        pd.DataFrame
            The fully cleaned DataFrame.
        """
        logger.info("Starting data cleaning pipeline. Initial rows: %d", len(self.df))
        self._remove_invalid_ids()
        self._remove_duplicates()
        self._clean_data_types()
        self._clean_prices()
        self._clean_coordinates()
        self._handle_missing_values()
        self._normalize_categoricals()

        self.report["final_rows"] = len(self.df)
        self.report["final_columns"] = len(self.df.columns)
        self.report["total_rows_removed"] = (
            self.report["initial_rows"] - self.report["final_rows"]
        )
        logger.info(
            "Cleaning complete. Final rows: %d (removed %d).",
            self.report["final_rows"],
            self.report["total_rows_removed"],
        )
        return self.df

    # ------------------------------------------------------------------
    # Step 1 — remove invalid IDs
    # ------------------------------------------------------------------

    def _remove_invalid_ids(self) -> None:
        """
        Drop rows where ``listing_id`` or ``host_id`` is null.

        These rows are fundamentally unusable — every downstream join and
        aggregation depends on valid identifiers.

        Updates
        -------
        ``self.report["steps"]["remove_invalid_ids"]`` with count removed.
        """
        before = len(self.df)
        id_cols = [c for c in ["listing_id", "host_id"] if c in self.df.columns]
        if id_cols:
            self.df.dropna(subset=id_cols, inplace=True)
        removed = before - len(self.df)
        self.report["steps"]["remove_invalid_ids"] = {
            "rows_before": before,
            "rows_after": len(self.df),
            "rows_removed": removed,
        }
        logger.info("remove_invalid_ids: removed %d rows with null IDs.", removed)

    # ------------------------------------------------------------------
    # Step 2 — remove duplicates
    # ------------------------------------------------------------------

    def _remove_duplicates(self) -> None:
        """
        Remove duplicate rows keyed on ``listing_id``.

        The first occurrence of each ``listing_id`` is kept; subsequent ones
        are dropped.  If ``listing_id`` is absent, falls back to full-row
        deduplication.

        Updates
        -------
        ``self.report["steps"]["remove_duplicates"]`` with count removed.
        """
        before = len(self.df)
        if "listing_id" in self.df.columns:
            self.df.drop_duplicates(subset=["listing_id"], keep="first", inplace=True)
        else:
            self.df.drop_duplicates(inplace=True)
        removed = before - len(self.df)
        self.report["steps"]["remove_duplicates"] = {
            "rows_before": before,
            "rows_after": len(self.df),
            "rows_removed": removed,
        }
        logger.info("remove_duplicates: removed %d duplicate rows.", removed)

    # ------------------------------------------------------------------
    # Step 3 — data type normalisation
    # ------------------------------------------------------------------

    def _clean_data_types(self) -> None:
        """
        Coerce columns to their canonical dtypes.

        - ``last_review``: parsed as datetime (errors -> NaT)
        - Numeric columns: ``price``, ``minimum_nights``, ``maximum_nights``,
          ``number_of_reviews``, ``reviews_per_month``, ``availability_365``,
          ``host_listings_count``, ``calculated_host_listings_count``,
          ``number_of_reviews_ltm``, ``review_rate_number``,
          ``latitude``, ``longitude``  — coerced with ``errors='coerce'``
        - Boolean columns: ``host_is_superhost``, ``instant_bookable``
          mapped from string variants (``"t"``/``"f"``, ``"True"``/``"False"``)
          to Python bool.

        Updates
        -------
        ``self.report["steps"]["clean_data_types"]`` with columns processed.
        """
        processed: dict[str, str] = {}

        # Date columns
        date_cols = ["last_review"]
        for col in date_cols:
            if col in self.df.columns:
                self.df[col] = pd.to_datetime(self.df[col], errors="coerce")
                processed[col] = "datetime"

        # Numeric columns
        numeric_cols = [
            "price",
            "minimum_nights",
            "maximum_nights",
            "number_of_reviews",
            "reviews_per_month",
            "availability_365",
            "host_listings_count",
            "calculated_host_listings_count",
            "number_of_reviews_ltm",
            "review_rate_number",
            "latitude",
            "longitude",
        ]
        for col in numeric_cols:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors="coerce")
                processed[col] = "numeric"

        # Boolean columns
        bool_true_vals = {"t", "true", "1", "yes"}
        bool_false_vals = {"f", "false", "0", "no"}
        bool_cols = ["host_is_superhost", "instant_bookable"]
        for col in bool_cols:
            if col in self.df.columns:
                str_col = self.df[col].astype(str).str.strip().str.lower()
                self.df[col] = str_col.map(
                    lambda x: True if x in bool_true_vals else (False if x in bool_false_vals else None)  # noqa: E731
                )
                processed[col] = "bool"

        self.report["steps"]["clean_data_types"] = {"columns_processed": processed}
        logger.info("clean_data_types: processed %d columns.", len(processed))

    # ------------------------------------------------------------------
    # Step 4 — price cleaning
    # ------------------------------------------------------------------

    def _clean_prices(self) -> None:
        """
        Remove invalid price rows and cap high outliers.

        - Rows with ``price <= 0`` or ``price`` is NaN are dropped.
        - Prices above the 99th percentile are capped to that value (Winsorising),
          preventing extreme outliers from distorting revenue estimates.

        Updates
        -------
        ``self.report["steps"]["clean_prices"]`` with counts and the cap value.
        """
        if "price" not in self.df.columns:
            self.report["steps"]["clean_prices"] = {"skipped": "price column not found"}
            return

        before = len(self.df)
        self.df = self.df[self.df["price"].notna() & (self.df["price"] > 0)].copy()
        invalid_removed = before - len(self.df)

        # Cap at 99th percentile
        cap_value = float(self.df["price"].quantile(0.99))
        outliers_capped = int((self.df["price"] > cap_value).sum())
        self.df["price"] = self.df["price"].clip(upper=cap_value)

        self.report["steps"]["clean_prices"] = {
            "rows_before": before,
            "rows_after": len(self.df),
            "invalid_price_rows_removed": invalid_removed,
            "outlier_cap_value": round(cap_value, 2),
            "prices_capped": outliers_capped,
        }
        logger.info(
            "clean_prices: removed %d invalid-price rows; capped %d outliers at $%.2f.",
            invalid_removed,
            outliers_capped,
            cap_value,
        )

    # ------------------------------------------------------------------
    # Step 5 — coordinate validation
    # ------------------------------------------------------------------

    def _clean_coordinates(self) -> None:
        """
        Validate geographic coordinates for New York City bounds.

        Valid ranges:
        - ``latitude`` : [40.4774, 40.9176]
        - ``longitude``: [-74.2591, -73.7004]

        Rows outside these bounds are dropped.

        Updates
        -------
        ``self.report["steps"]["clean_coordinates"]`` with count removed.
        """
        lat_col, lon_col = "latitude", "longitude"
        if lat_col not in self.df.columns or lon_col not in self.df.columns:
            self.report["steps"]["clean_coordinates"] = {
                "skipped": "lat/lon columns not found"
            }
            return

        before = len(self.df)
        lat_valid = self.df[lat_col].between(-90.0, 90.0) & self.df[lat_col].notna()
        lon_valid = self.df[lon_col].between(-180.0, 180.0) & self.df[lon_col].notna()
        self.df = self.df[lat_valid & lon_valid].copy()
        removed = before - len(self.df)

        self.report["steps"]["clean_coordinates"] = {
            "rows_before": before,
            "rows_after": len(self.df),
            "rows_removed": removed,
        }
        logger.info("clean_coordinates: removed %d rows with invalid coordinates.", removed)

    # ------------------------------------------------------------------
    # Step 6 — missing value imputation
    # ------------------------------------------------------------------

    def _handle_missing_values(self) -> None:
        """
        Impute missing values using domain-appropriate strategies.

        Strategy
        --------
        - ``reviews_per_month``       : fill 0 (no reviews yet)
        - ``number_of_reviews``       : fill 0
        - ``number_of_reviews_ltm``   : fill 0
        - ``availability_365``        : fill median
        - ``minimum_nights``          : fill median
        - ``host_listings_count``     : fill median
        - ``calculated_host_listings_count`` : fill from ``host_listings_count`` else median
        - ``review_rate_number``      : fill median
        - ``host_is_superhost``       : fill False
        - ``instant_bookable``        : fill False
        - ``neighbourhood_group``     : fill mode
        - ``room_type``               : fill mode
        - ``property_type``           : fill mode
        - ``last_review``             : left as NaT (intentional absence)

        Updates
        -------
        ``self.report["steps"]["handle_missing_values"]`` with per-column counts.
        """
        imputed: dict[str, Any] = {}

        def _fill(col: str, value: Any) -> None:
            if col in self.df.columns:
                n_missing = int(self.df[col].isna().sum())
                if n_missing > 0:
                    self.df[col] = self.df[col].fillna(value)
                    imputed[col] = {"strategy": "constant", "value": str(value), "filled": n_missing}

        def _fill_median(col: str) -> None:
            if col in self.df.columns:
                n_missing = int(self.df[col].isna().sum())
                if n_missing > 0:
                    med = self.df[col].median()
                    self.df[col] = self.df[col].fillna(med)
                    imputed[col] = {
                        "strategy": "median",
                        "value": round(float(med), 4),
                        "filled": n_missing,
                    }

        def _fill_mode(col: str) -> None:
            if col in self.df.columns:
                n_missing = int(self.df[col].isna().sum())
                if n_missing > 0:
                    mode_val = self.df[col].mode(dropna=True)
                    if not mode_val.empty:
                        self.df[col] = self.df[col].fillna(mode_val.iloc[0])
                        imputed[col] = {
                            "strategy": "mode",
                            "value": str(mode_val.iloc[0]),
                            "filled": n_missing,
                        }

        # Zero-fill for review counts (missing = not yet reviewed)
        for col in ["reviews_per_month", "number_of_reviews", "number_of_reviews_ltm"]:
            _fill(col, 0)

        # Median-fill for numeric columns
        for col in [
            "availability_365",
            "minimum_nights",
            "host_listings_count",
            "review_rate_number",
        ]:
            _fill_median(col)

        # calculated_host_listings_count mirrors host_listings_count
        if (
            "calculated_host_listings_count" in self.df.columns
            and "host_listings_count" in self.df.columns
        ):
            mask = self.df["calculated_host_listings_count"].isna()
            n_missing = int(mask.sum())
            if n_missing > 0:
                self.df.loc[mask, "calculated_host_listings_count"] = self.df.loc[
                    mask, "host_listings_count"
                ]
                imputed["calculated_host_listings_count"] = {
                    "strategy": "from host_listings_count",
                    "filled": n_missing,
                }
            _fill_median("calculated_host_listings_count")

        # Boolean defaults
        _fill("host_is_superhost", False)
        _fill("instant_bookable", False)

        # Categorical mode-fill
        for col in ["neighbourhood_group", "room_type", "property_type"]:
            _fill_mode(col)

        self.report["steps"]["handle_missing_values"] = {"columns_imputed": imputed}
        logger.info("handle_missing_values: imputed values in %d columns.", len(imputed))

    # ------------------------------------------------------------------
    # Step 7 — categorical normalisation
    # ------------------------------------------------------------------

    def _normalize_categoricals(self) -> None:
        """
        Standardise string formatting for categorical columns.

        Transformations
        ---------------
        - ``room_type``      : ``str.strip().str.title()``
        - ``property_type``  : ``str.strip().str.title()``
        - ``neighbourhood``  : ``str.strip().str.title()``
        - ``neighbourhood_group`` : ``str.strip().str.title()``

        Updates
        -------
        ``self.report["steps"]["normalize_categoricals"]`` with columns touched.
        """
        if "room_type" in self.df.columns:
            rt_map = {
                "entire home/apt": "Entire home/apt",
                "entire home": "Entire home/apt",
                "entire apt": "Entire home/apt",
                "entire home/apartment": "Entire home/apt",
                "private room": "Private room",
                "shared room": "Shared room",
                "hotel room": "Hotel room",
            }
            self.df["room_type"] = (
                self.df["room_type"]
                .astype(str)
                .str.strip()
                .str.lower()
                .map(lambda x: rt_map.get(x, x.title()))
            )

        cat_cols = ["property_type", "neighbourhood", "neighbourhood_group"]
        normalised = ["room_type"] if "room_type" in self.df.columns else []
        for col in cat_cols:
            if col in self.df.columns:
                self.df[col] = (
                    self.df[col].astype(str).str.strip().str.title()
                )
                normalised.append(col)

        self.report["steps"]["normalize_categoricals"] = {"columns_normalised": normalised}
        logger.info("normalize_categoricals: normalised %d columns.", len(normalised))

    # ------------------------------------------------------------------
    # Report
    # ------------------------------------------------------------------

    def generate_report(self) -> dict:
        """
        Return the accumulated cleaning report.

        Returns
        -------
        dict
            Contains ``original_rows``, ``final_rows``, ``duplicates_removed``,
            ``invalids_removed``, ``outliers_handled``, and detailed ``steps``.
        """
        steps = self.report.get("steps", {})
        dups_removed = steps.get("remove_duplicates", {}).get("rows_removed", 0)
        invalid_ids = steps.get("remove_invalid_ids", {}).get("rows_removed", 0)
        invalid_prices = steps.get("clean_prices", {}).get("invalid_price_rows_removed", 0)
        invalid_coords = steps.get("clean_coordinates", {}).get("rows_removed", 0)
        outliers = steps.get("clean_prices", {}).get("outliers_capped", 0)

        self.report["original_rows"] = self.report.get("initial_rows", len(self.df))
        self.report["final_rows"] = self.report.get("final_rows", len(self.df))
        self.report["duplicates_removed"] = dups_removed
        self.report["invalids_removed"] = invalid_ids + invalid_prices + invalid_coords
        self.report["outliers_handled"] = outliers
        self.report["total_rows_removed"] = self.report["original_rows"] - self.report["final_rows"]

        return self.report


# ---------------------------------------------------------------------------
# Module-level convenience function
# ---------------------------------------------------------------------------


def clean_data(
    input_path: str,
    output_path: str,
) -> tuple[pd.DataFrame, dict]:
    """
    Load raw data, run the cleaning pipeline, save the result, and return both.

    This is the standard entry-point for batch ETL jobs.

    Parameters
    ----------
    input_path : str
        Absolute or project-relative path to the raw CSV file.
    output_path : str
        Absolute or project-relative path where the cleaned CSV will be saved.
        Parent directories are created automatically.

    Returns
    -------
    tuple[pd.DataFrame, dict]
        ``(cleaned_df, cleaning_report)``

    Raises
    ------
    FileNotFoundError
        If ``input_path`` does not resolve to an existing file.
    ValueError
        If the cleaned DataFrame is empty after all cleaning steps.

    Examples
    --------
    >>> df, report = clean_data(
    ...     "data/raw/synthetic_airbnb.csv",
    ...     "data/processed/airbnb_cleaned.csv",
    ... )
    >>> report["total_rows_removed"]
    213
    """
    # Resolve paths relative to project root if not absolute
    in_path = Path(input_path)
    if not in_path.is_absolute():
        in_path = _PROJECT_ROOT / input_path

    out_path = Path(output_path)
    if not out_path.is_absolute():
        out_path = _PROJECT_ROOT / output_path

    if not in_path.exists():
        raise FileNotFoundError(f"Input file not found: {in_path}")

    logger.info("Loading raw data from %s", in_path)
    raw_df = pd.read_csv(in_path, low_memory=False)
    logger.info("Raw data loaded: %d rows, %d columns.", len(raw_df), len(raw_df.columns))

    cleaner = DataCleaner(raw_df)
    cleaned_df = cleaner.clean()
    report = cleaner.generate_report()

    if cleaned_df.empty:
        raise ValueError("Cleaning pipeline produced an empty DataFrame.")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    cleaned_df.to_csv(out_path, index=False)
    logger.info("Cleaned data saved to %s (%d rows).", out_path, len(cleaned_df))

    return cleaned_df, report
