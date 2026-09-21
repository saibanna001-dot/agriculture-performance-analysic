"""
visualizations.py
=================
All matplotlib / seaborn plot helpers.
Each function saves a figure to `output_dir` and returns the file path.
"""

from __future__ import annotations

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")          # non-interactive backend for file output
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from scipy import stats

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Global style
# ---------------------------------------------------------------------------
PALETTE = "Set2"
FIG_DPI = 150
sns.set_theme(style="whitegrid", palette=PALETTE, font_scale=1.0)


def _save(fig: plt.Figure, output_dir: str, filename: str) -> str:
    path = os.path.join(output_dir, filename)
    fig.savefig(path, dpi=FIG_DPI, bbox_inches="tight")
    plt.close(fig)
    return path


# ---------------------------------------------------------------------------
# 1. Seasonal performance
# ---------------------------------------------------------------------------
def plot_seasonal_yield(df: pd.DataFrame, output_dir: str) -> str:
    """Box plots of Yield_Tonnes_Ha by Season."""
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Agricultural Performance by Season", fontsize=14, fontweight="bold")

    season_order = sorted(df["Season"].dropna().unique())

    # Yield distribution
    sns.boxplot(data=df, x="Season", y="Yield_Tonnes_Ha",
                order=season_order, palette=PALETTE, ax=axes[0])
    axes[0].set_title("Yield Distribution (Tonnes/Ha)")
    axes[0].set_xlabel("Season")
    axes[0].set_ylabel("Yield (t/ha)")

    # Mean yield + profit per season
    summary = df.groupby("Season").agg(
        Mean_Yield=("Yield_Tonnes_Ha", "mean"),
        Mean_Profit=("Profit_INR", "mean"),
    ).reindex(season_order)

    x = np.arange(len(summary))
    width = 0.35
    colors = sns.color_palette(PALETTE, 2)
    bars1 = axes[1].bar(x - width / 2, summary["Mean_Yield"], width,
                        label="Avg Yield (t/ha)", color=colors[0])
    ax2 = axes[1].twinx()
    bars2 = ax2.bar(x + width / 2, summary["Mean_Profit"], width,
                    label="Avg Profit (INR)", color=colors[1], alpha=0.8)
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(summary.index)
    axes[1].set_title("Mean Yield & Profit by Season")
    axes[1].set_ylabel("Avg Yield (t/ha)")
    ax2.set_ylabel("Avg Profit (INR)")
    lines = [bars1, bars2]
    labels = [b.get_label() for b in lines]
    axes[1].legend(lines, labels, loc="upper left", fontsize=8)

    plt.tight_layout()
    return _save(fig, output_dir, "01_seasonal_performance.png")


# ---------------------------------------------------------------------------
# 2. Crop yield & production comparison
# ---------------------------------------------------------------------------
def plot_crop_performance(df: pd.DataFrame, output_dir: str) -> str:
    """Bar charts comparing crop yield and production."""
    crop_stats = df.groupby("Crop").agg(
        Mean_Yield=("Yield_Tonnes_Ha", "mean"),
        Total_Production=("Production_Tonnes", "sum"),
        Farm_Count=("Farm_ID", "count"),
    ).sort_values("Mean_Yield", ascending=False)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Crop Performance Comparison", fontsize=14, fontweight="bold")

    colors = sns.color_palette(PALETTE, len(crop_stats))

    axes[0].barh(crop_stats.index, crop_stats["Mean_Yield"], color=colors)
    axes[0].set_xlabel("Mean Yield (Tonnes / Ha)")
    axes[0].set_title("Mean Yield by Crop")
    axes[0].invert_yaxis()
    for i, v in enumerate(crop_stats["Mean_Yield"]):
        axes[0].text(v + 0.02, i, f"{v:.2f}", va="center", fontsize=8)

    axes[1].barh(crop_stats.index, crop_stats["Total_Production"] / 1_000,
                 color=colors)
    axes[1].set_xlabel("Total Production (× 1 000 Tonnes)")
    axes[1].set_title("Total Production by Crop")
    axes[1].invert_yaxis()

    plt.tight_layout()
    return _save(fig, output_dir, "02_crop_performance.png")


