"""
src/database.py
===============
SQLite database management for the Airbnb Pricing & Revenue Analytics project.

The ``AirbnbDatabase`` class wraps a SQLite connection and provides:
- Schema creation (listings, hosts, neighbourhoods, cleaning_report tables)
- Bulk data loading from a DataFrame
- Parameterised query execution
- Named analysis queries loaded from the ``sql/`` folder
- Pre-built aggregation helpers

Module-level ``initialize_database()`` is the standard entry-point for
one-shot setup (create schema + load data).
"""

from __future__ import annotations

import json
import logging
import sqlite3
from pathlib import Path
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)

_PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# DDL statements
# ---------------------------------------------------------------------------

_DDL_LISTINGS = """
CREATE TABLE IF NOT EXISTS listings (
    listing_id                      INTEGER PRIMARY KEY,
    host_id                         INTEGER,
    host_name                       TEXT,
    neighbourhood                   TEXT,
    neighbourhood_group             TEXT,
    latitude                        REAL,
    longitude                       REAL,
    room_type                       TEXT,
    property_type                   TEXT,
    price                           REAL,
    minimum_nights                  INTEGER,
    maximum_nights                  INTEGER,
    number_of_reviews               INTEGER,
    reviews_per_month               REAL,
    review_rate_number              REAL,
    availability_365                INTEGER,
    number_of_reviews_ltm           INTEGER,
    host_listings_count             INTEGER,
    calculated_host_listings_count  INTEGER,
    host_is_superhost               INTEGER,
    instant_bookable                INTEGER,
    last_review                     TEXT,
    license                         TEXT,
    -- Engineered features
    estimated_occupied_days         REAL,
    estimated_occupancy_rate        REAL,
    estimated_annual_revenue        REAL,
    estimated_monthly_revenue       REAL,
    revenue_per_available_day       REAL,
    price_category                  TEXT,
    occupancy_category              TEXT,
    host_category                   TEXT,
    pricing_gap                     REAL,
    pricing_opportunity             TEXT,
    demand_score                    REAL,
    host_performance_score          REAL,
    location_score                  REAL,
    price_competitiveness           REAL
);
"""

_DDL_HOSTS = """
CREATE TABLE IF NOT EXISTS hosts (
    host_id             INTEGER PRIMARY KEY,
    host_name           TEXT,
    host_listings_count INTEGER,
    is_superhost        INTEGER,
    avg_price           REAL,
    avg_reviews_per_month REAL,
    total_annual_revenue REAL,
    host_category       TEXT
);
"""

_DDL_NEIGHBOURHOODS = """
CREATE TABLE IF NOT EXISTS neighbourhoods (
    neighbourhood       TEXT PRIMARY KEY,
    neighbourhood_group TEXT,
    listing_count       INTEGER,
    avg_price           REAL,
    median_price        REAL,
    avg_reviews         REAL,
    avg_occupancy_rate  REAL,
    total_revenue       REAL
);
"""

_DDL_CLEANING_REPORT = """
CREATE TABLE IF NOT EXISTS cleaning_report (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at  TEXT DEFAULT (datetime('now')),
    report_json TEXT
);
"""


