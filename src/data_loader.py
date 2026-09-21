"""
data_loader.py
==============
Handles CSV loading, schema validation, missing-value audit,
and a printable data-quality report.
"""

from __future__ import annotations

import os
import pandas as pd
import numpy as np


# ---------------------------------------------------------------------------
# Expected schema
# ---------------------------------------------------------------------------
NUMERIC_COLS = [
    "Farm_Area_Hectares", "Rainfall_mm", "Avg_Temperature_C", "Humidity_pct",
    "Sunlight_Hours_Day", "Soil_pH", "Soil_Moisture_pct", "Nitrogen_kg_ha",
    "Phosphorus_kg_ha", "Potassium_kg_ha", "Fertilizer_kg_ha",
    "Pesticide_Litre_ha", "Seed_Quality_Score", "Yield_Tonnes_Ha",
    "Production_Tonnes", "Market_Price_INR_Tonne", "Total_Cost_INR",
    "Revenue_INR", "Profit_INR", "Water_Used_m3",
    "Water_Efficiency_t_per_1000m3", "Disease_Pest_Risk_pct",
]

CATEGORICAL_COLS = [
    "Farm_ID", "State", "District", "Crop", "Season", "Irrigation_Method",
]


def load_data(csv_path: str) -> pd.DataFrame:
    """Load the CSV, coerce numeric types, and return the DataFrame."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset not found: {csv_path}")

    df = pd.read_csv(csv_path)

    # Coerce numeric columns
    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def describe_structure(df: pd.DataFrame) -> None:
    """Print a structured overview of the DataFrame."""
    sep = "=" * 65

    print(f"\n{sep}")
    print("  DATASET STRUCTURE OVERVIEW")
    print(sep)
    print(f"  Rows          : {df.shape[0]:,}")
    print(f"  Columns       : {df.shape[1]}")
    print(f"  Memory usage  : {df.memory_usage(deep=True).sum() / 1024:.1f} KB")

    print(f"\n{'Column':<35} {'Dtype':<15} {'Non-Null':>10}")
    print("-" * 65)
    for col in df.columns:
        print(f"  {col:<33} {str(df[col].dtype):<15} {df[col].notna().sum():>10,}")

    print(f"\n  Categorical columns : {[c for c in CATEGORICAL_COLS if c in df.columns]}")
    print(f"  Numeric columns     : {len([c for c in NUMERIC_COLS if c in df.columns])}")


def missing_value_audit(df: pd.DataFrame) -> pd.DataFrame:
    """Return a DataFrame summarising missing values per column."""
    total = df.shape[0]
    missing = df.isnull().sum()
    pct = (missing / total * 100).round(2)
    audit = pd.DataFrame({
        "Missing_Count": missing,
        "Missing_Pct": pct,
    })
    audit = audit[audit["Missing_Count"] > 0].sort_values("Missing_Pct", ascending=False)
    return audit


def data_quality_report(df: pd.DataFrame) -> None:
    """Print a full data-quality report."""
    sep = "=" * 65
    print(f"\n{sep}")
    print("  DATA QUALITY REPORT")
    print(sep)

    # Missing values
    audit = missing_value_audit(df)
    if audit.empty:
        print("  [OK] No missing values found.")
    else:
        print(f"  [!] Columns with missing values ({len(audit)}):")
        print(audit.to_string())

    # Duplicate rows
    dupes = df.duplicated().sum()
    print(f"\n  Duplicate rows : {dupes}")

    # Negative profit / revenue check
    neg_profit = (df["Profit_INR"] < 0).sum()
    neg_revenue = (df["Revenue_INR"] < 0).sum()
    print(f"  Farms with negative profit  : {neg_profit:,} "
          f"({neg_profit / len(df) * 100:.1f} %)")
    print(f"  Farms with negative revenue : {neg_revenue:,}")

    # Seed quality range check  (expected 0-1)
    invalid_seed = ((df["Seed_Quality_Score"] < 0) |
                    (df["Seed_Quality_Score"] > 1)).sum()
    print(f"  Invalid Seed_Quality_Score  : {invalid_seed}")

    # Soil pH range check (normal 4–9)
    invalid_ph = ((df["Soil_pH"] < 3) | (df["Soil_pH"] > 10)).sum()
    print(f"  Suspicious Soil_pH values   : {invalid_ph}")

    # Unique categorical values
    print("\n  Unique values per categorical column:")
    for col in CATEGORICAL_COLS:
        if col in df.columns and col != "Farm_ID":
            vals = df[col].unique()
            print(f"    {col:<22}: {len(vals)}  -> {sorted(vals[:8].tolist())}"
                  f"{'...' if len(vals) > 8 else ''}")

    # Descriptive statistics for key numeric cols
    key_cols = ["Yield_Tonnes_Ha", "Profit_INR", "Water_Used_m3",
                "Water_Efficiency_t_per_1000m3", "Rainfall_mm"]
    available = [c for c in key_cols if c in df.columns]
    print(f"\n  Descriptive statistics (key numeric columns):")
    print(df[available].describe().round(2).to_string())
    print(sep)
