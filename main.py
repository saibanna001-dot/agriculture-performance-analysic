"""
main.py
=======
Full agriculture performance analysis pipeline.

Usage:
    python main.py
    python main.py --data path/to/dataset.csv --out outputs/figures
"""

from __future__ import annotations

import argparse
import os
import sys
import time

# ---------------------------------------------------------------------------
# Allow running from the project root without installing the package
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(__file__))

from src.data_loader import (
    load_data,
    describe_structure,
    data_quality_report,
)
from src.eda import print_eda_tables
from src.statistics import (
    detect_outliers_iqr,
    print_outlier_report,
    print_correlation_report,
    print_insights,
)
from src.visualizations import (
    plot_seasonal_yield,
    plot_crop_performance,
    plot_crop_yield_season_heatmap,
    plot_env_vs_yield,
    plot_irrigation_analysis,
    plot_irrigation_yield_boxplot,
    plot_water_analysis,
    plot_financial_analysis,
    plot_profit_by_irrigation,
    plot_outlier_summary,
    plot_correlation_heatmap,
    plot_key_scatter_matrix,
    plot_nutrient_vs_yield,
    plot_disease_risk_analysis,
)

# ---------------------------------------------------------------------------
# Default paths (relative to this file)
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(__file__)
DEFAULT_DATA = os.path.join(_HERE, "data", "seasonal_agriculture_performance_dataset.csv")
DEFAULT_OUT = os.path.join(_HERE, "outputs", "figures")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Agriculture Performance Data Analysis Pipeline"
    )
    parser.add_argument("--data", default=DEFAULT_DATA,
                        help="Path to the CSV dataset")
    parser.add_argument("--out", default=DEFAULT_OUT,
                        help="Output directory for figures")
    return parser.parse_args()


def section(title: str) -> None:
    print(f"\n{'-' * 65}")
    print(f"  >> {title}")
    print(f"{'-' * 65}")


def run_pipeline(csv_path: str, output_dir: str) -> None:
    os.makedirs(output_dir, exist_ok=True)
    total_start = time.time()

    # -----------------------------------------------------------------------
    # 1. Load & validate data
    # -----------------------------------------------------------------------
    section("Loading dataset")
    df = load_data(csv_path)
    print(f"  Loaded {len(df):,} rows × {df.shape[1]} columns from:\n  {csv_path}")

    # -----------------------------------------------------------------------
    # 2. Structure overview
    # -----------------------------------------------------------------------
    section("Dataset structure")
    describe_structure(df)

    # -----------------------------------------------------------------------
    # 3. Data quality
    # -----------------------------------------------------------------------
    section("Data quality report")
    data_quality_report(df)

    # -----------------------------------------------------------------------
    # 4. EDA summary tables
    # -----------------------------------------------------------------------
    section("Exploratory data analysis — summary tables")
    print_eda_tables(df)

    # -----------------------------------------------------------------------
    # 5. Outlier detection
    # -----------------------------------------------------------------------
    section("Outlier detection (IQR method)")
    outlier_info = detect_outliers_iqr(df)
    print_outlier_report(outlier_info)

    # -----------------------------------------------------------------------
    # 6. Correlation analysis
    # -----------------------------------------------------------------------
    section("Correlation analysis")
    print_correlation_report(df)

    # -----------------------------------------------------------------------
    # 7. Practical insights
    # -----------------------------------------------------------------------
    section("Practical resource-management insights")
    print_insights(df)

    # -----------------------------------------------------------------------
    # 8. Visualizations
    # -----------------------------------------------------------------------
    section("Generating visualizations")

    plots = [
        ("Seasonal performance",         lambda: plot_seasonal_yield(df, output_dir)),
        ("Crop performance comparison",  lambda: plot_crop_performance(df, output_dir)),
        ("Crop × Season yield heatmap",  lambda: plot_crop_yield_season_heatmap(df, output_dir)),
        ("Environment vs yield",         lambda: plot_env_vs_yield(df, output_dir)),
        ("Irrigation method analysis",   lambda: plot_irrigation_analysis(df, output_dir)),
        ("Irrigation yield boxplot",     lambda: plot_irrigation_yield_boxplot(df, output_dir)),
        ("Water usage & efficiency",     lambda: plot_water_analysis(df, output_dir)),
        ("Financial analysis",           lambda: plot_financial_analysis(df, output_dir)),
        ("Profit by irrigation",         lambda: plot_profit_by_irrigation(df, output_dir)),
        ("Outlier summary",              lambda: plot_outlier_summary(df, outlier_info, output_dir)),
        ("Correlation heatmap",          lambda: plot_correlation_heatmap(df, output_dir)),
        ("Key scatter matrix",           lambda: plot_key_scatter_matrix(df, output_dir)),
        ("Nutrient inputs vs yield",     lambda: plot_nutrient_vs_yield(df, output_dir)),
        ("Disease & pest risk",          lambda: plot_disease_risk_analysis(df, output_dir)),
    ]

    saved: list[str] = []
    for label, fn in plots:
        t0 = time.time()
        try:
            path = fn()
            saved.append(path)
            elapsed = time.time() - t0
            print(f"  [OK] {label:<35}  ->  {os.path.basename(path)}  ({elapsed:.1f}s)")
        except Exception as exc:
            print(f"  [FAIL] {label:<35}  ERROR: {exc}")

    # -----------------------------------------------------------------------
    # 9. Summary
    # -----------------------------------------------------------------------
    total_elapsed = time.time() - total_start
    print(f"\n{'=' * 65}")
    print(f"  PIPELINE COMPLETE")
    print(f"  Figures saved : {len(saved)} / {len(plots)}")
    print(f"  Output folder : {output_dir}")
    print(f"  Total runtime : {total_elapsed:.1f}s")
    print(f"{'=' * 65}\n")


if __name__ == "__main__":
    args = parse_args()
    run_pipeline(csv_path=args.data, output_dir=args.out)
