"""
statistics.py
=============
Outlier detection (IQR method) and correlation analysis utilities.
"""

from __future__ import annotations

import pandas as pd
import numpy as np
from src.data_loader import NUMERIC_COLS


# ---------------------------------------------------------------------------
# Outlier detection
# ---------------------------------------------------------------------------
def detect_outliers_iqr(df: pd.DataFrame,
                         cols: list[str] | None = None,
                         iqr_multiplier: float = 1.5) -> dict:
    """
    Detect outliers in numeric columns using the IQR method.

    Returns a dict keyed by column name with:
        - 'count'  : number of outlier rows
        - 'pct'    : percentage of total rows
        - 'lower'  : lower fence
        - 'upper'  : upper fence
        - 'index'  : boolean Series of outlier flags
    """
    if cols is None:
        cols = [c for c in NUMERIC_COLS if c in df.columns]

    result: dict = {}
    for col in cols:
        series = df[col].dropna()
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - iqr_multiplier * iqr
        upper = q3 + iqr_multiplier * iqr
        mask = (df[col] < lower) | (df[col] > upper)
        result[col] = {
            "count": int(mask.sum()),
            "pct": round(mask.sum() / len(df) * 100, 2),
            "lower": round(lower, 4),
            "upper": round(upper, 4),
            "mask": mask,
        }
    return result


def print_outlier_report(outlier_info: dict, threshold_pct: float = 5.0) -> None:
    """Print an outlier summary table."""
    sep = "=" * 65
    print(f"\n{sep}")
    print("  OUTLIER DETECTION REPORT  (IQR × 1.5)")
    print(sep)
    print(f"  {'Column':<35} {'Count':>7} {'Pct':>7}  Fences")
    print("-" * 65)
    flagged = []
    for col, info in sorted(outlier_info.items(),
                             key=lambda x: x[1]["count"], reverse=True):
        marker = "[!]" if info["pct"] > threshold_pct else "   "
        print(f"  {marker} {col:<33} {info['count']:>7,} "
              f"{info['pct']:>6.1f}%  "
              f"[{info['lower']:.2f}, {info['upper']:.2f}]")
        if info["pct"] > threshold_pct:
            flagged.append(col)

    if flagged:
        print(f"\n  [!] Variables with > {threshold_pct}% outliers: {flagged}")
    else:
        print(f"\n  [OK] No variable exceeds the {threshold_pct}% outlier threshold.")
    print(sep)


