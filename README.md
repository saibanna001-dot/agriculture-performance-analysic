# Agriculture Performance Data Analysis

A comprehensive Python data-analysis project exploring seasonal agricultural
performance across Indian states using a 4 000-row dataset.

## Project Structure

```
agriculture_analysis/
├── data/
│   └── seasonal_agriculture_performance_dataset.csv   # raw dataset
├── outputs/
│   └── figures/          # all saved plots (.png)
├── src/
│   ├── __init__.py
│   ├── data_loader.py    # loading, schema validation, missing-value audit
│   ├── eda.py            # seasonal, crop, environment, irrigation analyses
│   ├── statistics.py     # outlier detection & correlation analysis
│   └── visualizations.py # all matplotlib / seaborn plot helpers
├── main.py               # orchestrates full pipeline
├── requirements.txt
└── README.md
```

## Analyses Covered

| # | Topic |
|---|-------|
| 1 | Dataset structure & data-type overview |
| 2 | Missing value audit & data-quality report |
| 3 | Seasonal agricultural performance |
| 4 | Crop yield & production comparison |
| 5 | Environmental conditions vs. outcomes |
| 6 | Irrigation method effects on yield |
| 7 | Water usage & water-use efficiency |
| 8 | Revenue, cost & profit patterns |
| 9 | Outlier detection (IQR method) |
| 10 | Correlation analysis (heatmap + scatter matrix) |
| 11 | Practical resource-management insights |

## Setup & Usage

```bash
# 1. Create virtual environment (recommended)
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the full analysis pipeline
python main.py
```

All figures are saved to `outputs/figures/`.
A summary report is printed to the console.

## Dataset Columns

| Column | Description |
|--------|-------------|
| Farm_ID | Unique farm identifier |
| State / District | Geographic location |
| Crop | Crop type (Rice, Wheat, Maize, etc.) |
| Season | Kharif / Rabi / Zaid |
| Farm_Area_Hectares | Farm size |
| Rainfall_mm | Seasonal rainfall |
| Avg_Temperature_C | Average temperature |
| Humidity_pct | Relative humidity % |
| Sunlight_Hours_Day | Daily sunlight hours |
| Soil_pH / Soil_Moisture_pct | Soil conditions |
| Nitrogen / Phosphorus / Potassium (kg/ha) | Nutrient inputs |
| Irrigation_Method | Drip / Flood / Sprinkler / Rainfed |
| Fertilizer_kg_ha / Pesticide_Litre_ha | Input quantities |
| Seed_Quality_Score | Seed quality (0–1) |
| Yield_Tonnes_Ha | Crop yield per hectare |
| Production_Tonnes | Total production |
| Market_Price_INR_Tonne | Market price |
| Total_Cost_INR / Revenue_INR / Profit_INR | Financials |
| Water_Used_m3 | Total water used |
| Water_Efficiency_t_per_1000m3 | Water-use efficiency |
| Disease_Pest_Risk_pct | Disease/pest risk % |
