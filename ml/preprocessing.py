"""
Airfare Intelligence Platform — ML Preprocessing Pipeline
Phase 3: ML Training

Defines the feature engineering and preprocessing pipeline for fare prediction.
Features are selected based on domain relevance — not blindly from column list.

NOTE: Flight number is NOT used as a predictive feature (too specific, leaks).
"""

import logging
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (
    LabelEncoder,
    OneHotEncoder,
    OrdinalEncoder,
    StandardScaler,
)

logger = logging.getLogger(__name__)

# ── Feature definitions ───────────────────────────────────────

# Categorical features (OneHotEncoded)
CAT_FEATURES = [
    "airline",
    "origin",
    "destination",
    "cabin_class",
]

# Ordinal features (have a natural order)
ORD_FEATURES = ["stops"]  # 0, 1, 2, 3

# Numerical features
NUM_FEATURES = [
    "duration_minutes",
    "days_left",
]

# Time features (extracted from departure_time → hour buckets)
TIME_FEATURES = ["departure_hour"]

# Final feature set (in order)
ALL_FEATURES = CAT_FEATURES + ORD_FEATURES + NUM_FEATURES + TIME_FEATURES

# Target variable
TARGET = "fare"


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract and engineer features from the normalized airfare DataFrame.
    Returns a DataFrame with exactly ALL_FEATURES columns + TARGET.
    """
    out = df.copy()

    # ── Time feature: departure hour ──────────────────────────
    if "departure_time" in out.columns:
        def extract_hour(t):
            if pd.isna(t):
                return 12  # default midday
            try:
                return int(str(t).split(":")[0])
            except (ValueError, AttributeError):
                return 12

        out["departure_hour"] = out["departure_time"].apply(extract_hour)
    else:
        out["departure_hour"] = 12

    # ── Fill missing numerical features ───────────────────────
    if "duration_minutes" not in out.columns:
        out["duration_minutes"] = np.nan
    if "days_left" not in out.columns:
        out["days_left"] = np.nan

    # Fill missing durations with route-level median (not fabrication — it's imputation)
    if out["duration_minutes"].isna().any():
        if "origin" in out.columns and "destination" in out.columns:
            route_median_duration = (
                out.groupby(["origin", "destination"])["duration_minutes"]
                .transform("median")
            )
            out["duration_minutes"] = out["duration_minutes"].fillna(route_median_duration)
        # Final fallback: global median
        global_dur_median = out["duration_minutes"].median()
        out["duration_minutes"] = out["duration_minutes"].fillna(
            global_dur_median if not pd.isna(global_dur_median) else 120.0
        )

    # Fill missing days_left with median
    if out["days_left"].isna().any():
        global_dl_median = out["days_left"].median()
        out["days_left"] = out["days_left"].fillna(
            global_dl_median if not pd.isna(global_dl_median) else 30.0
        )

    # ── Ensure categorical columns exist ──────────────────────
    for col in CAT_FEATURES:
        if col not in out.columns:
            out[col] = "Unknown"
        out[col] = out[col].fillna("Unknown").astype(str)

    # ── Stops ─────────────────────────────────────────────────
    if "stops" not in out.columns:
        out["stops"] = 0
    out["stops"] = out["stops"].fillna(0).astype(int)

    return out


def build_preprocessing_pipeline() -> ColumnTransformer:
    """
    Build sklearn ColumnTransformer for the fare prediction model.

    Returns:
        ColumnTransformer that handles categorical, ordinal, and numerical features.
    """
    # Categorical: One-hot encode
    cat_transformer = Pipeline(steps=[
        ("ohe", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])

    # Ordinal: Keep as numeric (stops: 0, 1, 2...)
    ord_transformer = Pipeline(steps=[
        ("passthrough", "passthrough"),
    ])

    # Numerical: Standard scale
    num_transformer = Pipeline(steps=[
        ("scaler", StandardScaler()),
    ])

    # Time features (departure hour → treat as numerical cyclic or categorical)
    time_transformer = Pipeline(steps=[
        ("scaler", StandardScaler()),
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", cat_transformer, CAT_FEATURES),
            ("ord", "passthrough", ORD_FEATURES),
            ("num", num_transformer, NUM_FEATURES),
            ("time", time_transformer, TIME_FEATURES),
        ],
        remainder="drop",  # Drop all unlisted columns (no accidental leakage)
    )

    return preprocessor


def prepare_train_data(
    df: pd.DataFrame,
    exclude_demo_anomalies: bool = True,
    cabin_filter: Optional[str] = None,
) -> tuple[pd.DataFrame, pd.Series]:
    """
    Prepare X, y from the normalized DataFrame for model training.

    Parameters
    ----------
    df : normalized airfare DataFrame
    exclude_demo_anomalies : if True, exclude rows flagged as demo anomalies
    cabin_filter : if set, train only on that cabin class

    Returns
    -------
    X : feature DataFrame
    y : fare Series
    """
    data = df.copy()

    # Drop demo anomalies from training (they are artificially skewed)
    if exclude_demo_anomalies and "is_demo_anomaly" in data.columns:
        before = len(data)
        data = data[~data["is_demo_anomaly"].fillna(False)]
        logger.info(f"Excluded {before - len(data)} demo anomaly rows from training data")

    # Filter cabin class if requested
    if cabin_filter and "cabin_class" in data.columns:
        data = data[data["cabin_class"] == cabin_filter]
        logger.info(f"Filtered to cabin class: {cabin_filter} → {len(data):,} rows")

    # Require fare (target)
    data = data[data[TARGET].notna() & (data[TARGET] > 0)].copy()

    # Feature extraction
    data = extract_features(data)

    # Select only the feature columns
    available = [f for f in ALL_FEATURES if f in data.columns]
    missing = [f for f in ALL_FEATURES if f not in data.columns]
    if missing:
        logger.warning(f"Features not found in data (will be skipped): {missing}")

    X = data[available]
    y = data[TARGET]

    logger.info(f"Training data prepared: {X.shape[0]:,} rows × {X.shape[1]} features")
    logger.info(f"Target (fare) range: ₹{y.min():,.0f} – ₹{y.max():,.0f}")
    logger.info(f"Features used: {available}")

    return X, y
