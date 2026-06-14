import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import confusion_matrix, roc_curve, auc, precision_recall_curve, accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
import os

sns.set_theme(style="darkgrid")

def main():
    os.chdir("/Users/sudenazcobanoglu/Desktop/final_makina/final_makine")
    os.makedirs("figures", exist_ok=True)
    
    # Load Data like the notebook
    df = pd.read_csv('data/raw/online_shoppers_intention.csv')
    X = df.drop(columns=['Revenue'])
    y = df['Revenue'].astype(int)
    
    cat_cols = X.select_dtypes(include=['object', 'bool']).columns.tolist()
    num_cols = X.select_dtypes(exclude=['object', 'bool']).columns.tolist()
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    preprocessor = ColumnTransformer(transformers=[
        ('num', StandardScaler(), num_cols),
        ('cat', OneHotEncoder(handle_unknown='ignore', drop='first'), cat_cols)
    ])
    
    X_train_processed = preprocessor.fit_transform(X_train)
    X_test_processed = preprocessor.transform(X_test)
    
    # Base Model Prediction
    base_gbc = GradientBoostingClassifier(random_state=42)
    base_gbc.fit(X_train_processed, y_train)
    y_pred_base = base_gbc.predict(X_test_processed)
    y_prob_base = base_gbc.predict_proba(X_test_processed)[:, 1]
    
    # Final Model Prediction
    final_model = ImbPipeline([
        ('smote', SMOTE(random_state=42)),
        ('gbc', GradientBoostingClassifier(
            learning_rate=0.05, max_depth=3, n_estimators=200, subsample=0.8, random_state=42))
    ])
    final_model.fit(X_train_processed, y_train)
    y_prob_opt = final_model.predict_proba(X_test_processed)[:, 1]
    y_pred_opt = (y_prob_opt >= 0.35).astype(int)
    
    # --- 1. BASELINE CM ---
    cm_base = confusion_matrix(y_test, y_pred_base)
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(cm_base, annot=True, fmt='d', cmap='Blues', cbar=False, ax=ax)
    ax.set_title("Baseline GBC Confusion Matrix")
    ax.set_ylabel("True Label")
    ax.set_xlabel("Predicted Label")
    fig.tight_layout()
    fig.savefig("figures/single_cm_baseline.png")
    plt.close()
    
    fig = px.imshow(cm_base, text_auto=True, color_continuous_scale='Blues',
                    title='Baseline GBC Confusion Matrix', labels=dict(x="Predicted Label", y="True Label"))
    fig.write_html("figures/single_cm_baseline.html")

    # --- 2. OPTIMIZED CM ---
    cm_opt = confusion_matrix(y_test, y_pred_opt)
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(cm_opt, annot=True, fmt='d', cmap='Greens', cbar=False, ax=ax)
    ax.set_title("Optimized Model Confusion Matrix")
    ax.set_ylabel("True Label")
    ax.set_xlabel("Predicted Label")
    fig.tight_layout()
    fig.savefig("figures/single_cm_optimized.png")
    plt.close()
    
    fig = px.imshow(cm_opt, text_auto=True, color_continuous_scale='Greens',
                    title='Optimized Model Confusion Matrix', labels=dict(x="Predicted Label", y="True Label"))
    fig.write_html("figures/single_cm_optimized.html")

    # --- 3. ROC CURVE ---
    fpr_b, tpr_b, _ = roc_curve(y_test, y_prob_base)
    auc_b = auc(fpr_b, tpr_b)
    fpr_o, tpr_o, _ = roc_curve(y_test, y_prob_opt)
    auc_o = auc(fpr_o, tpr_o)
    
    fig = plt.figure(figsize=(6, 5))
    plt.plot(fpr_b, tpr_b, linestyle='--', label=f'Base AUC={auc_b:.2f}')
    plt.plot(fpr_o, tpr_o, label=f'Final AUC={auc_o:.2f}')
    plt.plot([0, 1], [0, 1], 'k:')
    plt.legend()
    plt.title("ROC Curve Comparison")
    plt.tight_layout()
    plt.savefig("figures/single_roc_curve.png")
    plt.close()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=fpr_b, y=tpr_b, mode='lines', name=f'Baseline AUC={auc_b:.2f}', line=dict(dash='dash')))
    fig.add_trace(go.Scatter(x=fpr_o, y=tpr_o, mode='lines', name=f'Final AUC={auc_o:.2f}'))
    fig.add_trace(go.Scatter(x=[0,1], y=[0,1], mode='lines', line=dict(dash='dot', color='black'), showlegend=False))
    fig.update_layout(title="ROC Curve Comparison")
    fig.write_html("figures/single_roc_curve.html")

    # --- 4. PR CURVE ---
    p_b, r_b, _ = precision_recall_curve(y_test, y_prob_base)
    p_o, r_o, _ = precision_recall_curve(y_test, y_prob_opt)
    
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(r_b, p_b, linestyle='--', label='Baseline')
    ax.plot(r_o, p_o, label='Final Model')
    ax.legend()
    ax.set_title("Precision-Recall Curve Comparison")
    fig.tight_layout()
    fig.savefig("figures/single_pr_curve.png")
    plt.close()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=r_b, y=p_b, mode='lines', name='Baseline PR', line=dict(dash='dash')))
    fig.add_trace(go.Scatter(x=r_o, y=p_o, mode='lines', name='Final PR'))
    fig.update_layout(title="Precision-Recall Curve Comparison")
    fig.write_html("figures/single_pr_curve.html")

    # --- 5. METRICS BAR CHART ---
    def get_metrics(y_t, y_p, p_p):
        return [accuracy_score(y_t, y_p), precision_score(y_t, y_p), 
                recall_score(y_t, y_p), f1_score(y_t, y_p), roc_auc_score(y_t, p_p)]
    met_b = get_metrics(y_test, y_pred_base, y_prob_base)
    met_o = get_metrics(y_test, y_pred_opt, y_prob_opt)
    df_metrics = pd.DataFrame({
        'Metric': ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'ROC-AUC'],
        'Baseline': met_b,
        'Final Optimized': met_o
    }).melt(id_vars='Metric', var_name='Model', value_name='Score')

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=df_metrics, x='Metric', y='Score', hue='Model', ax=ax, palette=['#abcdef', '#f4a582'])
    ax.set_title("Metrics Summary")
    ax.set_ylim(0, 1.0)
    fig.tight_layout()
    fig.savefig("figures/single_metrics_summary.png")
    plt.close()

    fig = px.bar(df_metrics, x='Metric', y='Score', color='Model', barmode='group', title="Metrics Summary")
    fig.write_html("figures/single_metrics_summary.html")

    # --- 6. DISTRIBUTIONS (TP vs FN) ---
    analysis_df = X_test.copy()
    analysis_df['y_true'] = y_test
    analysis_df['y_pred_final'] = y_pred_opt
    
    tp_mask = (analysis_df['y_true'] == 1) & (analysis_df['y_pred_final'] == 1)
    fn_mask = (analysis_df['y_true'] == 1) & (analysis_df['y_pred_final'] == 0)
    
    analysis_df['Outcome'] = 'Other'
    analysis_df.loc[tp_mask, 'Outcome'] = 'True Positive (Caught)'
    analysis_df.loc[fn_mask, 'Outcome'] = 'False Negative (Missed)'
    
    focus_df = analysis_df[analysis_df['Outcome'] != 'Other']

    for col in ['PageValues', 'ProductRelated_Duration', 'ExitRates']:
        fig, ax = plt.subplots(figsize=(6, 5))
        sns.boxplot(data=focus_df, x='Outcome', y=col, hue='Outcome', ax=ax, palette='Set2')
        ax.set_title(f"{col} Distribution (TP vs FN)")
        fig.tight_layout()
        fig.savefig(f"figures/single_dist_{col}.png")
        plt.close()

        fig = px.box(focus_df, x='Outcome', y=col, color='Outcome', title=f"{col} Distribution (TP vs FN)")
        fig.write_html(f"figures/single_dist_{col}.html")

    print("Success: Generated individual plot files in the 'figures' folder.")

if __name__ == '__main__':
    main()
