import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import GradientBoostingClassifier
import joblib
import os
import plotly.io as pio

def main():
    os.chdir("/Users/sudenazcobanoglu/Desktop/final_makina/final_makine")
    os.makedirs("figures", exist_ok=True)
    
    # Let's say we just do it for dummy / or read the data properly:
    try:
        X_train = pd.read_csv("data/model_ready/X_train.csv")
        X_test = pd.read_csv("data/model_ready/X_test.csv")
        y_train = pd.read_csv("data/model_ready/y_train.csv").values.ravel()
        y_test = pd.read_csv("data/model_ready/y_test.csv").values.ravel()
        
        # We need a quick GBC representation if it is not saved.
        # So we'll train one fast just for these plots
        base_gbc = GradientBoostingClassifier(random_state=42)
        base_gbc.fit(X_train, y_train)
        y_pred_base = base_gbc.predict(X_test)
        y_prob_base = base_gbc.predict_proba(X_test)[:, 1]
        
        from imblearn.over_sampling import SMOTE
        from imblearn.pipeline import Pipeline
        final_model = Pipeline([
            ('smote', SMOTE(random_state=42)),
            ('gbc', GradientBoostingClassifier(
                learning_rate=0.05, max_depth=3, n_estimators=200, subsample=0.8, random_state=42))
        ])
        final_model.fit(X_train, y_train)
        y_prob_opt = final_model.predict_proba(X_test)[:, 1]
        t = 0.35
        y_pred_opt = (y_prob_opt >= t).astype(int)
        
        from sklearn.metrics import confusion_matrix
        cm_base = confusion_matrix(y_test, y_pred_base)
        cm_opt = confusion_matrix(y_test, y_pred_opt)
        
        # 1. Base CM
        fig, ax = plt.subplots(figsize=(6, 5))
        sns.heatmap(cm_base, annot=True, fmt='d', cmap='Blues', cbar=False, ax=ax)
        ax.set_title("Baseline Confusion Matrix")
        fig.tight_layout()
        fig.savefig("figures/cm_baseline.png")
        plt.close()
        
        fig = px.imshow(cm_base, text_auto=True, color_continuous_scale='Blues',
                        title='Baseline Confusion Matrix')
        fig.write_html("figures/cm_baseline.html")
        
        # 2. Opt CM
        fig, ax = plt.subplots(figsize=(6, 5))
        sns.heatmap(cm_opt, annot=True, fmt='d', cmap='Greens', cbar=False, ax=ax)
        ax.set_title(f"Optimized Confusion Matrix (Threshold={t})")
        fig.tight_layout()
        fig.savefig("figures/cm_optimized.png")
        plt.close()
        
        fig = px.imshow(cm_opt, text_auto=True, color_continuous_scale='Greens',
                        title=f'Optimized Confusion Matrix (Threshold={t})')
        fig.write_html("figures/cm_optimized.html")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