def plot_crop_yield_season_heatmap(df: pd.DataFrame, output_dir: str) -> str:
    """Heatmap of mean yield per crop × season."""
    pivot = df.pivot_table(values="Yield_Tonnes_Ha", index="Crop",
                           columns="Season", aggfunc="mean")
    fig, ax = plt.subplots(figsize=(9, 6))
    sns.heatmap(pivot, annot=True, fmt=".2f", cmap="YlGn",
                linewidths=0.5, ax=ax)
    ax.set_title("Mean Yield (t/ha) — Crop × Season", fontsize=13,
                 fontweight="bold")
    ax.set_xlabel("Season")
    ax.set_ylabel("Crop")
    plt.tight_layout()
    return _save(fig, output_dir, "03_crop_season_yield_heatmap.png")


# ---------------------------------------------------------------------------
# 3. Environmental conditions vs outcomes
# ---------------------------------------------------------------------------
def plot_env_vs_yield(df: pd.DataFrame, output_dir: str) -> str:
    """Scatter plots of key environmental variables vs yield."""
    env_vars = [
        ("Rainfall_mm", "Rainfall (mm)"),
        ("Avg_Temperature_C", "Avg Temperature (C)"),
        ("Humidity_pct", "Humidity (%)"),
        ("Sunlight_Hours_Day", "Sunlight (hrs/day)"),
        ("Soil_pH", "Soil pH"),
        ("Soil_Moisture_pct", "Soil Moisture (%)"),
    ]

    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    fig.suptitle("Environmental Conditions vs. Yield", fontsize=14,
                 fontweight="bold")
    axes = axes.flatten()

    sample = df.sample(min(1000, len(df)), random_state=42)

    for ax, (col, label) in zip(axes, env_vars):
        if col not in df.columns:
            continue
        ax.scatter(sample[col], sample["Yield_Tonnes_Ha"],
                   alpha=0.35, s=12, color="#3b7cb8")
        # regression line
        valid = sample[[col, "Yield_Tonnes_Ha"]].dropna()
        if len(valid) > 2:
            m, b, r, p, _ = stats.linregress(valid[col], valid["Yield_Tonnes_Ha"])
            xline = np.linspace(valid[col].min(), valid[col].max(), 100)
            ax.plot(xline, m * xline + b, color="crimson", linewidth=1.5)
            ax.set_title(f"{label}\n(r = {r:.2f}, p = {p:.3f})", fontsize=9)
        else:
            ax.set_title(label, fontsize=9)
        ax.set_xlabel(label, fontsize=8)
        ax.set_ylabel("Yield (t/ha)", fontsize=8)

    plt.tight_layout()
    return _save(fig, output_dir, "04_environment_vs_yield.png")


# ---------------------------------------------------------------------------
# 4. Irrigation method analysis
# ---------------------------------------------------------------------------
def plot_irrigation_analysis(df: pd.DataFrame, output_dir: str) -> str:
    """Compare yield, water used, and efficiency across irrigation methods."""
    irr_stats = df.groupby("Irrigation_Method").agg(
        Mean_Yield=("Yield_Tonnes_Ha", "mean"),
        Mean_Water=("Water_Used_m3", "mean"),
        Mean_Efficiency=("Water_Efficiency_t_per_1000m3", "mean"),
        Count=("Farm_ID", "count"),
    ).sort_values("Mean_Yield", ascending=False)

    methods = irr_stats.index.tolist()
    colors = sns.color_palette(PALETTE, len(methods))

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle("Irrigation Method Analysis", fontsize=14, fontweight="bold")

    for ax, col, ylabel, title in zip(
        axes,
        ["Mean_Yield", "Mean_Water", "Mean_Efficiency"],
        ["Mean Yield (t/ha)", "Mean Water Used (m³)", "Water Efficiency (t/1000 m³)"],
        ["Mean Yield by Irrigation", "Water Consumption by Method",
         "Water-Use Efficiency"],
    ):
        bars = ax.bar(methods, irr_stats[col], color=colors)
        ax.set_title(title)
        ax.set_xlabel("Irrigation Method")
        ax.set_ylabel(ylabel)
        ax.tick_params(axis="x", rotation=15)
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h * 1.01,
                    f"{h:.2f}", ha="center", va="bottom", fontsize=8)

    plt.tight_layout()
    return _save(fig, output_dir, "05_irrigation_analysis.png")


