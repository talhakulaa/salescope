import pandas as pd
import plotly.express as px
from statsmodels.stats.outliers_influence import variance_inflation_factor

df = pd.read_csv('../data/raw/online_shoppers_intention.csv')

# Numeric Correlation
numeric_df = df.select_dtypes(include=['int64', 'float64', 'bool']).copy()
# convert bool to int
for col in numeric_df.select_dtypes(include=['bool']):
    numeric_df[col] = numeric_df[col].astype(int)

corr = numeric_df.corr()

fig = px.imshow(corr, text_auto=True, color_continuous_scale='RdBu_r', aspect="auto")
fig.update_layout(title="Korelasyon Matrisi", margin=dict(l=60, r=40, t=80, b=60))
fig.write_html(f"../figures/phase4_correlation_matrix.html")

print("--- Yüksek Korelasyonlar (>0.7 veya <-0.7) ---")
# filter high correlation pairs
high_corr = []
for col in corr.columns:
    for row in corr.index:
        if row != col and abs(corr.loc[row, col]) > 0.7:
            if (row, col, corr.loc[row, col]) not in high_corr and (col, row, corr.loc[col, row]) not in high_corr:
                high_corr.append((row, col, corr.loc[row, col]))

for pair in high_corr:
    print(f"{pair[0]} & {pair[1]}: {pair[2]:.2f}")

print("\n--- Hedef Değişken Korelasyonları (Revenue) ---")
print(corr['Revenue'].sort_values(ascending=False)[1:])