class AirbnbDatabase:
    """
    Manages the project's SQLite database.

    Parameters
    ----------
    db_path : str or Path, optional
        Absolute or project-relative path to the ``.db`` file.
        Defaults to ``data/airbnb.db`` relative to the project root.
        Parent directories are created automatically.

    Attributes
    ----------
    db_path : Path
        Resolved absolute path to the database file.
    conn : sqlite3.Connection
        Active database connection.

    Examples
    --------
    >>> db = AirbnbDatabase()
    >>> db.create_tables()
    >>> db.load_data(enriched_df)
    >>> stats = db.get_neighbourhood_stats()
    >>> db.close()
    """

    def __init__(self, db_path: str | Path | None = None) -> None:
        if db_path is None:
            self.db_path: Path = _PROJECT_ROOT / "data" / "airbnb.db"
        else:
            p = Path(db_path)
            self.db_path = p if p.is_absolute() else _PROJECT_ROOT / p

        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn: sqlite3.Connection = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        # Enable WAL mode for better concurrent read performance
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.execute("PRAGMA foreign_keys=ON;")
        logger.info("Connected to database at %s", self.db_path)

    # ------------------------------------------------------------------
    # Schema
    # ------------------------------------------------------------------

    def create_tables(self) -> None:
        """
        Create all project tables (idempotent — uses ``CREATE TABLE IF NOT EXISTS``).

        Tables created:
        - ``listings``         — full listing data + engineered features
        - ``hosts``            — host-level aggregates
        - ``neighbourhoods``   — neighbourhood-level aggregates
        - ``cleaning_report``  — JSON blobs from the DataCleaner report
        """
        cursor = self.conn.cursor()
        for ddl in [_DDL_LISTINGS, _DDL_HOSTS, _DDL_NEIGHBOURHOODS, _DDL_CLEANING_REPORT]:
            cursor.executescript(ddl)
        self.conn.commit()
        logger.info("Database tables created / verified.")

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------

    def load_data(self, df: pd.DataFrame) -> None:
        """
        Insert (or replace) all DataFrame rows into the ``listings`` table.

        Columns in ``df`` that don't match table columns are silently ignored.
        Boolean columns are converted to 0/1 for SQLite compatibility.
        Datetime columns are converted to ISO strings.

        Parameters
        ----------
        df : pd.DataFrame
            Enriched listings DataFrame (cleaned + feature-engineered).

        Raises
        ------
        ValueError
            If ``df`` is empty.
        """
        if df.empty:
            raise ValueError("Cannot load an empty DataFrame into the database.")

        load_df = df.copy()

        # Convert booleans to int
        for col in load_df.select_dtypes(include="bool").columns:
            load_df[col] = load_df[col].astype(int)

        # Convert datetimes to str
        for col in load_df.select_dtypes(include=["datetime64[ns]", "datetimetz"]).columns:
            load_df[col] = load_df[col].astype(str)

        load_df.to_sql(
            "listings",
            self.conn,
            if_exists="replace",
            index=False,
            chunksize=1000,
        )
        self.conn.commit()
        logger.info("Loaded %d rows into listings table.", len(load_df))

        # Populate aggregated tables
        self._populate_host_table(load_df)
        self._populate_neighbourhood_table(load_df)

    def _populate_host_table(self, df: pd.DataFrame) -> None:
        """Compute and insert host-level aggregates into the ``hosts`` table."""
        if "host_id" not in df.columns:
            return

        def _safe(col: str) -> pd.Series:
            if col in df.columns:
                return pd.to_numeric(df[col], errors="coerce").fillna(0)
            return pd.Series(0.0, index=df.index)

        host_df = (
            df.assign(
                _price=_safe("price"),
                _rpm=_safe("reviews_per_month"),
                _rev=_safe("estimated_annual_revenue"),
            )
            .groupby("host_id")
            .agg(
                host_name=("host_name", "first") if "host_name" in df.columns else ("host_id", "first"),
                host_listings_count=("host_id", "count"),
                is_superhost=("host_is_superhost", "first") if "host_is_superhost" in df.columns else ("host_id", lambda x: 0),
                avg_price=("_price", "mean"),
                avg_reviews_per_month=("_rpm", "mean"),
                total_annual_revenue=("_rev", "sum"),
                host_category=("host_category", "first") if "host_category" in df.columns else ("host_id", lambda x: "Single-Property"),
            )
            .reset_index()
        )

        # Convert booleans
        for col in host_df.select_dtypes(include="bool").columns:
            host_df[col] = host_df[col].astype(int)

        host_df.to_sql("hosts", self.conn, if_exists="replace", index=False)
        self.conn.commit()
        logger.info("Populated hosts table with %d records.", len(host_df))

    def _populate_neighbourhood_table(self, df: pd.DataFrame) -> None:
        """Compute and insert neighbourhood-level aggregates into the ``neighbourhoods`` table."""
        nbhd_col = "neighbourhood"
        if nbhd_col not in df.columns:
            return

        def _safe(col: str) -> pd.Series:
            if col in df.columns:
                return pd.to_numeric(df[col], errors="coerce").fillna(0)
            return pd.Series(0.0, index=df.index)

        nbhd_df = (
            df.assign(
                _price=_safe("price"),
                _reviews=_safe("number_of_reviews"),
                _occ=_safe("estimated_occupancy_rate"),
                _rev=_safe("estimated_annual_revenue"),
            )
            .groupby(nbhd_col)
            .agg(
                neighbourhood_group=("neighbourhood_group", "first") if "neighbourhood_group" in df.columns else (nbhd_col, lambda x: "Unknown"),
                listing_count=(nbhd_col, "count"),
                avg_price=("_price", "mean"),
                median_price=("_price", "median"),
                avg_reviews=("_reviews", "mean"),
                avg_occupancy_rate=("_occ", "mean"),
                total_revenue=("_rev", "sum"),
            )
            .reset_index()
        )

        nbhd_df.to_sql("neighbourhoods", self.conn, if_exists="replace", index=False)
        self.conn.commit()
        logger.info("Populated neighbourhoods table with %d records.", len(nbhd_df))

    # ------------------------------------------------------------------
    # Query execution
    # ------------------------------------------------------------------

    def execute_query(self, sql: str, params: tuple = ()) -> pd.DataFrame:
        """
        Execute an arbitrary SQL query and return results as a DataFrame.

        Parameters
        ----------
        sql : str
            SQL query string.  Use ``?`` placeholders for parameters.
        params : tuple, optional
            Parameters for the query placeholders.

        Returns
        -------
        pd.DataFrame
            Query result.  Empty DataFrame if the query returns no rows.

        Examples
        --------
        >>> df = db.execute_query("SELECT * FROM listings WHERE price > ?", (200,))
        """
        try:
            return pd.read_sql_query(sql, self.conn, params=params)
        except Exception as exc:  # noqa: BLE001
            logger.error("Query execution failed: %s\nSQL: %s", exc, sql)
            return pd.DataFrame()

    def run_analysis_query(self, name: str) -> pd.DataFrame:
        """
        Load and execute a named SQL file from the project's ``sql/`` folder.

        The file is expected at ``<project_root>/sql/<name>.sql``.

        Parameters
        ----------
        name : str
            Name of the SQL file (without the ``.sql`` extension).

        Returns
        -------
        pd.DataFrame
            Query results, or an empty DataFrame if the file is not found.

        Examples
        --------
        >>> db.run_analysis_query("top_revenue_listings")
        """
        sql_path = _PROJECT_ROOT / "sql" / f"{name}.sql"
        if not sql_path.exists():
            logger.warning("Analysis query file not found: %s", sql_path)
            return pd.DataFrame()
        sql = sql_path.read_text(encoding="utf-8")
        logger.info("Running analysis query: %s", name)
        return self.execute_query(sql)

    # ------------------------------------------------------------------
    # Pre-built aggregation helpers
    # ------------------------------------------------------------------

    def get_neighbourhood_stats(self) -> pd.DataFrame:
        """
        Return all neighbourhood-level aggregates from the ``neighbourhoods`` table.

        Returns
        -------
        pd.DataFrame
            Columns: neighbourhood, neighbourhood_group, listing_count,
            avg_price, median_price, avg_reviews, avg_occupancy_rate, total_revenue.
        """
        return self.execute_query(
            "SELECT * FROM neighbourhoods ORDER BY total_revenue DESC"
        )

    def get_room_type_stats(self) -> pd.DataFrame:
        """
        Return aggregated statistics by room type from the ``listings`` table.

        Returns
        -------
        pd.DataFrame
            Columns: room_type, listing_count, avg_price, median_price,
            avg_occupancy_rate, total_revenue.
        """
        sql = """
        SELECT
            room_type,
            COUNT(*)                        AS listing_count,
            ROUND(AVG(price), 2)            AS avg_price,
            ROUND(AVG(estimated_occupancy_rate), 4) AS avg_occupancy_rate,
            ROUND(SUM(estimated_annual_revenue), 2) AS total_revenue
        FROM listings
        WHERE room_type IS NOT NULL
        GROUP BY room_type
        ORDER BY total_revenue DESC
        """
        return self.execute_query(sql)

    def get_host_stats(self) -> pd.DataFrame:
        """
        Return all host-level records from the ``hosts`` table ordered by revenue.

        Returns
        -------
        pd.DataFrame
        """
        return self.execute_query(
            "SELECT * FROM hosts ORDER BY total_annual_revenue DESC"
        )

    def get_top_revenue_listings(self, n: int = 10) -> pd.DataFrame:
        """
        Return the top-n listings by estimated annual revenue.

        Parameters
        ----------
        n : int, optional
            Number of listings to return (default ``10``).

        Returns
        -------
        pd.DataFrame
            Subset of the listings table with key revenue columns.
        """
        sql = """
        SELECT
            listing_id,
            neighbourhood,
            room_type,
            property_type,
            price,
            estimated_occupancy_rate,
            estimated_annual_revenue,
            demand_score,
            price_category
        FROM listings
        ORDER BY estimated_annual_revenue DESC
        LIMIT ?
        """
        return self.execute_query(sql, params=(n,))

    def save_cleaning_report(self, report: dict) -> None:
        """
        Persist a cleaning report dictionary as a JSON blob in the database.

        Parameters
        ----------
        report : dict
            The report dictionary from ``DataCleaner.generate_report()``.
        """
        report_json = json.dumps(report, default=str)
        self.conn.execute(
            "INSERT INTO cleaning_report (report_json) VALUES (?)", (report_json,)
        )
        self.conn.commit()
        logger.info("Cleaning report saved to database.")

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def close(self) -> None:
        """
        Close the database connection gracefully.

        After calling ``close()``, this instance should not be used.
        """
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed.")


# ---------------------------------------------------------------------------
# Module-level convenience function
# ---------------------------------------------------------------------------


def initialize_database(
    df: pd.DataFrame,
    db_path: str | Path | None = None,
) -> AirbnbDatabase:
    """
    Create the database, set up the schema, and load data in one call.

    Parameters
    ----------
    df : pd.DataFrame
        Enriched listings DataFrame to load.
    db_path : str or Path, optional
        Path to the SQLite file.  Defaults to ``data/airbnb.db``.

    Returns
    -------
    AirbnbDatabase
        Fully initialised and loaded database instance.
        The caller is responsible for calling ``.close()`` when done.

    Examples
    --------
    >>> db = initialize_database(enriched_df)
    >>> stats = db.get_neighbourhood_stats()
    >>> db.close()
    """
    db = AirbnbDatabase(db_path)
    db.create_tables()
    db.load_data(df)
    logger.info("Database initialised at %s with %d listings.", db.db_path, len(df))
    return db
