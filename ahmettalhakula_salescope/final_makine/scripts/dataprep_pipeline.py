import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler, OneHotEncoder, FunctionTransformer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib
import warnings
warnings.filterwarnings('ignore')

# Klasörlerin oluşturulması
os.makedirs('../data/model_ready', exist_ok=True)
os.makedirs('../models', exist_ok=True)

print("1. Veri Okunuyor...")
df = pd.read_csv('../data/raw/online_shoppers_intention.csv')

print("2. Feature Engineering (Phase 5) Uygulanıyor...")
# Toplam etkileşim süresi
df["Total_Duration"] = df["Administrative_Duration"] + df["Informational_Duration"] + df["ProductRelated_Duration"]
# Ziyaretçinin sitedeki kalitesi ve sepete ilgi düzeyi
df["Engagement_Score"] = df["PageValues"] * df["ProductRelated"]
# Hemen çıkma tehlikesi endeksi (0 division önlemi ile)
df["Bounce_Exit_Ratio"] = df["BounceRates"] / (df["ExitRates"] + 0.0001)
# Yeni/Eski müşteri ayrımı için Binary Flag
df["Returning_Visitor_Flag"] = (df["VisitorType"] == "Returning_Visitor").astype(int)

print("3. Multicollinearity Çözümü (Phase 6): BounceRates ve ProductRelated_Duration düşürülüyor...")
# EDA Raporunda r=0.91 (BounceRates/ExitRates) ve r=0.86 (ProductRelated/Duration) olduğu için redundancy engelleniyor.
# YBS Notu: ProductRelated_Duration iş zekası bazlı "Total_Duration" a yedirildikten sora drop ediliyor.
df = df.drop(columns=['BounceRates', 'ProductRelated_Duration'])

print("4. Veri Tipi Dönüşümleri (Target & Binary)...")
df['Revenue'] = df['Revenue'].astype(int)
df['Weekend'] = df['Weekend'].astype(int)

print("5. Train/Test Stratified Split (Phase 2)...")
X = df.drop(columns=['Revenue'])
y = df['Revenue']

# Değişken grupları
cat_nominal = ['VisitorType', 'OperatingSystems', 'Browser', 'Region', 'TrafficType']
cat_ordinal = ['Month']
passthrough_cols = ['Weekend', 'Returning_Visitor_Flag']
# ProductRelated_Duration listeden kaldırıldı.
num_cols = ['Administrative', 'Administrative_Duration', 'Informational', 'Informational_Duration', 
            'ProductRelated', 'ExitRates', 'PageValues', 'SpecialDay', 
            'Total_Duration', 'Engagement_Score', 'Bounce_Exit_Ratio']

X[cat_nominal] = X[cat_nominal].astype(str)

print("6. Preprocessing Pipeline Kurulumu (Phase 4)...")
# Month dönüştürücü
month_map = {'Feb':2, 'Mar':3, 'May':5, 'June':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
def encode_month(X_in):
    X_copy = X_in.copy()
    for c in X_copy.columns:
        X_copy[c] = X_copy[c].map(month_map).fillna(0)
    return X_copy

month_transformer = Pipeline(steps=[
    ('map', FunctionTransformer(encode_month)),
    ('scaler', RobustScaler())
])

nominal_transformer = Pipeline(steps=[
    ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
])

num_transformer = Pipeline(steps=[
    ('scaler', RobustScaler())
])

preprocessor = ColumnTransformer(
    transformers=[
        ('num', num_transformer, num_cols),
        ('month', month_transformer, cat_ordinal),
        ('cat', nominal_transformer, cat_nominal)
    ],
    remainder='passthrough'
)

# Leakage önlemek için işlem öncesinde veri bölünüyor.
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print("7. Pipeline Training Data'ya Fit Ediliyor...")
X_train_processed = preprocessor.fit_transform(X_train)
X_test_processed = preprocessor.transform(X_test)

# Sütun isimlerinin geri alınması (Feature Importance analizi için gerekli)
cat_features = preprocessor.named_transformers_['cat']['onehot'].get_feature_names_out(cat_nominal)
all_features = num_cols + cat_ordinal + list(cat_features) + passthrough_cols

X_train_df = pd.DataFrame(X_train_processed, columns=all_features)
X_test_df = pd.DataFrame(X_test_processed, columns=all_features)

print("8. Veriler kaydediliyor...")
X_train_df.to_csv('../data/model_ready/X_train.csv', index=False)
X_test_df.to_csv('../data/model_ready/X_test.csv', index=False)
y_train.to_csv('../data/model_ready/y_train.csv', index=False)
y_test.to_csv('../data/model_ready/y_test.csv', index=False)

joblib.dump(preprocessor, '../models/preprocessing_pipeline.pkl')
print("Model Ready Data ve Preprocessing Pipeline başarıyla güncellendi!")
