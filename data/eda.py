"""
Airfare Intelligence Platform — EDA (Exploratory Data Analysis)
Phase 2: Historical Data Ingestion

Generates a structured EDA report covering:
  - Dataset dimensions
  - Missing values
  - Duplicates
  - Airlines, origins, destinations
  - Fare distribution
  - Average fare by airline
  - Average fare by route
  - Days left vs fare relationship
  - Stops vs fare relationship
  - Class vs fare relationship

Results are saved to data/processed/eda/
"""

import logging
import warnings
from pathlib import Path
from typing import Optional

import matplotlib
matplotlib.use("Agg")   # Non-interactive backend for server-side rendering
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd
import seaborn as sns

warnings.filterwarnings("ignore", category=FutureWarning)
logger = logging.getLogger(__name__)

# ── Plot style ────────────────────────────────────────────────
STYLE = {
    "figure.facecolor": "#0f1117",
    "axes.facecolor": "#1a1f2e",
    "axes.edgecolor": "#2d3550",
    "axes.labelcolor": "#e0e6f0",
    "axes.titlecolor": "#ffffff",
    "xtick.color": "#a0a8c0",
    "ytick.color": "#a0a8c0",
    "grid.color": "#2d3550",
    "text.color": "#e0e6f0",
    "font.family": "DejaVu Sans",
    "figure.dpi": 120,
}
ACCENT = "#4f8ef7"
ACCENT2 = "#f7a34f"
PALETTE = ["#4f8ef7", "#f7a34f", "#4fe8a0", "#f74f7a", "#a04ff7", "#4ff7f4", "#f7f74f"]


def _apply_style():
    plt.rcParams.update(STYLE)
    sns.set_palette(PALETTE)


