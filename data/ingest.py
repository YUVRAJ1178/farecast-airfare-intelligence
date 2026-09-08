"""
Airfare Intelligence Platform — Master Data Ingestion Script
Phase 2: Historical Data Ingestion

Usage:
  python data/ingest.py                    # Use real data if available, demo otherwise
  python data/ingest.py --demo             # Force demo mode
  python data/ingest.py --kaggle path.csv  # Specify Kaggle CSV path
  python data/ingest.py --skip-eda        # Skip EDA (faster, for CI)

This script:
  1. Loads raw data (real CSVs or generates demo data)
  2. Cleans and normalizes via cleaning pipeline
  3. Runs EDA and saves plots/report
  4. Saves processed data to data/processed/airfare_clean.csv
"""

import argparse
import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("ingest")

# Paths (relative to project root)
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
EDA_DIR = PROCESSED_DIR / "eda"

KAGGLE_DEFAULT_PATH = RAW_DIR / "kaggle_flight_price.csv"
GITHUB_DEFAULT_PATH = RAW_DIR / "full_fare.csv"
OUTPUT_PATH = PROCESSED_DIR / "airfare_clean.csv"


def main():
    parser = argparse.ArgumentParser(
        description="Airfare Intelligence — Data Ingestion Pipeline"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Force demo mode (generate synthetic data even if real data exists)",
    )
    parser.add_argument(
        "--kaggle",
        type=Path,
        default=KAGGLE_DEFAULT_PATH,
        help="Path to Kaggle Flight Price CSV",
    )
    parser.add_argument(
        "--github",
        type=Path,
        default=GITHUB_DEFAULT_PATH,
        help="Path to GitHub full_fare.csv",
    )
    parser.add_argument(
        "--skip-eda",
        action="store_true",
        help="Skip EDA step (faster for CI/testing)",
    )
    parser.add_argument(
        "--demo-records",
        type=int,
        default=50000,
        help="Number of synthetic records to generate in demo mode (default: 50000)",
    )
    args = parser.parse_args()

    # Add project root to path for imports
    sys.path.insert(0, str(PROJECT_ROOT))

    from data.cleaning import run_cleaning_pipeline
    from data.demo_generator import generate_demo_dataset, generate_demo_anomalies
    from data.schema import DataSource

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    # ── Step 1: Load / Generate Data ─────────────────────────
    kaggle_path = args.kaggle
    if not kaggle_path.exists():
        for candidate in [RAW_DIR / "goibibo_flights_data.xls", RAW_DIR / "economy.xls", RAW_DIR / "Clean_Dataset.csv"]:
            if candidate.exists():
                kaggle_path = candidate
                break

    github_path = args.github
    has_kaggle = kaggle_path.exists() and not args.demo
    has_github = github_path.exists() and not args.demo

    if args.demo or (not has_kaggle and not has_github):
        if args.demo:
            logger.info("Demo mode explicitly requested.")
        else:
            logger.warning(
                "No real data found. Falling back to DEMO MODE.\n"
                f"  Expected Kaggle CSV at: {args.kaggle}\n"
                f"  Expected GitHub CSV at: {args.github}\n"
                "  All generated data will be tagged source='{DataSource.DEMO}' "
                "and clearly labelled in the UI."
            )
        import pandas as pd
        df = generate_demo_dataset(
            n_records=args.demo_records,
            output_path=PROCESSED_DIR / "demo_raw.csv",
        )
        df = generate_demo_anomalies(df, n_anomalies=20)
        df.to_csv(OUTPUT_PATH, index=False)
        logger.info(f"Demo data saved to {OUTPUT_PATH}")
    else:
        logger.info(f"Real data found: Kaggle/Flight data = {kaggle_path if has_kaggle else 'None'}, GitHub data = {github_path if has_github else 'None'}")
        df = run_cleaning_pipeline(
            kaggle_path=kaggle_path if has_kaggle else None,
            github_path=github_path if has_github else None,
            output_path=OUTPUT_PATH,
        )

        if df.empty:
            logger.error("Cleaning pipeline returned empty DataFrame. Check input files.")
            sys.exit(1)

    logger.info(f"Dataset ready: {len(df):,} rows")
    logger.info(f"Data sources present: {df['source'].value_counts().to_dict()}")

    # ── Step 2: EDA ───────────────────────────────────────────
    if not args.skip_eda:
        logger.info("Running EDA...")
        try:
            from data.eda import run_eda
            eda_results = run_eda(df, output_dir=EDA_DIR)
            logger.info(f"EDA complete. Results in {EDA_DIR}")
        except Exception as e:
            logger.error(f"EDA failed (non-fatal): {e}")
    else:
        logger.info("Skipping EDA (--skip-eda flag set)")

    # ── Step 3: Summary ───────────────────────────────────────
    logger.info("\n" + "=" * 60)
    logger.info("DATA INGESTION COMPLETE")
    logger.info("=" * 60)
    logger.info(f"  Output file:   {OUTPUT_PATH}")
    logger.info(f"  Total records: {len(df):,}")
    if "source" in df.columns:
        for src, count in df["source"].value_counts().items():
            label = "(DEMO — not real)" if src == DataSource.DEMO else "(historical)"
            logger.info(f"  Source '{src}': {count:,} records {label}")
    if "airline" in df.columns:
        logger.info(f"  Airlines: {sorted(df['airline'].unique())}")
    if "origin" in df.columns and "destination" in df.columns:
        routes = df.groupby(["origin", "destination"]).size().shape[0]
        logger.info(f"  Unique routes: {routes}")
    if "fare" in df.columns:
        logger.info(f"  Fare range: ₹{df['fare'].min():,.0f} – ₹{df['fare'].max():,.0f}")
        logger.info(f"  Avg fare:   ₹{df['fare'].mean():,.0f}")
    logger.info("=" * 60)
    logger.info("\nNext step: python ml/train.py")


if __name__ == "__main__":
    main()
