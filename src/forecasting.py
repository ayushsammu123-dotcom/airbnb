"""
src/forecasting.py
==================
ML-based pricing models for the Airbnb Pricing & Revenue Analytics project.

The ``PricingModel`` class trains three regression models on listing features
to predict fair nightly prices.  Predictions are used to compute pricing gaps
(actual − predicted) that power the underpriced/overpriced analysis layer.

Models
------
- Linear Regression          — fast baseline
- Random Forest Regressor    — ensemble, handles non-linearity
- Gradient Boosting Regressor — sequential boosting, typically best performer

All models are trained with log-transformed prices to reduce right-skew and
evaluated on original scale (exponentiating predictions back before metric
computation).

Module-level ``train_pricing_model()`` is the standard entry-point.
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Feature / target configuration
# ---------------------------------------------------------------------------

_CATEGORICAL_FEATURES: list[str] = ["room_type", "neighbourhood", "host_is_superhost"]
_NUMERIC_FEATURES: list[str] = [
    "minimum_nights",
    "availability_365",
    "number_of_reviews",
    "reviews_per_month",
    "host_listings_count",
    "latitude",
    "longitude",
]
_ALL_FEATURES: list[str] = _CATEGORICAL_FEATURES + _NUMERIC_FEATURES
_TARGET: str = "price"


class PricingModel:
    """
    Trains, evaluates, and applies multiple regression pricing models.

    After calling ``train_all_models(df)``, the instance stores all trained
    models, their evaluation metrics, and the label encoders used during
    feature preparation.  Use ``predict_prices()`` and ``compute_pricing_gaps()``
    to add ML-derived columns back to the listing DataFrame.

    Attributes
    ----------
    results : dict
        Keyed by model name.  Each value is a dict with keys:
        ``model``, ``metrics``, ``feature_names``.
    _encoders : dict[str, LabelEncoder]
        Fitted label encoders for categorical features.
    _best_model_name : str
        Name of the model with the lowest MAE on the test set.

    Examples
    --------
    >>> pm = train_pricing_model(enriched_df)
    >>> enriched_df["predicted_price"] = pm.predict_prices(enriched_df)
    >>> enriched_df["pricing_gap"]     = pm.compute_pricing_gaps(enriched_df)
    """

    def __init__(self) -> None:
        self.results: dict[str, Any] = {}
        self._encoders: dict[str, LabelEncoder] = {}
        self._best_model_name: str = ""

    # ------------------------------------------------------------------
    # Feature preparation
    # ------------------------------------------------------------------

    def prepare_features(
        self,
        df: pd.DataFrame,
        fit_encoders: bool = False,
    ) -> tuple[np.ndarray, np.ndarray, list[str]]:
        """
        Build the feature matrix X and target vector y for model training.

        Categorical features (``room_type``, ``neighbourhood``,
        ``host_is_superhost``) are integer-encoded with ``LabelEncoder``.
        Numeric features are coerced and NaN-filled with column medians.

        The target (``price``) is log-transformed via ``log1p`` to reduce
        right-skew and stabilise variance.

        Parameters
        ----------
        df : pd.DataFrame
            Listings DataFrame containing at least ``price`` and the feature
            columns listed in ``_ALL_FEATURES``.
        fit_encoders : bool, optional
            If ``True``, fit new ``LabelEncoder`` instances (training phase).
            If ``False``, use already-fitted encoders (inference phase).
            Defaults to ``False``; callers must pass ``True`` during training.

        Returns
        -------
        tuple[np.ndarray, np.ndarray, list[str]]
            ``(X, y, feature_names)`` where X has shape ``(n_samples, n_features)``
            and y has shape ``(n_samples,)`` (log-transformed prices).

        Raises
        ------
        ValueError
            If the DataFrame is empty or the ``price`` column is absent.
        """
        if df.empty or _TARGET not in df.columns:
            raise ValueError("DataFrame must be non-empty and contain a 'price' column.")

        work = df.copy()

        # Filter to valid prices
        work = work[pd.to_numeric(work[_TARGET], errors="coerce") > 0].copy()
        if work.empty:
            raise ValueError("No rows with valid (> 0) price after filtering.")

        y = np.log1p(pd.to_numeric(work[_TARGET], errors="coerce").values)

        feature_frames: list[pd.Series] = []
        feature_names: list[str] = []

        # Encode categoricals
        for col in _CATEGORICAL_FEATURES:
            if col in work.columns:
                series = work[col].astype(str).fillna("Unknown")
                if fit_encoders:
                    enc = LabelEncoder()
                    encoded = enc.fit_transform(series)
                    self._encoders[col] = enc
                else:
                    enc = self._encoders.get(col)
                    if enc is None:
                        # Fallback: fit on-the-fly
                        enc = LabelEncoder()
                        encoded = enc.fit_transform(series)
                        self._encoders[col] = enc
                    else:
                        # Handle unseen labels gracefully
                        known = set(enc.classes_)
                        series = series.apply(
                            lambda x: x if x in known else enc.classes_[0]
                        )
                        encoded = enc.transform(series)
                feature_frames.append(pd.Series(encoded, name=col, index=work.index))
                feature_names.append(col)
            else:
                feature_frames.append(pd.Series(np.zeros(len(work)), name=col, index=work.index))
                feature_names.append(col)

        # Numeric features
        for col in _NUMERIC_FEATURES:
            if col in work.columns:
                num = pd.to_numeric(work[col], errors="coerce")
                num = num.fillna(num.median() if num.notna().any() else 0)
            else:
                num = pd.Series(np.zeros(len(work)), index=work.index)
            feature_frames.append(num.rename(col))
            feature_names.append(col)

        X = np.column_stack([s.values for s in feature_frames])
        return X, y, feature_names

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------

    def train_all_models(self, df: pd.DataFrame) -> dict:
        """
        Train LinearRegression, RandomForest, and GradientBoosting models.

        An 80/20 stratification-free split (``random_state=42``) is used.
        All models share the same train/test split for fair comparison.

        Parameters
        ----------
        df : pd.DataFrame
            Enriched listings DataFrame used for training.

        Returns
        -------
        dict
            Nested results dict keyed by model name:
            ``{"model": ..., "metrics": {...}, "feature_names": [...]}``
            The same dict is stored in ``self.results``.

        Notes
        -----
        After this method, ``self._best_model_name`` is set to the model
        with the lowest test-set MAE.
        """
        logger.info("Preparing features for model training …")
        X, y, feature_names = self.prepare_features(df, fit_encoders=True)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.20, random_state=42
        )
        logger.info(
            "Train size: %d  |  Test size: %d  |  Features: %d",
            len(X_train),
            len(X_test),
            X.shape[1],
        )

        model_specs: dict[str, Any] = {
            "LinearRegression": LinearRegression(),
            "RandomForestRegressor": RandomForestRegressor(
                n_estimators=100, random_state=42, n_jobs=-1
            ),
            "GradientBoostingRegressor": GradientBoostingRegressor(
                n_estimators=100, random_state=42, learning_rate=0.1, max_depth=4
            ),
        }

        for name, model in model_specs.items():
            logger.info("Training %s …", name)
            model.fit(X_train, y_train)
            metrics = self.evaluate_model(model, X_test, y_test)
            self.results[name] = {
                "model": model,
                "metrics": metrics,
                "feature_names": feature_names,
            }
            logger.info(
                "%s  |  MAE=%.2f  RMSE=%.2f  R2=%.4f",
                name,
                metrics["mae"],
                metrics["rmse"],
                metrics["r2"],
            )

        # Pick best by lowest MAE
        self._best_model_name = min(
            self.results, key=lambda n: self.results[n]["metrics"]["mae"]
        )
        logger.info("Best model: %s (MAE=%.2f)", self._best_model_name, self.results[self._best_model_name]["metrics"]["mae"])
        return self.results

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------

    def evaluate_model(
        self,
        model: Any,
        X_test: np.ndarray,
        y_test: np.ndarray,
    ) -> dict:
        """
        Compute MAE, RMSE, and R2 on the original (non-log) price scale.

        Parameters
        ----------
        model
            A fitted sklearn-compatible estimator.
        X_test : np.ndarray
            Test feature matrix.
        y_test : np.ndarray
            Log-transformed test target values.

        Returns
        -------
        dict
            Keys: ``mae``, ``rmse``, ``r2`` — all on original price scale.
        """
        y_pred_log = model.predict(X_test)
        # Exponentiate back to original price scale
        y_pred = np.expm1(y_pred_log)
        y_true = np.expm1(y_test)

        mae = float(mean_absolute_error(y_true, y_pred))
        rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
        r2 = float(r2_score(y_true, y_pred))

        return {"mae": round(mae, 4), "rmse": round(rmse, 4), "r2": round(r2, 4)}

    # ------------------------------------------------------------------
    # Feature importance
    # ------------------------------------------------------------------

    def get_feature_importance(
        self,
        model: Any,
        feature_names: list[str],
    ) -> pd.DataFrame:
        """
        Extract feature importances from a tree-based or linear model.

        For tree-based models (Random Forest, Gradient Boosting) returns
        ``feature_importances_``.  For linear models returns absolute
        coefficient magnitudes.  Falls back to a zero-filled DataFrame if
        neither attribute is present.

        Parameters
        ----------
        model
            A fitted sklearn-compatible estimator.
        feature_names : list[str]
            Names corresponding to the columns of the training matrix.

        Returns
        -------
        pd.DataFrame
            Columns: ``feature``, ``importance``.
            Sorted by importance descending.
        """
        if hasattr(model, "feature_importances_"):
            importances = model.feature_importances_
        elif hasattr(model, "coef_"):
            importances = np.abs(model.coef_)
        else:
            importances = np.zeros(len(feature_names))

        result = pd.DataFrame(
            {"feature": feature_names, "importance": importances}
        ).sort_values("importance", ascending=False).reset_index(drop=True)
        result["importance"] = result["importance"].round(6)
        return result

    # ------------------------------------------------------------------
    # Inference
    # ------------------------------------------------------------------

    def predict_prices(self, df: pd.DataFrame) -> pd.Series:
        """
        Predict fair nightly prices for all listings using the best model.

        Parameters
        ----------
        df : pd.DataFrame
            Listings DataFrame.  Does not need to contain ``price``.

        Returns
        -------
        pd.Series
            Predicted prices (original scale, USD).  Named ``"predicted_price"``.
            Returns a zero Series if no model has been trained yet.
        """
        if not self.results or not self._best_model_name:
            logger.warning("No trained model available; returning zero predictions.")
            return pd.Series(np.zeros(len(df)), index=df.index, name="predicted_price")

        model = self.results[self._best_model_name]["model"]
        feature_names = self.results[self._best_model_name]["feature_names"]

        # We call prepare_features in inference mode (fit_encoders=False)
        # but we need a dummy price column to avoid ValueError
        work = df.copy()
        if _TARGET not in work.columns:
            work[_TARGET] = 100.0  # dummy; y is not used during inference

        try:
            X, _, _ = self.prepare_features(work, fit_encoders=False)
            y_pred_log = model.predict(X)
            predicted = pd.Series(
                np.expm1(y_pred_log).clip(min=1.0),
                index=work.index,
                name="predicted_price",
            ).round(2)
        except Exception as exc:  # noqa: BLE001
            logger.error("Prediction failed: %s — returning zeros.", exc)
            predicted = pd.Series(np.zeros(len(df)), index=df.index, name="predicted_price")

        return predicted

    def compute_pricing_gaps(self, df: pd.DataFrame) -> pd.Series:
        """
        Compute the pricing gap for each listing: ``actual_price - predicted_price``.

        Positive gap  => overpriced relative to model prediction.
        Negative gap  => underpriced relative to model prediction.

        Parameters
        ----------
        df : pd.DataFrame
            Listings DataFrame with a ``price`` column.

        Returns
        -------
        pd.Series
            Pricing gaps in USD, named ``"pricing_gap"``.
        """
        predicted = self.predict_prices(df)
        actual = pd.to_numeric(df.get("price", pd.Series(0.0, index=df.index)), errors="coerce").fillna(0)
        gap = (actual - predicted).round(2)
        gap.name = "pricing_gap"
        return gap

    def get_best_model_name(self) -> str:
        """
        Return the name of the best-performing model by lowest MAE.

        Returns
        -------
        str
            Model name, or empty string if no models have been trained.
        """
        return self._best_model_name


# ---------------------------------------------------------------------------
# Module-level convenience function
# ---------------------------------------------------------------------------


def train_pricing_model(df: pd.DataFrame) -> PricingModel:
    """
    Train all pricing models on the provided DataFrame.

    Uses an 80/20 train/test split internally.  Prints a summary table of
    model metrics to the log.

    Parameters
    ----------
    df : pd.DataFrame
        Enriched listings DataFrame.  Should be the output of
        ``feature_engineering.engineer_features()``.

    Returns
    -------
    PricingModel
        Fully trained instance.  Call ``.predict_prices(df)`` and
        ``.compute_pricing_gaps(df)`` to derive ML columns.

    Examples
    --------
    >>> pm = train_pricing_model(enriched_df)
    >>> enriched_df["predicted_price"] = pm.predict_prices(enriched_df)
    >>> enriched_df["pricing_gap"]     = pm.compute_pricing_gaps(enriched_df)
    >>> enriched_df["pricing_opportunity"] = enriched_df["pricing_gap"].apply(
    ...     lambda g: "Underpriced" if g < -50 else ("Overpriced" if g > 50 else "Fairly Priced")
    ... )
    >>> print("Best model:", pm.get_best_model_name())
    """
    if df.empty:
        raise ValueError("Cannot train pricing model on an empty DataFrame.")

    pm = PricingModel()
    pm.train_all_models(df)

    # Log a summary table
    logger.info("=" * 55)
    logger.info("%-30s %8s %8s %8s", "Model", "MAE", "RMSE", "R2")
    logger.info("-" * 55)
    for name, res in pm.results.items():
        m = res["metrics"]
        logger.info("%-30s %8.2f %8.2f %8.4f", name, m["mae"], m["rmse"], m["r2"])
    logger.info("=" * 55)
    logger.info("Best model: %s", pm.get_best_model_name())

    return pm
