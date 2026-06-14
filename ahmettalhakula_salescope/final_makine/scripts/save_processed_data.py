import pandas as pd
import warnings
warnings.filterwarnings('ignore')

df = pd.read_csv('../data/raw/online_shoppers_intention.csv')

# Feature Engineering
df["Total_Duration"] = df["Administrative_Duration"] + df["Informational_Duration"] + df["ProductRelated_Duration"]
df["Engagement_Score"] = df["PageValues"] * df["ProductRelated"]
df["Bounce_Exit_Ratio"] = df["BounceRates"] / (df["ExitRates"] + 0.0001)
df["Returning_Visitor_Flag"] = (df["VisitorType"] == "Returning_Visitor").astype(int)

# Multi-Collinearity (Redundancy) Drops
df = df.drop(columns=['BounceRates', 'ProductRelated_Duration'])

# Encoding & Types
df['Revenue'] = df['Revenue'].astype(int)
df['Weekend'] = df['Weekend'].astype(int)

# İşlenmiş hali (scaling & split öncesi) kaydetme
import os
os.makedirs('../data/processed', exist_ok=True)
df.to_csv('../data/processed/shoppers_cleaned.csv', index=False)
print("Temizlenmiş ve Feature Engineering uygulanmış tam veri seti (shoppers_cleaned.csv) data/processed altına kaydedildi!")
