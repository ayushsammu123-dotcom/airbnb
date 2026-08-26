"""
Tests for Airbnb Pricing & Revenue Analytics
=============================================
Run with: pytest tests/ -v
"""
import sys
import os
from pathlib import Path

# Ensure src/ is importable
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

import pytest
import pandas as pd
import numpy as np


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_raw_df():
    """Create a small raw DataFrame with known issues for testing cleaning."""
    np.random.seed(42)
    n = 200
    data = {
        "listing_id": list(range(1, n + 1)) + [5, 10],  # 2 duplicates
        "host_id": np.random.randint(1000, 2000, n + 2),
        "host_name": ["Host " + str(i) for i in range(n + 2)],
        "neighbourhood": np.random.choice(
            ["Manhattan", "Brooklyn", "Queens", "Bronx"], n + 2
        ),
        "neighbourhood_group": np.random.choice(
            ["Manhattan", "Brooklyn", "Queens", "Bronx"], n + 2
        ),
        "latitude": np.random.uniform(40.5, 40.9, n + 2),
        "longitude": np.random.uniform(-74.2, -73.7, n + 2),
        "room_type": np.random.choice(
            ["Entire home/apt", "Private room", "Shared room"], n + 2
        ),
        "property_type": np.random.choice(
            ["Apartment", "House", "Condo"], n + 2
        ),
        "price": list(np.random.uniform(50, 500, n - 3))
        + [-10, 0, 0, 5000, 4500],  # invalid prices, total n+2
        "minimum_nights": np.random.randint(1, 30, n + 2),
        "maximum_nights": np.full(n + 2, 365),
        "number_of_reviews": np.random.randint(0, 300, n + 2),
        "reviews_per_month": np.random.uniform(0, 5, n + 2),
        "review_rate_number": np.random.uniform(3, 5, n + 2),
        "availability_365": np.random.randint(0, 365, n + 2),
        "number_of_reviews_ltm": np.random.randint(0, 50, n + 2),
        "host_listings_count": np.random.randint(1, 20, n + 2),
        "host_is_superhost": np.random.choice([True, False], n + 2),
        "instant_bookable": np.random.choice([True, False], n + 2),
        "calculated_host_listings_count": np.random.randint(1, 20, n + 2),
        "last_review": ["2023-01-15"] * (n + 2),
        "license": [None] * (n + 2),
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_clean_df():
    """Create a pre-cleaned DataFrame for feature engineering and analysis tests."""
    np.random.seed(0)
    n = 500
    neighbourhoods = ["Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"]
    return pd.DataFrame(
        {
            "listing_id": range(1, n + 1),
            "host_id": np.random.randint(1000, 1200, n),
            "host_name": ["Host " + str(i % 100) for i in range(n)],
            "neighbourhood": np.random.choice(neighbourhoods, n),
            "neighbourhood_group": np.random.choice(
                ["Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"], n
            ),
            "latitude": np.random.uniform(40.55, 40.90, n),
            "longitude": np.random.uniform(-74.05, -73.75, n),
            "room_type": np.random.choice(
                ["Entire home/apt", "Private room", "Shared room", "Hotel room"],
                n,
                p=[0.55, 0.35, 0.05, 0.05],
            ),
            "property_type": np.random.choice(
                ["Apartment", "House", "Condo", "Loft", "Studio"], n
            ),
            "price": np.random.uniform(40, 600, n),
            "minimum_nights": np.random.randint(1, 15, n),
            "maximum_nights": np.full(n, 365),
            "number_of_reviews": np.random.randint(0, 400, n),
            "reviews_per_month": np.random.uniform(0.1, 8.0, n),
            "review_rate_number": np.random.uniform(3.0, 5.0, n),
            "availability_365": np.random.randint(0, 365, n),
            "number_of_reviews_ltm": np.random.randint(0, 60, n),
            "host_listings_count": np.random.randint(1, 15, n),
            "host_is_superhost": np.random.choice([True, False], n, p=[0.25, 0.75]),
            "instant_bookable": np.random.choice([True, False], n),
            "calculated_host_listings_count": np.random.randint(1, 15, n),
            "last_review": pd.to_datetime("2023-06-01"),
            "license": [None] * n,
        }
    )


# ---------------------------------------------------------------------------
# Data Cleaning Tests
# ---------------------------------------------------------------------------

class TestDataCleaning:
    """Tests for src/data_cleaning.py"""

    def test_import(self):
        from src.data_cleaning import DataCleaner, clean_data
        assert DataCleaner is not None
        assert clean_data is not None

    def test_removes_duplicates(self, sample_raw_df):
        from src.data_cleaning import DataCleaner
        cleaner = DataCleaner(sample_raw_df.copy())
        cleaned = cleaner.clean()
        # listing_ids 5 and 10 appeared twice each
        assert cleaned["listing_id"].duplicated().sum() == 0

    def test_removes_negative_prices(self, sample_raw_df):
        from src.data_cleaning import DataCleaner
        cleaner = DataCleaner(sample_raw_df.copy())
        cleaned = cleaner.clean()
        assert (cleaned["price"] <= 0).sum() == 0

    def test_removes_zero_prices(self, sample_raw_df):
        from src.data_cleaning import DataCleaner
        cleaner = DataCleaner(sample_raw_df.copy())
        cleaned = cleaner.clean()
        assert (cleaned["price"] == 0).sum() == 0

    def test_no_missing_price(self, sample_raw_df):
        from src.data_cleaning import DataCleaner
        cleaner = DataCleaner(sample_raw_df.copy())
        cleaned = cleaner.clean()
        assert cleaned["price"].isna().sum() == 0

    def test_cleaning_report_keys(self, sample_raw_df):
        from src.data_cleaning import DataCleaner
        cleaner = DataCleaner(sample_raw_df.copy())
        cleaner.clean()
        report = cleaner.generate_report()
        required_keys = [
            "original_rows",
            "final_rows",
            "duplicates_removed",
            "invalids_removed",
            "outliers_handled",
        ]
        for key in required_keys:
            assert key in report, f"Missing key in report: {key}"

    def test_original_row_count_in_report(self, sample_raw_df):
        from src.data_cleaning import DataCleaner
        cleaner = DataCleaner(sample_raw_df.copy())
        cleaner.clean()
        report = cleaner.generate_report()
        assert report["original_rows"] == len(sample_raw_df)

    def test_final_rows_less_than_original(self, sample_raw_df):
        from src.data_cleaning import DataCleaner
        cleaner = DataCleaner(sample_raw_df.copy())
        cleaned = cleaner.clean()
        report = cleaner.generate_report()
        assert report["final_rows"] <= report["original_rows"]
        assert report["final_rows"] == len(cleaned)

    def test_valid_coordinates(self, sample_raw_df):
        from src.data_cleaning import DataCleaner
        cleaner = DataCleaner(sample_raw_df.copy())
        cleaned = cleaner.clean()
        assert cleaned["latitude"].between(-90, 90).all()
        assert cleaned["longitude"].between(-180, 180).all()

    def test_price_always_positive(self, sample_raw_df):
        from src.data_cleaning import DataCleaner
        cleaner = DataCleaner(sample_raw_df.copy())
        cleaned = cleaner.clean()
        assert (cleaned["price"] > 0).all()


# ---------------------------------------------------------------------------
# Feature Engineering Tests
# ---------------------------------------------------------------------------

class TestFeatureEngineering:
    """Tests for src/feature_engineering.py"""

    def test_import(self):
        from src.feature_engineering import engineer_features, compute_demand_score
        assert engineer_features is not None
        assert compute_demand_score is not None

    def test_estimated_occupied_days_range(self, sample_clean_df):
        from src.feature_engineering import engineer_features
        df = engineer_features(sample_clean_df.copy())
        assert "estimated_occupied_days" in df.columns
        assert df["estimated_occupied_days"].between(0, 365).all()

    def test_estimated_occupancy_rate_range(self, sample_clean_df):
        from src.feature_engineering import engineer_features
        df = engineer_features(sample_clean_df.copy())
        assert "estimated_occupancy_rate" in df.columns
        assert df["estimated_occupancy_rate"].between(0, 1).all()

    def test_estimated_annual_revenue_non_negative(self, sample_clean_df):
        from src.feature_engineering import engineer_features
        df = engineer_features(sample_clean_df.copy())
        assert "estimated_annual_revenue" in df.columns
        assert (df["estimated_annual_revenue"] >= 0).all()

    def test_estimated_monthly_revenue_equals_annual_over_12(self, sample_clean_df):
        from src.feature_engineering import engineer_features
        df = engineer_features(sample_clean_df.copy())
        diff = (df["estimated_annual_revenue"] / 12 - df["estimated_monthly_revenue"]).abs()
        assert diff.max() < 0.01  # within rounding

    def test_price_category_values(self, sample_clean_df):
        from src.feature_engineering import engineer_features
        df = engineer_features(sample_clean_df.copy())
        valid_categories = {"Budget", "Mid-Range", "Premium", "Luxury"}
        assert set(df["price_category"].dropna().unique()).issubset(valid_categories)

    def test_occupancy_category_values(self, sample_clean_df):
        from src.feature_engineering import engineer_features
        df = engineer_features(sample_clean_df.copy())
        valid_categories = {"Low", "Medium", "High"}
        assert set(df["occupancy_category"].dropna().unique()).issubset(valid_categories)

    def test_host_category_values(self, sample_clean_df):
        from src.feature_engineering import engineer_features
        df = engineer_features(sample_clean_df.copy())
        valid_categories = {"Single-Property", "Multi-Property"}
        assert set(df["host_category"].dropna().unique()).issubset(valid_categories)

    def test_demand_score_range(self, sample_clean_df):
        from src.feature_engineering import engineer_features, compute_demand_score
        df = engineer_features(sample_clean_df.copy())
        scores = compute_demand_score(df)
        assert scores.between(0, 100).all()

    def test_demand_score_length(self, sample_clean_df):
        from src.feature_engineering import engineer_features, compute_demand_score
        df = engineer_features(sample_clean_df.copy())
        scores = compute_demand_score(df)
        assert len(scores) == len(df)


# ---------------------------------------------------------------------------
# Revenue Calculation Tests
# ---------------------------------------------------------------------------

class TestRevenueCalculations:
    """Verify revenue estimation methodology is correct."""

    def test_revenue_formula(self, sample_clean_df):
        """estimated_annual_revenue = price * estimated_occupied_days"""
        from src.feature_engineering import engineer_features
        df = engineer_features(sample_clean_df.copy())
        expected = df["price"] * df["estimated_occupied_days"]
        diff = (df["estimated_annual_revenue"] - expected).abs()
        assert diff.max() < 0.01

    def test_occupied_days_formula(self, sample_clean_df):
        """estimated_occupied_days = 365 - availability_365"""
        from src.feature_engineering import engineer_features
        df = engineer_features(sample_clean_df.copy())
        expected = (365 - df["availability_365"]).clip(0, 365)
        diff = (df["estimated_occupied_days"] - expected).abs()
        assert diff.max() < 0.01

    def test_occupancy_rate_formula(self, sample_clean_df):
        """estimated_occupancy_rate = estimated_occupied_days / 365"""
        from src.feature_engineering import engineer_features
        df = engineer_features(sample_clean_df.copy())
        expected = df["estimated_occupied_days"] / 365
        diff = (df["estimated_occupancy_rate"] - expected).abs()
        assert diff.max() < 0.001

    def test_zero_availability_means_full_revenue(self, sample_clean_df):
        """A listing with 0 availability has max occupied days."""
        from src.feature_engineering import engineer_features
        df = sample_clean_df.copy()
        df["availability_365"] = 0
        df = engineer_features(df)
        assert (df["estimated_occupied_days"] == 365).all()

    def test_full_availability_means_zero_revenue(self, sample_clean_df):
        """A listing with 365 availability has 0 estimated occupied days."""
        from src.feature_engineering import engineer_features
        df = sample_clean_df.copy()
        df["availability_365"] = 365
        df = engineer_features(df)
        assert (df["estimated_occupied_days"] == 0).all()
        assert (df["estimated_annual_revenue"] == 0).all()


# ---------------------------------------------------------------------------
# Analysis Tests
# ---------------------------------------------------------------------------

class TestAnalysis:
    """Tests for src/analysis.py"""

    def test_import(self):
        from src.analysis import (
            compute_neighbourhood_stats,
            compute_room_type_stats,
            compute_price_correlation,
        )
        assert compute_neighbourhood_stats is not None

    def test_neighbourhood_stats_columns(self, sample_clean_df):
        from src.feature_engineering import engineer_features
        from src.analysis import compute_neighbourhood_stats
        df = engineer_features(sample_clean_df.copy())
        stats = compute_neighbourhood_stats(df)
        assert "neighbourhood" in stats.columns
        assert "avg_price" in stats.columns
        assert "listing_count" in stats.columns

    def test_room_type_stats_columns(self, sample_clean_df):
        from src.feature_engineering import engineer_features
        from src.analysis import compute_room_type_stats
        df = engineer_features(sample_clean_df.copy())
        stats = compute_room_type_stats(df)
        assert "room_type" in stats.columns
        assert "avg_price" in stats.columns

    def test_price_correlation_returns_dataframe(self, sample_clean_df):
        from src.feature_engineering import engineer_features
        from src.analysis import compute_price_correlation
        df = engineer_features(sample_clean_df.copy())
        corr = compute_price_correlation(df)
        assert isinstance(corr, pd.DataFrame)
        assert len(corr) > 0

    def test_get_top_listings_returns_n_rows(self, sample_clean_df):
        from src.feature_engineering import engineer_features
        from src.analysis import get_top_listings
        df = engineer_features(sample_clean_df.copy())
        top = get_top_listings(df, metric="estimated_annual_revenue", n=10)
        assert len(top) <= 10

    def test_neighbourhood_stats_count_positive(self, sample_clean_df):
        from src.feature_engineering import engineer_features
        from src.analysis import compute_neighbourhood_stats
        df = engineer_features(sample_clean_df.copy())
        stats = compute_neighbourhood_stats(df)
        assert (stats["listing_count"] > 0).all()


# ---------------------------------------------------------------------------
# Utils Tests
# ---------------------------------------------------------------------------

class TestUtils:
    """Tests for src/utils.py"""

    def test_import(self):
        from src.utils import (
            format_currency,
            format_number,
            format_percentage,
            get_price_category,
            get_occupancy_category,
        )
        assert format_currency is not None

    def test_format_currency(self):
        from src.utils import format_currency
        result = format_currency(1500.5)
        assert "₹" in result
        assert "1,500" in result or "1500" in result

    def test_format_number(self):
        from src.utils import format_number
        result = format_number(12345.678, decimals=0)
        assert "12" in result

    def test_format_percentage(self):
        from src.utils import format_percentage
        result = format_percentage(0.756)
        assert "%" in result

    def test_price_category_budget(self):
        from src.utils import get_price_category
        assert get_price_category(1500) == "Budget"

    def test_price_category_mid_range(self):
        from src.utils import get_price_category
        assert get_price_category(4000) == "Mid-Range"

    def test_price_category_premium(self):
        from src.utils import get_price_category
        assert get_price_category(10000) == "Premium"

    def test_price_category_luxury(self):
        from src.utils import get_price_category
        assert get_price_category(25000) == "Luxury"

    def test_occupancy_category_low(self):
        from src.utils import get_occupancy_category
        assert get_occupancy_category(0.1) == "Low"

    def test_occupancy_category_medium(self):
        from src.utils import get_occupancy_category
        assert get_occupancy_category(0.5) == "Medium"

    def test_occupancy_category_high(self):
        from src.utils import get_occupancy_category
        assert get_occupancy_category(0.8) == "High"

    def test_compute_revenue_metrics(self, sample_clean_df):
        from src.feature_engineering import engineer_features
        from src.utils import compute_revenue_metrics
        df = engineer_features(sample_clean_df.copy())
        metrics = compute_revenue_metrics(df)
        assert "total_listings" in metrics
        assert "avg_price" in metrics
        assert metrics["total_listings"] == len(df)
        assert metrics["avg_price"] > 0


# ---------------------------------------------------------------------------
# Database Tests
# ---------------------------------------------------------------------------

class TestDatabase:
    """Tests for src/database.py"""

    def test_import(self):
        from src.database import AirbnbDatabase, initialize_database
        assert AirbnbDatabase is not None

    def test_database_creation(self, sample_clean_df, tmp_path):
        from src.feature_engineering import engineer_features
        from src.database import AirbnbDatabase
        df = engineer_features(sample_clean_df.copy())
        db_path = str(tmp_path / "test.db")
        db = AirbnbDatabase(db_path=db_path)
        db.create_tables()
        db.load_data(df)
        result = db.execute_query("SELECT COUNT(*) as cnt FROM listings")
        assert result["cnt"].iloc[0] == len(df)
        db.close()

    def test_query_returns_dataframe(self, sample_clean_df, tmp_path):
        from src.feature_engineering import engineer_features
        from src.database import AirbnbDatabase
        df = engineer_features(sample_clean_df.copy())
        db_path = str(tmp_path / "test2.db")
        db = AirbnbDatabase(db_path=db_path)
        db.create_tables()
        db.load_data(df)
        result = db.execute_query("SELECT * FROM listings LIMIT 10")
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 10
        db.close()

    def test_neighbourhood_stats(self, sample_clean_df, tmp_path):
        from src.feature_engineering import engineer_features
        from src.database import AirbnbDatabase
        df = engineer_features(sample_clean_df.copy())
        db_path = str(tmp_path / "test3.db")
        db = AirbnbDatabase(db_path=db_path)
        db.create_tables()
        db.load_data(df)
        stats = db.get_neighbourhood_stats()
        assert isinstance(stats, pd.DataFrame)
        assert len(stats) > 0
        db.close()


# ---------------------------------------------------------------------------
# Pricing Category Tests
# ---------------------------------------------------------------------------

class TestPricingCategories:
    """Verify pricing categorization logic."""

    @pytest.mark.parametrize(
        "price,expected",
        [
            (2000.0, "Budget"),
            (3499.99, "Budget"),
            (3500.0, "Mid-Range"),
            (7999.99, "Mid-Range"),
            (8000.0, "Premium"),
            (19999.99, "Premium"),
            (20000.0, "Luxury"),
            (65000.0, "Luxury"),
        ],
    )
    def test_price_category_boundaries(self, price, expected):
        from src.utils import get_price_category
        assert get_price_category(price) == expected

    @pytest.mark.parametrize(
        "rate,expected",
        [
            (0.1, "Low"),
            (0.29, "Low"),
            (0.30, "Medium"),
            (0.59, "Medium"),
            (0.60, "High"),
            (1.0, "High"),
        ],
    )
    def test_occupancy_category_boundaries(self, rate, expected):
        from src.utils import get_occupancy_category
        assert get_occupancy_category(rate) == expected


# ---------------------------------------------------------------------------
# Data Validation Tests
# ---------------------------------------------------------------------------

class TestDataValidation:
    """Validate data integrity constraints."""

    def test_listing_ids_unique_after_cleaning(self, sample_raw_df):
        from src.data_cleaning import DataCleaner
        cleaner = DataCleaner(sample_raw_df.copy())
        cleaned = cleaner.clean()
        assert cleaned["listing_id"].nunique() == len(cleaned)

    def test_no_null_listing_ids(self, sample_raw_df):
        from src.data_cleaning import DataCleaner
        cleaner = DataCleaner(sample_raw_df.copy())
        cleaned = cleaner.clean()
        assert cleaned["listing_id"].isna().sum() == 0

    def test_room_types_are_known(self, sample_raw_df):
        from src.data_cleaning import DataCleaner
        known_types = {
            "Entire home/apt",
            "Private room",
            "Shared room",
            "Hotel room",
        }
        cleaner = DataCleaner(sample_raw_df.copy())
        cleaned = cleaner.clean()
        cleaned_types = set(cleaned["room_type"].dropna().unique())
        assert cleaned_types.issubset(known_types)

    def test_availability_in_range(self, sample_clean_df):
        from src.feature_engineering import engineer_features
        df = engineer_features(sample_clean_df.copy())
        assert df["estimated_occupied_days"].between(0, 365).all()

    def test_occupancy_rate_between_0_and_1(self, sample_clean_df):
        from src.feature_engineering import engineer_features
        df = engineer_features(sample_clean_df.copy())
        assert df["estimated_occupancy_rate"].between(0, 1).all()


# ---------------------------------------------------------------------------
# Aggregation Tests
# ---------------------------------------------------------------------------

class TestAggregations:
    """Test that aggregation functions return correct results."""

    def test_neighbourhood_avg_price_is_positive(self, sample_clean_df):
        from src.feature_engineering import engineer_features
        from src.analysis import compute_neighbourhood_stats
        df = engineer_features(sample_clean_df.copy())
        stats = compute_neighbourhood_stats(df)
        assert (stats["avg_price"] > 0).all()

    def test_total_listings_in_metrics(self, sample_clean_df):
        from src.feature_engineering import engineer_features
        from src.utils import compute_revenue_metrics
        df = engineer_features(sample_clean_df.copy())
        metrics = compute_revenue_metrics(df)
        assert metrics["total_listings"] == 500

    def test_host_stats_aggregation(self, sample_clean_df):
        from src.feature_engineering import engineer_features
        from src.analysis import compute_host_stats
        df = engineer_features(sample_clean_df.copy())
        stats = compute_host_stats(df)
        assert "host_id" in stats.columns
        assert "avg_price" in stats.columns
        assert len(stats) <= len(df)  # fewer hosts than listings

    def test_property_type_stats(self, sample_clean_df):
        from src.feature_engineering import engineer_features
        from src.analysis import compute_property_type_stats
        df = engineer_features(sample_clean_df.copy())
        stats = compute_property_type_stats(df)
        assert "property_type" in stats.columns
        assert "avg_price" in stats.columns


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