# ---------------------------------------------------------------------------
# Correlation analysis
# ---------------------------------------------------------------------------
def compute_correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Return Pearson correlation matrix for all numeric columns."""
    num_df = df[[c for c in NUMERIC_COLS if c in df.columns]]
    return num_df.corr(method="pearson")


def top_correlations(corr_matrix: pd.DataFrame,
                     target: str = "Yield_Tonnes_Ha",
                     top_n: int = 10) -> pd.Series:
    """Return the top N correlations with the target variable."""
    if target not in corr_matrix.columns:
        return pd.Series(dtype=float)
    return (corr_matrix[target]
            .drop(target, errors="ignore")
            .abs()
            .sort_values(ascending=False)
            .head(top_n))


def print_correlation_report(df: pd.DataFrame) -> None:
    """Print a correlation analysis report."""
    sep = "=" * 65
    corr = compute_correlation_matrix(df)

    print(f"\n{sep}")
    print("  CORRELATION ANALYSIS")
    print(sep)

    for target in ["Yield_Tonnes_Ha", "Profit_INR",
                   "Water_Efficiency_t_per_1000m3"]:
        if target not in corr.columns:
            continue
        print(f"\n  Top correlations with  {target}:")
        tc = (corr[target]
              .drop(target, errors="ignore")
              .sort_values(key=abs, ascending=False)
              .head(10))
        for col, val in tc.items():
            bar = "#" * int(abs(val) * 20)
            direction = "+" if val >= 0 else "-"
            print(f"    {col:<35} {direction}{abs(val):.4f}  {bar}")

    # Strongest pairs overall
    print(f"\n  Strongest cross-variable correlations:")
    pairs = []
    cols = corr.columns.tolist()
    for i, c1 in enumerate(cols):
        for c2 in cols[i + 1:]:
            pairs.append((c1, c2, corr.loc[c1, c2]))
    pairs.sort(key=lambda x: abs(x[2]), reverse=True)
    for c1, c2, r in pairs[:10]:
        print(f"    {c1:<30}  <->  {c2:<30}  r = {r:+.4f}")
    print(sep)


# ---------------------------------------------------------------------------
# Practical resource-management insights
# ---------------------------------------------------------------------------
def print_insights(df: pd.DataFrame) -> None:
    """Derive and print practical resource-management insights."""
    sep = "=" * 65
    print(f"\n{sep}")
    print("  PRACTICAL RESOURCE-MANAGEMENT INSIGHTS")
    print(sep)

    # 1. Most profitable crop
    crop_profit = df.groupby("Crop")["Profit_INR"].mean().sort_values(ascending=False)
    print(f"\n  1. Most profitable crop (avg profit):")
    for crop, profit in crop_profit.items():
        sign = "+" if profit >= 0 else ""
        print(f"       {crop:<20}: INR {sign}{profit:,.0f}")

    # 2. Best irrigation method for yield
    irr_yield = df.groupby("Irrigation_Method")["Yield_Tonnes_Ha"].mean()
    best_irr = irr_yield.idxmax()
    print(f"\n  2. Irrigation method with highest avg yield: "
          f"{best_irr} ({irr_yield[best_irr]:.2f} t/ha)")

    # 3. Most water-efficient irrigation
    irr_eff = df.groupby("Irrigation_Method")["Water_Efficiency_t_per_1000m3"].mean()
    best_eff_irr = irr_eff.idxmax()
    print(f"  3. Most water-efficient irrigation method: "
          f"{best_eff_irr} ({irr_eff[best_eff_irr]:.3f} t/1000 m³)")

    # 4. Season with highest profitability
    season_profit = df.groupby("Season")["Profit_INR"].mean().sort_values(ascending=False)
    best_season = season_profit.index[0]
    print(f"  4. Most profitable season: "
          f"{best_season} (avg INR {season_profit[best_season]:,.0f})")

    # 5. Percentage of farms operating at a loss
    loss_pct = (df["Profit_INR"] < 0).mean() * 100
    print(f"  5. Farms operating at a loss: {loss_pct:.1f} %")

    # 6. Correlation between seed quality and yield
    r_seed = df[["Seed_Quality_Score", "Yield_Tonnes_Ha"]].corr().iloc[0, 1]
    print(f"  6. Seed quality <-> yield correlation: r = {r_seed:.4f}")

    # 7. Optimal rainfall range (IQR of high-yield farms)
    high_yield = df[df["Yield_Tonnes_Ha"] > df["Yield_Tonnes_Ha"].quantile(0.75)]
    q1_rain = high_yield["Rainfall_mm"].quantile(0.25)
    q3_rain = high_yield["Rainfall_mm"].quantile(0.75)
    print(f"  7. Rainfall range for top-quartile yield farms: "
          f"{q1_rain:.0f} – {q3_rain:.0f} mm")

    # 8. High disease risk impact
    low_risk = df[df["Disease_Pest_Risk_pct"] < 30]["Yield_Tonnes_Ha"].mean()
    high_risk = df[df["Disease_Pest_Risk_pct"] >= 60]["Yield_Tonnes_Ha"].mean()
    print(f"  8. Mean yield at low risk (<30%): {low_risk:.2f} t/ha  |  "
          f"high risk (>=60%): {high_risk:.2f} t/ha")

    # 9. State with most farms
    top_state = df["State"].value_counts().index[0]
    print(f"  9. State with highest farm count: "
          f"{top_state} ({df['State'].value_counts().iloc[0]:,} farms)")

    # 10. Mean fertilizer use for top vs bottom yield quartile
    q75 = df["Yield_Tonnes_Ha"].quantile(0.75)
    q25 = df["Yield_Tonnes_Ha"].quantile(0.25)
    fert_top = df[df["Yield_Tonnes_Ha"] >= q75]["Fertilizer_kg_ha"].mean()
    fert_bot = df[df["Yield_Tonnes_Ha"] <= q25]["Fertilizer_kg_ha"].mean()
    print(f"  10. Avg fertilizer — top-yield quartile: {fert_top:.1f} kg/ha  |  "
          f"bottom-yield quartile: {fert_bot:.1f} kg/ha")

    print(sep)