def _save(fig, path: Path, title: str):
    fig.tight_layout(pad=2.0)
    fig.savefig(path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    logger.info(f"Saved plot: {path.name}")


def run_eda(df: pd.DataFrame, output_dir: Path) -> dict:
    """
    Run the full EDA pipeline.

    Parameters
    ----------
    df : pd.DataFrame
        Normalized airfare DataFrame (output of cleaning pipeline or demo generator)
    output_dir : Path
        Directory to save plots and the text report

    Returns
    -------
    dict
        Summary statistics dictionary (also usable by API endpoints)
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    _apply_style()

    results = {}

    # ── 1. Dataset Dimensions ─────────────────────────────────
    logger.info("── EDA 1: Dataset Dimensions")
    results["dimensions"] = {
        "rows": len(df),
        "columns": list(df.columns),
        "n_columns": len(df.columns),
    }
    logger.info(f"  Rows: {len(df):,}  |  Columns: {len(df.columns)}")

    # ── 2. Missing Values ─────────────────────────────────────
    logger.info("── EDA 2: Missing Values")
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    missing_df = pd.DataFrame({
        "missing_count": missing,
        "missing_pct": missing_pct
    }).query("missing_count > 0").sort_values("missing_pct", ascending=False)
    results["missing_values"] = missing_df.to_dict()
    logger.info(f"  Columns with missing values:\n{missing_df.to_string()}")

    # ── 3. Duplicates ─────────────────────────────────────────
    logger.info("── EDA 3: Duplicates")
    dup_count = df.duplicated().sum()
    results["duplicates"] = int(dup_count)
    logger.info(f"  Duplicate rows: {dup_count:,}")

    # ── 4. Airlines ───────────────────────────────────────────
    logger.info("── EDA 4: Airlines")
    if "airline" in df.columns:
        airline_counts = df["airline"].value_counts()
        results["airlines"] = airline_counts.to_dict()
        logger.info(f"  Airlines: {airline_counts.to_dict()}")

        fig, ax = plt.subplots(figsize=(10, 5))
        fig.patch.set_facecolor(STYLE["figure.facecolor"])
        ax.set_facecolor(STYLE["axes.facecolor"])
        bars = ax.barh(
            airline_counts.index,
            airline_counts.values,
            color=PALETTE[:len(airline_counts)],
        )
        ax.set_xlabel("Number of Observations", color=STYLE["axes.labelcolor"])
        ax.set_title("Airfare Observations by Airline", color="#ffffff", fontsize=14, pad=12)
        ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"{x:,.0f}"))
        for bar, val in zip(bars, airline_counts.values):
            ax.text(bar.get_width() + max(airline_counts) * 0.01,
                    bar.get_y() + bar.get_height() / 2,
                    f"{val:,}", va="center", color="#a0a8c0", fontsize=9)
        ax.grid(axis="x", alpha=0.3)
        ax.invert_yaxis()
        _save(fig, output_dir / "01_airline_distribution.png", "Airlines")

    # ── 5. Origins & Destinations ─────────────────────────────
    logger.info("── EDA 5: Origins & Destinations")
    if "origin" in df.columns and "destination" in df.columns:
        results["origins"] = df["origin"].value_counts().head(15).to_dict()
        results["destinations"] = df["destination"].value_counts().head(15).to_dict()

        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        fig.patch.set_facecolor(STYLE["figure.facecolor"])
        for ax in axes:
            ax.set_facecolor(STYLE["axes.facecolor"])

        origin_vc = df["origin"].value_counts().head(10)
        axes[0].barh(origin_vc.index, origin_vc.values, color=ACCENT)
        axes[0].set_title("Top Origins", color="#ffffff", fontsize=12)
        axes[0].set_xlabel("Observations", color=STYLE["axes.labelcolor"])
        axes[0].invert_yaxis()
        axes[0].grid(axis="x", alpha=0.3)

        dest_vc = df["destination"].value_counts().head(10)
        axes[1].barh(dest_vc.index, dest_vc.values, color=ACCENT2)
        axes[1].set_title("Top Destinations", color="#ffffff", fontsize=12)
        axes[1].set_xlabel("Observations", color=STYLE["axes.labelcolor"])
        axes[1].invert_yaxis()
        axes[1].grid(axis="x", alpha=0.3)

        _save(fig, output_dir / "02_origin_destination.png", "Origins & Destinations")

    # ── 6. Fare Distribution ──────────────────────────────────
    logger.info("── EDA 6: Fare Distribution")
    if "fare" in df.columns:
        fare_series = df["fare"].dropna()
        results["fare_stats"] = {
            "min": float(fare_series.min()),
            "max": float(fare_series.max()),
            "mean": float(fare_series.mean()),
            "median": float(fare_series.median()),
            "std": float(fare_series.std()),
            "p25": float(fare_series.quantile(0.25)),
            "p75": float(fare_series.quantile(0.75)),
            "p95": float(fare_series.quantile(0.95)),
        }
        logger.info(f"  Fare stats: {results['fare_stats']}")

        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        fig.patch.set_facecolor(STYLE["figure.facecolor"])
        for ax in axes:
            ax.set_facecolor(STYLE["axes.facecolor"])

        # Histogram
        axes[0].hist(fare_series, bins=60, color=ACCENT, edgecolor="#0f1117", alpha=0.85)
        axes[0].set_xlabel("Fare (₹)", color=STYLE["axes.labelcolor"])
        axes[0].set_ylabel("Count", color=STYLE["axes.labelcolor"])
        axes[0].set_title("Fare Distribution", color="#ffffff", fontsize=12)
        axes[0].axvline(fare_series.median(), color=ACCENT2, linestyle="--",
                        label=f"Median: ₹{fare_series.median():,.0f}")
        axes[0].legend(framealpha=0.3, labelcolor="#e0e6f0")
        axes[0].grid(alpha=0.3)
        axes[0].xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"₹{x/1000:.0f}k"))

        # Box plot (log scale for visibility)
        axes[1].boxplot(
            fare_series,
            patch_artist=True,
            boxprops=dict(facecolor="#1f2a4a", color=ACCENT),
            medianprops=dict(color=ACCENT2, linewidth=2),
            whiskerprops=dict(color=ACCENT),
            capprops=dict(color=ACCENT),
            flierprops=dict(markerfacecolor=ACCENT, marker=".", alpha=0.3),
        )
        axes[1].set_title("Fare Box Plot", color="#ffffff", fontsize=12)
        axes[1].set_ylabel("Fare (₹)", color=STYLE["axes.labelcolor"])
        axes[1].grid(alpha=0.3)
        axes[1].yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))

        _save(fig, output_dir / "03_fare_distribution.png", "Fare Distribution")

    # ── 7. Average Fare by Airline ────────────────────────────
    logger.info("── EDA 7: Average Fare by Airline")
    if "airline" in df.columns and "fare" in df.columns:
        avg_fare_airline = (
            df.groupby("airline")["fare"]
            .agg(["mean", "median", "count"])
            .round(0)
            .sort_values("mean", ascending=False)
        )
        results["avg_fare_by_airline"] = avg_fare_airline["mean"].to_dict()
        logger.info(f"  Avg fare by airline:\n{avg_fare_airline.to_string()}")

        fig, ax = plt.subplots(figsize=(10, 5))
        fig.patch.set_facecolor(STYLE["figure.facecolor"])
        ax.set_facecolor(STYLE["axes.facecolor"])
        colors = PALETTE[:len(avg_fare_airline)]
        bars = ax.barh(
            avg_fare_airline.index,
            avg_fare_airline["mean"],
            color=colors,
            alpha=0.9,
        )
        for bar, val in zip(bars, avg_fare_airline["mean"]):
            ax.text(bar.get_width() + 100, bar.get_y() + bar.get_height() / 2,
                    f"₹{val:,.0f}", va="center", color="#a0a8c0", fontsize=9)
        ax.set_xlabel("Average Fare (₹)", color=STYLE["axes.labelcolor"])
        ax.set_title("Average Fare by Airline", color="#ffffff", fontsize=14, pad=12)
        ax.invert_yaxis()
        ax.grid(axis="x", alpha=0.3)
        ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))
        _save(fig, output_dir / "04_avg_fare_by_airline.png", "Avg Fare by Airline")

    # ── 8. Average Fare by Route ──────────────────────────────
    logger.info("── EDA 8: Average Fare by Route")
    if "origin" in df.columns and "destination" in df.columns and "fare" in df.columns:
        df["route"] = df["origin"] + " → " + df["destination"]
        avg_fare_route = (
            df.groupby("route")["fare"]
            .agg(["mean", "median", "count"])
            .round(0)
            .sort_values("mean", ascending=False)
            .head(20)
        )
        results["avg_fare_by_route"] = avg_fare_route["mean"].to_dict()

        fig, ax = plt.subplots(figsize=(12, 8))
        fig.patch.set_facecolor(STYLE["figure.facecolor"])
        ax.set_facecolor(STYLE["axes.facecolor"])
        ax.barh(avg_fare_route.index, avg_fare_route["mean"], color=ACCENT, alpha=0.85)
        ax.set_xlabel("Average Fare (₹)", color=STYLE["axes.labelcolor"])
        ax.set_title("Average Fare by Route (Top 20)", color="#ffffff", fontsize=14, pad=12)
        ax.invert_yaxis()
        ax.grid(axis="x", alpha=0.3)
        ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))
        _save(fig, output_dir / "05_avg_fare_by_route.png", "Avg Fare by Route")

    # ── 9. Days Left vs Fare ──────────────────────────────────
    logger.info("── EDA 9: Days Left vs Fare")
    if "days_left" in df.columns and "fare" in df.columns:
        dl_fare = df[["days_left", "fare"]].dropna()
        dl_fare = dl_fare[dl_fare["days_left"].between(0, 90)]

        if len(dl_fare) > 100:
            # Bin days_left for cleaner visualization
            dl_fare["days_bucket"] = pd.cut(
                dl_fare["days_left"],
                bins=[0, 3, 7, 14, 21, 30, 45, 60, 90],
                labels=["1-3", "4-7", "8-14", "15-21", "22-30", "31-45", "46-60", "61-90"],
            )
            bucket_avg = dl_fare.groupby("days_bucket", observed=True)["fare"].median()
            results["days_left_vs_fare"] = {
                str(k): float(v) for k, v in bucket_avg.items()
            }

            fig, ax = plt.subplots(figsize=(12, 5))
            fig.patch.set_facecolor(STYLE["figure.facecolor"])
            ax.set_facecolor(STYLE["axes.facecolor"])
            ax.plot(
                range(len(bucket_avg)),
                bucket_avg.values,
                color=ACCENT, linewidth=2.5, marker="o", markersize=7,
            )
            ax.fill_between(range(len(bucket_avg)), bucket_avg.values,
                            alpha=0.15, color=ACCENT)
            ax.set_xticks(range(len(bucket_avg)))
            ax.set_xticklabels(bucket_avg.index, color=STYLE["axes.labelcolor"])
            ax.set_xlabel("Days Before Departure", color=STYLE["axes.labelcolor"])
            ax.set_ylabel("Median Fare (₹)", color=STYLE["axes.labelcolor"])
            ax.set_title("Fare vs Booking Window (Days Left)", color="#ffffff", fontsize=14, pad=12)
            ax.grid(alpha=0.3)
            ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))
            _save(fig, output_dir / "06_days_left_vs_fare.png", "Days Left vs Fare")

    # ── 10. Stops vs Fare ─────────────────────────────────────
    logger.info("── EDA 10: Stops vs Fare")
    if "stops" in df.columns and "fare" in df.columns:
        stops_fare = df.groupby("stops")["fare"].agg(["mean", "median"]).round(0)
        results["stops_vs_fare"] = stops_fare["median"].to_dict()
        logger.info(f"  Stops vs fare:\n{stops_fare.to_string()}")

        fig, ax = plt.subplots(figsize=(8, 5))
        fig.patch.set_facecolor(STYLE["figure.facecolor"])
        ax.set_facecolor(STYLE["axes.facecolor"])
        stop_labels = {0: "Non-stop", 1: "1 Stop", 2: "2 Stops", 3: "3+ Stops"}
        x = [stop_labels.get(s, str(s)) for s in stops_fare.index]
        ax.bar(x, stops_fare["median"], color=PALETTE[:len(stops_fare)], alpha=0.9)
        ax.set_xlabel("Number of Stops", color=STYLE["axes.labelcolor"])
        ax.set_ylabel("Median Fare (₹)", color=STYLE["axes.labelcolor"])
        ax.set_title("Median Fare by Number of Stops", color="#ffffff", fontsize=14, pad=12)
        ax.grid(axis="y", alpha=0.3)
        ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))
        _save(fig, output_dir / "07_stops_vs_fare.png", "Stops vs Fare")

    # ── 11. Cabin Class vs Fare ───────────────────────────────
    logger.info("── EDA 11: Cabin Class vs Fare")
    if "cabin_class" in df.columns and "fare" in df.columns:
        class_fare = df.groupby("cabin_class")["fare"].agg(["mean", "median"]).round(0)
        results["class_vs_fare"] = class_fare["median"].to_dict()
        logger.info(f"  Class vs fare:\n{class_fare.to_string()}")

        fig, ax = plt.subplots(figsize=(8, 5))
        fig.patch.set_facecolor(STYLE["figure.facecolor"])
        ax.set_facecolor(STYLE["axes.facecolor"])
        ax.bar(class_fare.index, class_fare["median"],
               color=PALETTE[:len(class_fare)], alpha=0.9)
        ax.set_xlabel("Cabin Class", color=STYLE["axes.labelcolor"])
        ax.set_ylabel("Median Fare (₹)", color=STYLE["axes.labelcolor"])
        ax.set_title("Median Fare by Cabin Class", color="#ffffff", fontsize=14, pad=12)
        ax.grid(axis="y", alpha=0.3)
        ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))
        _save(fig, output_dir / "08_class_vs_fare.png", "Class vs Fare")

    # ── Save text report ──────────────────────────────────────
    report_path = output_dir / "eda_report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("AIRFARE INTELLIGENCE PLATFORM — EDA REPORT\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Dataset Dimensions: {results['dimensions']['rows']:,} rows × {results['dimensions']['n_columns']} columns\n")
        f.write(f"Duplicate rows: {results.get('duplicates', 'N/A')}\n\n")

        if "fare_stats" in results:
            fs = results["fare_stats"]
            f.write("FARE STATISTICS (INR)\n")
            f.write(f"  Min:    ₹{fs['min']:,.0f}\n")
            f.write(f"  Max:    ₹{fs['max']:,.0f}\n")
            f.write(f"  Mean:   ₹{fs['mean']:,.0f}\n")
            f.write(f"  Median: ₹{fs['median']:,.0f}\n")
            f.write(f"  StdDev: ₹{fs['std']:,.0f}\n")
            f.write(f"  P25:    ₹{fs['p25']:,.0f}\n")
            f.write(f"  P75:    ₹{fs['p75']:,.0f}\n")
            f.write(f"  P95:    ₹{fs['p95']:,.0f}\n\n")

        if "missing_values" in results:
            mv = results["missing_values"]
            if mv.get("missing_count"):
                f.write("MISSING VALUES\n")
                for col in mv["missing_count"]:
                    cnt = mv["missing_count"][col]
                    pct = mv["missing_pct"][col]
                    f.write(f"  {col}: {cnt:,} ({pct:.1f}%)\n")
                f.write("\n")

        if "avg_fare_by_airline" in results:
            f.write("AVERAGE FARE BY AIRLINE\n")
            for airline, fare in sorted(results["avg_fare_by_airline"].items(),
                                        key=lambda x: -x[1]):
                f.write(f"  {airline}: ₹{fare:,.0f}\n")
            f.write("\n")

    logger.info(f"EDA report saved to {report_path}")
    logger.info("EDA complete.")
    return results


if __name__ == "__main__":
    import argparse
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    project_root = Path(__file__).parent.parent
    default_input = project_root / "data" / "processed" / "airfare_clean.csv"
    default_output = project_root / "data" / "processed" / "eda"

    parser = argparse.ArgumentParser(description="Airfare Intelligence — Exploratory Data Analysis")
    parser.add_argument(
        "--input",
        type=Path,
        default=default_input,
        help=f"Path to cleaned airfare CSV (default: {default_input})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=default_output,
        help=f"Directory to save EDA plots and report (default: {default_output})",
    )
    args = parser.parse_args()

    if not args.input.exists():
        logger.error(f"Input file not found: {args.input}. Run data/ingest.py first.")
        sys.exit(1)

    logger.info(f"Loading dataset from {args.input}...")
    df_data = pd.read_csv(args.input)
    run_eda(df_data, args.output_dir)
