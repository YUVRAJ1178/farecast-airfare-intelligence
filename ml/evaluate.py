"""
Airfare Intelligence Platform — Model Evaluation
Phase 3: ML Training

Computes and reports MAE, RMSE, R² on any split.
All metrics are computed from actual predictions — never fabricated.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def evaluate_model(
    pipeline,
    X: pd.DataFrame,
    y: pd.Series,
    split_name: str = "Evaluation",
) -> dict:
    """
    Evaluate a trained sklearn Pipeline on X, y.

    Returns
    -------
    dict with keys: mae, rmse, r2, mape, n_samples, split_name
    All values computed from actual predictions — none fabricated.
    """
    y_pred = pipeline.predict(X)
    y_arr = np.array(y)

    mae = float(mean_absolute_error(y_arr, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_arr, y_pred)))
    r2 = float(r2_score(y_arr, y_pred))

    # Mean Absolute Percentage Error (guard against zero fares)
    nonzero_mask = y_arr > 0
    if nonzero_mask.sum() > 0:
        mape = float(
            np.mean(np.abs((y_arr[nonzero_mask] - y_pred[nonzero_mask]) / y_arr[nonzero_mask])) * 100
        )
    else:
        mape = None

    return {
        "split": split_name,
        "n_samples": len(y_arr),
        "mae": round(mae, 2),
        "rmse": round(rmse, 2),
        "r2": round(r2, 4),
        "mape": round(mape, 2) if mape is not None else None,
    }


def print_evaluation_report(
    model_name: str,
    val_metrics: dict,
    test_metrics: dict,
):
    """Print a formatted evaluation report."""
    print(f"\n{'─'*50}")
    print(f"  Model: {model_name}")
    print(f"{'─'*50}")
    print(f"  {'Metric':<12}  {'Validation':>14}  {'Test':>14}")
    print(f"  {'─'*12}  {'─'*14}  {'─'*14}")
    print(f"  {'MAE (₹)':<12}  {val_metrics['mae']:>14,.0f}  {test_metrics['mae']:>14,.0f}")
    print(f"  {'RMSE (₹)':<12}  {val_metrics['rmse']:>14,.0f}  {test_metrics['rmse']:>14,.0f}")
    print(f"  {'R²':<12}  {val_metrics['r2']:>14.4f}  {test_metrics['r2']:>14.4f}")
    if val_metrics.get("mape") is not None:
        print(f"  {'MAPE (%)':<12}  {val_metrics['mape']:>14.1f}  {test_metrics.get('mape', 'N/A'):>14}")
    print(f"  {'Samples':<12}  {val_metrics['n_samples']:>14,}  {test_metrics['n_samples']:>14,}")
    print(f"{'─'*50}")


def main():
    """
    Standalone evaluation script.
    Loads the saved best model and re-evaluates on a test set.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )

    model_path = PROJECT_ROOT / "models" / "airfare_model.joblib"
    metrics_path = PROJECT_ROOT / "models" / "training_metrics.json"
    data_path = PROJECT_ROOT / "data" / "processed" / "airfare_clean.csv"

    if not model_path.exists():
        logger.error(f"No saved model found at {model_path}")
        logger.error("Run training first: python ml/train.py")
        sys.exit(1)

    logger.info(f"Loading model from {model_path}")
    pipeline = joblib.load(model_path)

    logger.info(f"Loading data from {data_path}")
    df = pd.read_csv(data_path)

    from ml.preprocessing import prepare_train_data
    from sklearn.model_selection import train_test_split

    X, y = prepare_train_data(df)
    _, X_test, _, y_test = train_test_split(X, y, test_size=0.15, random_state=42)

    logger.info(f"Evaluating on {len(X_test):,} test samples...")
    metrics = evaluate_model(pipeline, X_test, y_test, split_name="Test (held-out)")

    print("\n" + "="*50)
    print("  SAVED MODEL EVALUATION RESULTS")
    print("="*50)
    print(f"  MAE:  ₹{metrics['mae']:,.0f}")
    print(f"  RMSE: ₹{metrics['rmse']:,.0f}")
    print(f"  R²:   {metrics['r2']:.4f}")
    if metrics.get("mape"):
        print(f"  MAPE: {metrics['mape']:.1f}%")
    print(f"  Note: All metrics computed on held-out test data")
    print("="*50)

    if metrics_path.exists():
        with open(metrics_path) as f:
            training_record = json.load(f)
        print(f"\n  Best model was: {training_record.get('best_model', 'Unknown')}")


if __name__ == "__main__":
    main()
