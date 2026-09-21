"""
eda.py
======
Exploratory data analysis: computes summary tables for seasonal,
crop, environment, irrigation, water, and financial dimensions.
"""

from __future__ import annotations

import pandas as pd
import numpy as np


def seasonal_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Mean agricultural metrics grouped by Season."""
    return df.groupby("Season").agg(
        Farm_Count=("Farm_ID", "count"),
        Mean_Yield=("Yield_Tonnes_Ha", "mean"),
        Mean_Production=("Production_Tonnes", "mean"),
        Mean_Profit=("Profit_INR", "mean"),
        Mean_Rainfall=("Rainfall_mm", "mean"),
        Mean_Temperature=("Avg_Temperature_C", "mean"),
        Mean_Water_Used=("Water_Used_m3", "mean"),
    ).round(2)


def crop_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Per-crop aggregated metrics."""
    return df.groupby("Crop").agg(
        Farm_Count=("Farm_ID", "count"),
        Mean_Yield=("Yield_Tonnes_Ha", "mean"),
        Median_Yield=("Yield_Tonnes_Ha", "median"),
        Total_Production=("Production_Tonnes", "sum"),
        Mean_Profit=("Profit_INR", "mean"),
        Mean_Revenue=("Revenue_INR", "mean"),
        Pct_Profitable=(
            "Profit_INR", lambda x: (x > 0).mean() * 100
        ),
    ).round(2).sort_values("Mean_Yield", ascending=False)


def irrigation_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Per-irrigation-method comparison."""
    return df.groupby("Irrigation_Method").agg(
        Farm_Count=("Farm_ID", "count"),
        Mean_Yield=("Yield_Tonnes_Ha", "mean"),
        Mean_Water_Used=("Water_Used_m3", "mean"),
        Mean_Efficiency=("Water_Efficiency_t_per_1000m3", "mean"),
        Mean_Profit=("Profit_INR", "mean"),
        Pct_Profitable=(
            "Profit_INR", lambda x: (x > 0).mean() * 100
        ),
    ).round(2).sort_values("Mean_Yield", ascending=False)


def water_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Water usage statistics per season × irrigation method."""
    return df.groupby(["Season", "Irrigation_Method"]).agg(
        Mean_Water_Used=("Water_Used_m3", "mean"),
        Mean_Efficiency=("Water_Efficiency_t_per_1000m3", "mean"),
        Mean_Yield=("Yield_Tonnes_Ha", "mean"),
    ).round(2)


def financial_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Revenue, cost, and profit summary per crop."""
    summary = df.groupby("Crop").agg(
        Mean_Revenue=("Revenue_INR", "mean"),
        Mean_Cost=("Total_Cost_INR", "mean"),
        Mean_Profit=("Profit_INR", "mean"),
        Pct_Profitable=("Profit_INR", lambda x: (x > 0).mean() * 100),
    ).round(2).sort_values("Mean_Profit", ascending=False)
    summary["Profit_Margin_pct"] = (
        summary["Mean_Profit"] / summary["Mean_Revenue"] * 100
    ).round(2)
    return summary


def top_performing_states(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """States ranked by mean yield."""
    return (
        df.groupby("State").agg(
            Farm_Count=("Farm_ID", "count"),
            Mean_Yield=("Yield_Tonnes_Ha", "mean"),
            Mean_Profit=("Profit_INR", "mean"),
        )
        .sort_values("Mean_Yield", ascending=False)
        .head(top_n)
        .round(2)
    )


def print_eda_tables(df: pd.DataFrame) -> None:
    """Print all EDA summary tables."""
    sep = "=" * 65

    print(f"\n{sep}")
    print("  SEASONAL AGRICULTURAL PERFORMANCE")
    print(sep)
    print(seasonal_summary(df).to_string())

    print(f"\n{sep}")
    print("  CROP PERFORMANCE SUMMARY")
    print(sep)
    print(crop_summary(df).to_string())

    print(f"\n{sep}")
    print("  IRRIGATION METHOD SUMMARY")
    print(sep)
    print(irrigation_summary(df).to_string())

    print(f"\n{sep}")
    print("  WATER USAGE SUMMARY (Season × Irrigation Method)")
    print(sep)
    print(water_summary(df).to_string())

    print(f"\n{sep}")
    print("  FINANCIAL SUMMARY BY CROP")
    print(sep)
    print(financial_summary(df).to_string())

    print(f"\n{sep}")
    print("  TOP 10 STATES BY MEAN YIELD")
    print(sep)
    print(top_performing_states(df).to_string())
    print(sep)