def plot_irrigation_yield_boxplot(df: pd.DataFrame, output_dir: str) -> str:
    """Box + strip plot of yield per irrigation method."""
    order = (df.groupby("Irrigation_Method")["Yield_Tonnes_Ha"]
             .median().sort_values(ascending=False).index.tolist())

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.boxplot(data=df, x="Irrigation_Method", y="Yield_Tonnes_Ha",
                order=order, palette=PALETTE, ax=ax, fliersize=2)
    sns.stripplot(data=df.sample(min(600, len(df)), random_state=1),
                  x="Irrigation_Method", y="Yield_Tonnes_Ha", order=order,
                  color="black", alpha=0.15, size=2.5, jitter=True, ax=ax)
    ax.set_title("Yield Distribution by Irrigation Method",
                 fontsize=13, fontweight="bold")
    ax.set_xlabel("Irrigation Method")
    ax.set_ylabel("Yield (t/ha)")
    plt.tight_layout()
    return _save(fig, output_dir, "06_irrigation_yield_boxplot.png")


# ---------------------------------------------------------------------------
# 5. Water usage & efficiency
# ---------------------------------------------------------------------------
def plot_water_analysis(df: pd.DataFrame, output_dir: str) -> str:
    """Scatter of Water_Used vs Yield; efficiency distribution."""
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Water Usage & Efficiency Analysis", fontsize=14, fontweight="bold")

    # Water used vs yield coloured by irrigation method
    irr_methods = df["Irrigation_Method"].dropna().unique()
    palette_map = dict(zip(irr_methods, sns.color_palette(PALETTE, len(irr_methods))))
    sample = df.sample(min(1200, len(df)), random_state=7)
    for method in irr_methods:
        sub = sample[sample["Irrigation_Method"] == method]
        axes[0].scatter(sub["Water_Used_m3"], sub["Yield_Tonnes_Ha"],
                        alpha=0.4, s=12, label=method,
                        color=palette_map.get(method, "grey"))
    axes[0].set_xlabel("Water Used (m³)")
    axes[0].set_ylabel("Yield (t/ha)")
    axes[0].set_title("Water Used vs Yield\n(coloured by irrigation method)")
    axes[0].legend(fontsize=8, markerscale=1.5)

    # Water efficiency histogram
    axes[1].hist(df["Water_Efficiency_t_per_1000m3"].dropna(), bins=40,
                 color="#4b9cd3", edgecolor="white")
    median_eff = df["Water_Efficiency_t_per_1000m3"].median()
    axes[1].axvline(median_eff, color="crimson", linestyle="--",
                    label=f"Median: {median_eff:.2f}")
    axes[1].set_xlabel("Water Efficiency (t / 1 000 m³)")
    axes[1].set_ylabel("Farm Count")
    axes[1].set_title("Distribution of Water-Use Efficiency")
    axes[1].legend()

    plt.tight_layout()
    return _save(fig, output_dir, "07_water_analysis.png")


# ---------------------------------------------------------------------------
# 6. Revenue, cost & profit
# ---------------------------------------------------------------------------
def plot_financial_analysis(df: pd.DataFrame, output_dir: str) -> str:
    """Violin plots and scatter of financial variables."""
    fig, axes = plt.subplots(1, 3, figsize=(16, 6))
    fig.suptitle("Financial Performance Analysis", fontsize=14, fontweight="bold")

    # Profit distribution by season
    season_order = sorted(df["Season"].dropna().unique())
    sns.violinplot(data=df, x="Season", y="Profit_INR",
                   order=season_order, palette=PALETTE,
                   inner="quartile", ax=axes[0])
    axes[0].axhline(0, color="red", linestyle="--", linewidth=1)
    axes[0].set_title("Profit Distribution by Season")
    axes[0].set_ylabel("Profit (INR)")
    axes[0].yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"{x/1e6:.1f}M"))

    # Profit distribution by crop
    crop_order = (df.groupby("Crop")["Profit_INR"]
                  .median().sort_values(ascending=False).index.tolist())
    sns.boxplot(data=df, x="Crop", y="Profit_INR", order=crop_order,
                palette=PALETTE, ax=axes[1], fliersize=2)
    axes[1].axhline(0, color="red", linestyle="--", linewidth=1)
    axes[1].set_title("Profit Distribution by Crop")
    axes[1].set_ylabel("Profit (INR)")
    axes[1].tick_params(axis="x", rotation=25)
    axes[1].yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"{x/1e6:.1f}M"))

    # Revenue vs Cost scatter
    sample = df.sample(min(800, len(df)), random_state=3)
    axes[2].scatter(sample["Total_Cost_INR"], sample["Revenue_INR"],
                    alpha=0.35, s=12, color="#5a9e6f")
    max_val = max(sample["Total_Cost_INR"].max(), sample["Revenue_INR"].max())
    axes[2].plot([0, max_val], [0, max_val], "r--", linewidth=1,
                 label="Break-even line")
    axes[2].set_xlabel("Total Cost (INR)")
    axes[2].set_ylabel("Revenue (INR)")
    axes[2].set_title("Revenue vs Total Cost")
    axes[2].legend(fontsize=8)
    axes[2].xaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"{x/1e6:.1f}M"))
    axes[2].yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"{x/1e6:.1f}M"))

    plt.tight_layout()
    return _save(fig, output_dir, "08_financial_analysis.png")


