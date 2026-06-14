import pandas as pd
import plotly.express as px
import os

df = pd.read_csv('../data/raw/online_shoppers_intention.csv')

def apply_premium_layout(fig, title):
    fig.update_layout(
        title={"text": title, "x": 0.03, "font": {"size": 20, "family": "Arial Black", "color": "#1F2937"}},
        template="plotly_white", margin=dict(l=60, r=40, t=80, b=60)
    )
    return fig

# Numeric vs Target
num_vs_target = ['ProductRelated', 'ProductRelated_Duration', 'PageValues', 'BounceRates']
for col in num_vs_target:
    fig = px.box(df, x="Revenue", y=col, color="Revenue", color_discrete_sequence=["#F18F01", "#06A77D"])
    fig = apply_premium_layout(fig, f"Revenue vs {col}")
    fig.write_html(f"../figures/phase3_boxplot_revenue_{col}.html")
    # T-test or simply group means
    means = df.groupby('Revenue')[col].mean()
    print(f"\n{col} Mean by Revenue:")
    print(means)

# Categorical vs Target
cat_vs_target = ['VisitorType', 'Month']
for col in cat_vs_target:
    grouped = df.groupby(col)['Revenue'].mean().reset_index().sort_values(by='Revenue', ascending=False)
    grouped['Revenue_pct'] = grouped['Revenue'] * 100
    fig = px.bar(grouped, x=col, y='Revenue_pct', color=col, color_discrete_sequence=px.colors.qualitative.Pastel)
    fig = apply_premium_layout(fig, f"{col} bazlı Satın Alma (Revenue) Oranları")
    fig.write_html(f"../figures/phase3_bar_revenue_{col}.html")
    print(f"\nConversion Rate % by {col}:")
    print(grouped[['Revenue_pct', col]])

