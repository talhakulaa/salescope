import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

os.makedirs("../figures", exist_ok=True)
df = pd.read_csv('../data/raw/online_shoppers_intention.csv')

def apply_premium_layout(fig, title):
    fig.update_layout(
        title={
            "text": title,
            "x": 0.03,
            "xanchor": "left",
            "font": {"size": 20, "family": "Arial Black", "color": "#1F2937"}
        },
        template="plotly_white",
        paper_bgcolor="#FBFBF8",
        plot_bgcolor="#FBFBF8",
        font={"family": "Arial", "size": 13, "color": "#374151"},
        margin=dict(l=60, r=40, t=80, b=60),
        legend_title_text="Kategori"
    )
    return fig

# Numeric variables to analyze
num_cols = ['ProductRelated', 'ProductRelated_Duration', 'PageValues', 'BounceRates', 'ExitRates']

for col in num_cols:
    fig = px.histogram(df, x=col, nbins=50, color_discrete_sequence=["#2E86AB"])
    fig = apply_premium_layout(fig, f"{col} Histogramı")
    fig.write_html(f"../figures/phase2_histogram_{col}.html")
    # Also calculate outliers (IQR)
    q1 = df[col].quantile(0.25)
    q3 = df[col].quantile(0.75)
    iqr = q3 - q1
    outliers = ((df[col] < (q1 - 1.5 * iqr)) | (df[col] > (q3 + 1.5 * iqr))).mean() * 100
    skew = df[col].skew()
    print(f"{col} -> Outlier Oranı: %{outliers:.2f}, Çarpıklık: {skew:.2f}")

# Categorical variables
cat_cols = ['Month', 'VisitorType', 'Weekend', 'TrafficType']
for col in cat_cols:
    fig = px.bar(df[col].value_counts().reset_index(), x='count', y=col, orientation='h', color_discrete_sequence=["#A23B72"])
    fig = apply_premium_layout(fig, f"{col} Dağılımı")
    fig.write_html(f"../figures/phase2_bar_{col}.html")
    print(f"\n{col} Başa Gelen Kategoriler:")
    print(df[col].value_counts(normalize=True).head(3) * 100)