def plot_profit_by_irrigation(df: pd.DataFrame, output_dir: str) -> str:
    """Bar chart: mean profit per irrigation method."""
    stats_df = df.groupby("Irrigation_Method")["Profit_INR"].mean().sort_values()
    colors = ["#d73027" if v < 0 else "#1a9850" for v in stats_df.values]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.barh(stats_df.index, stats_df.values, color=colors)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Mean Profit (INR)")
    ax.set_title("Mean Profit by Irrigation Method", fontsize=13,
                 fontweight="bold")
    ax.xaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"{x/1e6:.2f}M"))
    for bar in bars:
        w = bar.get_width()
        ax.text(w + (abs(w) * 0.01), bar.get_y() + bar.get_height() / 2,
                f"{w/1e6:.3f}M", va="center", fontsize=8)
    plt.tight_layout()
    return _save(fig, output_dir, "09_profit_by_irrigation.png")


# ---------------------------------------------------------------------------
# 7. Outlier detection
# ---------------------------------------------------------------------------
def plot_outlier_summary(df: pd.DataFrame, outlier_info: dict,
                         output_dir: str) -> str:
    """Bar chart showing number of outliers per variable."""
    cols = list(outlier_info.keys())
    counts = [outlier_info[c]["count"] for c in cols]
    pcts = [outlier_info[c]["pct"] for c in cols]

    fig, ax = plt.subplots(figsize=(11, 5))
    bars = ax.bar(cols, counts, color=sns.color_palette("Reds_r", len(cols)))
    ax.set_title("Outlier Count per Numerical Variable (IQR Method)",
                 fontsize=13, fontweight="bold")
    ax.set_ylabel("Number of Outlier Rows")
    ax.tick_params(axis="x", rotation=45)
    for bar, pct in zip(bars, pcts):
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 1,
                f"{pct:.1f}%", ha="center", va="bottom", fontsize=7)
    plt.tight_layout()
    return _save(fig, output_dir, "10_outlier_summary.png")


# ---------------------------------------------------------------------------
# 8. Correlation heatmap
# ---------------------------------------------------------------------------
def plot_correlation_heatmap(df: pd.DataFrame, output_dir: str) -> str:
    """Full correlation heatmap of all numeric columns."""
    from src.data_loader import NUMERIC_COLS
    num_df = df[[c for c in NUMERIC_COLS if c in df.columns]]
    corr = num_df.corr()

    fig, ax = plt.subplots(figsize=(16, 13))
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="coolwarm",
                center=0, linewidths=0.4, ax=ax,
                annot_kws={"size": 7}, vmin=-1, vmax=1)
    ax.set_title("Correlation Heatmap — Numerical Agricultural Features",
                 fontsize=14, fontweight="bold")
    plt.tight_layout()
    return _save(fig, output_dir, "11_correlation_heatmap.png")


