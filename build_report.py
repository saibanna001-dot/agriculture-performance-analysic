import base64, os

fig_dir = 'outputs/figures'
files = sorted(os.listdir(fig_dir))

imgs = {}
for f in files:
    with open(os.path.join(fig_dir, f), 'rb') as fp:
        imgs[f] = base64.b64encode(fp.read()).decode()

charts = [
    ('01_seasonal_performance.png',     '01', 'Seasonal Performance',          'Box plot + grouped bar — yield and profit across Kharif, Rabi and Zaid seasons'),
    ('02_crop_performance.png',         '02', 'Crop Performance Comparison',   'Horizontal bar charts — mean yield and total production for all 8 crops'),
    ('03_crop_season_yield_heatmap.png','03', 'Crop x Season Yield Heatmap',   'Annotated heatmap — mean yield (t/ha) per crop-season combination'),
    ('04_environment_vs_yield.png',     '04', 'Environment vs Yield',          '6 scatter plots with regression lines — rainfall, temp, humidity, sunlight, pH, moisture'),
    ('05_irrigation_analysis.png',      '05', 'Irrigation Method Analysis',    '3 bar charts — mean yield, water consumed, and water-use efficiency per method'),
    ('06_irrigation_yield_boxplot.png', '06', 'Irrigation Yield Boxplot',      'Box + strip plot — full yield distribution per irrigation method'),
    ('07_water_analysis.png',           '07', 'Water Usage & Efficiency',      'Scatter (water vs yield by method) + water-efficiency histogram'),
    ('08_financial_analysis.png',       '08', 'Financial Analysis',            'Violin (profit by season), box (profit by crop), scatter (revenue vs cost)'),
    ('09_profit_by_irrigation.png',     '09', 'Profit by Irrigation Method',   'Horizontal bar — mean profit per method, green=positive, red=loss'),
    ('10_outlier_summary.png',          '10', 'Outlier Summary (IQR x 1.5)',   'Bar chart — outlier count and percentage per numerical variable'),
    ('11_correlation_heatmap.png',      '11', 'Correlation Heatmap',           'Full 22x22 lower-triangle Pearson correlation matrix, annotated'),
    ('12_scatter_matrix.png',           '12', 'Scatter Matrix (Pair Plot)',    'Pair plot of 6 key variables coloured by season (600-row sample)'),
    ('13_nutrient_vs_yield.png',        '13', 'Nutrient Inputs vs Yield',      '4 scatter plots — N, P, K, fertilizer vs yield with regression lines'),
    ('14_disease_risk_analysis.png',    '14', 'Disease & Pest Risk Analysis',  'Disease risk vs yield (by crop) + mean risk per season bar chart'),
]

css = """
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, "Segoe UI", system-ui, sans-serif;
  font-size: 14px;
  line-height: 1.6;
  color: #1f2328;
  background: #ffffff;
  padding: 40px 20px 72px;
}
.page { max-width: 820px; margin: 0 auto; }

.cover {
  border-bottom: 3px solid #1f2328;
  padding-bottom: 24px;
  margin-bottom: 36px;
}
.cover .eyebrow {
  font-size: 11px; text-transform: uppercase;
  letter-spacing: .1em; color: #57606a; margin-bottom: 6px;
}
.cover h1 { font-size: 26px; font-weight: 800; margin-bottom: 8px; line-height: 1.2; }
.cover .sub { color: #57606a; font-size: 13px; margin-bottom: 14px; }
.meta { display: flex; flex-wrap: wrap; gap: 18px; padding-top: 14px; border-top: 1px solid #e5e7eb; }
.meta-item { font-size: 12px; color: #57606a; }
.meta-item strong { color: #1f2328; display: block; font-size: 13px; }
.tag-ok { display: inline-block; padding: 2px 8px; border-radius: 99px;
           background: #dcfce7; color: #15803d; font-size: 11px; font-weight: 700; }

.toc {
  background: #f7f8fa; border: 1px solid #e5e7eb;
  border-radius: 8px; padding: 18px 22px; margin-bottom: 36px;
}
.toc h2 { font-size: 12px; text-transform: uppercase; letter-spacing: .07em;
           color: #57606a; margin-bottom: 10px; border: none; font-weight: 700; }
.toc-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 4px 20px; }
.toc-item {
  display: flex; align-items: center; gap: 8px;
  font-size: 12.5px; padding: 3px 0;
}
.toc-num {
  width: 20px; height: 20px; border-radius: 4px;
  background: #3b82d4; color: #fff;
  font-size: 10px; font-weight: 800;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}

.chart-section {
  margin-bottom: 48px;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  overflow: hidden;
}
.chart-header {
  display: flex; align-items: flex-start; gap: 12px;
  padding: 14px 18px;
  background: #f7f8fa;
  border-bottom: 1px solid #e5e7eb;
}
.badge {
  width: 28px; height: 28px; border-radius: 6px;
  background: #1f2328; color: #fff;
  font-size: 12px; font-weight: 800;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; margin-top: 1px;
}
.chart-title { font-size: 14px; font-weight: 700; color: #1f2328; }
.chart-desc  { font-size: 12px; color: #57606a; margin-top: 2px; }
.chart-section img {
  width: 100%; height: auto; display: block;
}

.footer {
  margin-top: 52px; padding-top: 14px;
  border-top: 1px solid #e5e7eb;
  text-align: center; font-size: 12px; color: #57606a;
}
"""

toc_items = '\n'.join(
    '<div class="toc-item"><span class="toc-num">{}</span> {}</div>'.format(num, title)
    for _, num, title, _ in charts
)

chart_sections = []
for fname, num, title, desc in charts:
    b64 = imgs[fname]
    section = (
        '<div class="chart-section">'
        '<div class="chart-header">'
        '<span class="badge">{}</span>'
        '<div>'
        '<div class="chart-title">{}</div>'
        '<div class="chart-desc">{}</div>'
        '</div>'
        '</div>'
        '<img src="data:image/png;base64,{}" alt="{}" />'
        '</div>'
    ).format(num, title, desc, b64, title)
    chart_sections.append(section)

charts_html = '\n'.join(chart_sections)

html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Agriculture Performance Analysis - Visualizations Report</title>
<style>
{css}
</style>
</head>
<body>
<div class="page">

<div class="cover">
  <div class="eyebrow">Data Analysis Project - Visualizations Report</div>
  <h1>Seasonal Agriculture Performance<br>All 14 Visualizations</h1>
  <div class="sub">Complete figure output from the Python analysis pipeline - 4,000 farms, 28 features, 8 Indian states, 3 seasons, 8 crops, 4 irrigation methods.</div>
  <div class="meta">
    <div class="meta-item"><strong>Figures</strong><span class="tag-ok">14 / 14 OK</span></div>
    <div class="meta-item"><strong>Dataset</strong>4,000 rows x 28 columns</div>
    <div class="meta-item"><strong>Runtime</strong>19.2 s</div>
    <div class="meta-item"><strong>Library</strong>matplotlib / seaborn / scipy</div>
    <div class="meta-item"><strong>Resolution</strong>150 DPI</div>
  </div>
</div>

<div class="toc">
  <h2>Figure Index</h2>
  <div class="toc-grid">
{toc_items}
  </div>
</div>

{charts_html}

<div class="footer">Made with IBM Bob</div>
</div>
</body>
</html>""".format(css=css, toc_items=toc_items, charts_html=charts_html)

out_path = 'outputs/visualizations_report.html'
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html)

size_kb = os.path.getsize(out_path) / 1024
print('Written: {}  ({:.0f} KB)'.format(out_path, size_kb))
