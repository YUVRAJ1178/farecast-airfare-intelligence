"""
Airfare Intelligence Platform — ML Model Training
Phase 3: ML Training

Compares multiple regression models and saves the best one.
Reports ONLY actually-calculated metrics — no fabricated accuracy.

Models compared:
  1. Linear Regression (baseline)
  2. Random Forest Regressor
  3. Gradient Boosting Regressor (sklearn)
  4. CatBoost Regressor (optional, if installed)

Usage:
  python ml/train.py
  python ml/train.py --input data/processed/airfare_clean.csv
  python ml/train.py --no-catboost    # Skip CatBoost
"""

import argparse
import json
import logging
import sys
import warnings
from pathlib import Path
from time import time

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import Pipeline

warnings.filterwarnings("ignore", category=UserWarning)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("train")

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ml.preprocessing import build_preprocessing_pipeline, prepare_train_data
from ml.evaluate import evaluate_model, print_evaluation_report

MODEL_OUTPUT_PATH = PROJECT_ROOT / "models" / "airfare_model.joblib"
METRICS_OUTPUT_PATH = PROJECT_ROOT / "models" / "training_metrics.json"


def build_model_candidates(use_catboost: bool = True) -> list[tuple[str, object]]:
    """Return list of (name, estimator) pairs to compare."""
    candidates = [
        ("Linear Regression (Ridge baseline)", Ridge(alpha=1.0)),
        (
            "Random Forest",
            RandomForestRegressor(
                n_estimators=200,
                max_depth=20,
                min_samples_split=5,
                n_jobs=-1,
                random_state=42,
            ),
        ),
        (
            "Gradient Boosting",
            GradientBoostingRegressor(
                n_estimators=200,
                max_depth=5,
                learning_rate=0.1,
                subsample=0.8,
                random_state=42,
            ),
        ),
    ]

    if use_catboost:
        try:
            from catboost import CatBoostRegressor
            candidates.append((
                "CatBoost",
                CatBoostRegressor(
                    iterations=300,
                    depth=6,
                    learning_rate=0.05,
                    loss_function="RMSE",
                    random_seed=42,
                    verbose=False,
                ),
            ))
            logger.info("CatBoost available — included in comparison")
        except ImportError:
            logger.warning("CatBoost not installed — skipping. Install with: pip install catboost")

    return candidates


def main():
    parser = argparse.ArgumentParser(description="Airfare Intelligence — ML Training")
    parser.add_argument(
        "--input",
        type=Path,
        default=PROJECT_ROOT / "data" / "processed" / "airfare_clean.csv",
        help="Path to processed airfare CSV",
    )
    parser.add_argument("--no-catboost", action="store_true", help="Skip CatBoost")
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.15,
        help="Test set fraction (default: 0.15)",
    )
    parser.add_argument(
        "--val-size",
        type=float,
        default=0.15,
        help="Validation set fraction of training data (default: 0.15)",
    )
    args = parser.parse_args()

    if not args.input.exists():
        logger.error(
            f"Input file not found: {args.input}\n"
            "Run data ingestion first: python data/ingest.py"
        )
        sys.exit(1)

    # ── Load Data ─────────────────────────────────────────────
    logger.info(f"Loading data from {args.input}")
    df = pd.read_csv(args.input)
    logger.info(f"Loaded {len(df):,} rows")

    # ── Prepare Features ──────────────────────────────────────
    X, y = prepare_train_data(df, exclude_demo_anomalies=True)

    if len(X) < 100:
        logger.error(f"Too few samples ({len(X)}) for reliable ML training.")
        sys.exit(1)

    # ── Train/Val/Test Split ───────────────────────────────────
    # We use a fixed random state for reproducibility
    X_train_full, X_test, y_train_full, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=42
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_full, y_train_full, test_size=args.val_size, random_state=42
    )

    logger.info(f"Split sizes — Train: {len(X_train):,} | Val: {len(X_val):,} | Test: {len(X_test):,}")

    # ── Build Preprocessing ───────────────────────────────────
    preprocessor = build_preprocessing_pipeline()

    # ── Train and Compare Models ──────────────────────────────
    candidates = build_model_candidates(use_catboost=not args.no_catboost)
    all_metrics = []
    best_model = None
    best_name = None
    best_val_rmse = float("inf")

    for name, estimator in candidates:
        logger.info(f"\n── Training: {name} ──")
        t0 = time()

        pipeline = Pipeline([
            ("preprocessor", build_preprocessing_pipeline()),
            ("model", estimator),
        ])

        try:
            pipeline.fit(X_train, y_train)
            train_time = time() - t0

            val_metrics = evaluate_model(pipeline, X_val, y_val, split_name="Validation")
            test_metrics = evaluate_model(pipeline, X_test, y_test, split_name="Test")

            print_evaluation_report(name, val_metrics, test_metrics)

            all_metrics.append({
                "model": name,
                "train_time_seconds": round(train_time, 2),
                "validation": val_metrics,
                "test": test_metrics,
            })

            # Select best by validation RMSE
            if val_metrics["rmse"] < best_val_rmse:
                best_val_rmse = val_metrics["rmse"]
                best_model = pipeline
                best_name = name

        except Exception as e:
            logger.error(f"Training failed for {name}: {e}")
            continue

    if best_model is None:
        logger.error("No model trained successfully.")
        sys.exit(1)

    # ── Save Best Model ───────────────────────────────────────
    logger.info(f"\n{'='*60}")
    logger.info(f"BEST MODEL: {best_name}")
    logger.info(f"Validation RMSE: ₹{best_val_rmse:,.0f}")
    logger.info(f"{'='*60}")

    MODEL_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_model, MODEL_OUTPUT_PATH)
    logger.info(f"Model saved to {MODEL_OUTPUT_PATH}")

    # ── Save Metrics ──────────────────────────────────────────
    training_record = {
        "best_model": best_name,
        "best_val_rmse": round(best_val_rmse, 2),
        "training_data_size": len(X_train),
        "validation_data_size": len(X_val),
        "test_data_size": len(X_test),
        "features_used": list(X.columns),
        "all_models": all_metrics,
        "note": (
            "All metrics computed on held-out data. "
            "These are actual measured values, not fabricated."
        ),
    }

    with open(METRICS_OUTPUT_PATH, "w") as f:
        json.dump(training_record, f, indent=2)
    logger.info(f"Training metrics saved to {METRICS_OUTPUT_PATH}")

    logger.info("\nNext step: python ml/evaluate.py")


if __name__ == "__main__":
    main()