def plot_key_scatter_matrix(df: pd.DataFrame, output_dir: str) -> str:
    """Pair plot of the most analytically important variables."""
    key = ["Yield_Tonnes_Ha", "Profit_INR", "Water_Efficiency_t_per_1000m3",
           "Rainfall_mm", "Fertilizer_kg_ha", "Seed_Quality_Score"]
    available = [c for c in key if c in df.columns]
    sample = df[available + ["Season"]].sample(min(600, len(df)), random_state=99)

    g = sns.pairplot(sample, hue="Season", diag_kind="kde",
                     plot_kws={"alpha": 0.35, "s": 12},
                     palette=PALETTE)
    g.figure.suptitle("Scatter Matrix — Key Agricultural Variables",
                       y=1.02, fontsize=13, fontweight="bold")
    path = os.path.join(output_dir, "12_scatter_matrix.png")
    g.figure.savefig(path, dpi=FIG_DPI, bbox_inches="tight")
    plt.close(g.figure)
    return path


# ---------------------------------------------------------------------------
# 9. Resource management insights
# ---------------------------------------------------------------------------
def plot_nutrient_vs_yield(df: pd.DataFrame, output_dir: str) -> str:
    """Scatter plots: Nitrogen, Phosphorus, Potassium vs yield."""
    nutrients = [
        ("Nitrogen_kg_ha", "Nitrogen (kg/ha)"),
        ("Phosphorus_kg_ha", "Phosphorus (kg/ha)"),
        ("Potassium_kg_ha", "Potassium (kg/ha)"),
        ("Fertilizer_kg_ha", "Total Fertilizer (kg/ha)"),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    fig.suptitle("Nutrient & Fertilizer Inputs vs Yield",
                 fontsize=14, fontweight="bold")
    axes = axes.flatten()
    sample = df.sample(min(1000, len(df)), random_state=5)

    for ax, (col, label) in zip(axes, nutrients):
        if col not in df.columns:
            continue
        ax.scatter(sample[col], sample["Yield_Tonnes_Ha"],
                   alpha=0.3, s=12, color="#7d5ea6")
        valid = sample[[col, "Yield_Tonnes_Ha"]].dropna()
        if len(valid) > 2:
            m, b, r, p, _ = stats.linregress(valid[col],
                                              valid["Yield_Tonnes_Ha"])
            xline = np.linspace(valid[col].min(), valid[col].max(), 100)
            ax.plot(xline, m * xline + b, color="darkorange", linewidth=1.5)
            ax.set_title(f"{label}\n(r = {r:.2f})", fontsize=9)
        else:
            ax.set_title(label, fontsize=9)
        ax.set_xlabel(label, fontsize=8)
        ax.set_ylabel("Yield (t/ha)", fontsize=8)

    plt.tight_layout()
    return _save(fig, output_dir, "13_nutrient_vs_yield.png")


def plot_disease_risk_analysis(df: pd.DataFrame, output_dir: str) -> str:
    """Disease/pest risk vs yield, coloured by crop."""
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Disease & Pest Risk Analysis", fontsize=14, fontweight="bold")

    crops = df["Crop"].dropna().unique()
    pal = dict(zip(crops, sns.color_palette(PALETTE, len(crops))))
    sample = df.sample(min(1000, len(df)), random_state=11)

    for crop in crops:
        sub = sample[sample["Crop"] == crop]
        axes[0].scatter(sub["Disease_Pest_Risk_pct"], sub["Yield_Tonnes_Ha"],
                        alpha=0.35, s=12, label=crop, color=pal[crop])
    axes[0].set_xlabel("Disease/Pest Risk (%)")
    axes[0].set_ylabel("Yield (t/ha)")
    axes[0].set_title("Disease Risk vs Yield (by Crop)")
    axes[0].legend(fontsize=7, markerscale=1.5)

    # Mean disease risk per season
    season_risk = df.groupby("Season")["Disease_Pest_Risk_pct"].mean().sort_values(
        ascending=False)
    axes[1].bar(season_risk.index, season_risk.values,
                color=sns.color_palette("Reds", len(season_risk)))
    axes[1].set_title("Mean Disease/Pest Risk by Season")
    axes[1].set_xlabel("Season")
    axes[1].set_ylabel("Mean Risk (%)")
    for i, v in enumerate(season_risk.values):
        axes[1].text(i, v + 0.3, f"{v:.1f}%", ha="center", fontsize=9)

    plt.tight_layout()
    return _save(fig, output_dir, "14_disease_risk_analysis.png")
