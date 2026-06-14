import pandas as pd
import numpy as np

# Veri okuma
df = pd.read_csv('../data/raw/online_shoppers_intention.csv')

print("--- DATA SHAPE ---")
print(df.shape)
print("\n--- DATA TYPES ---")
print(df.dtypes)
print("\n--- MISSING VALUES ---")
print(df.isnull().sum()[df.isnull().sum() > 0])
print("\n--- TARGET VARIABLE (Revenue) DISTRIBUTION ---")
print(df['Revenue'].value_counts(normalize=True) * 100)
