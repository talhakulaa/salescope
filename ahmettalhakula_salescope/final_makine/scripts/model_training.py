import os
import time
import joblib
import warnings
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from prettytable import PrettyTable

from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression, RidgeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    RandomForestClassifier,
    ExtraTreesClassifier,
    GradientBoostingClassifier,
    AdaBoostClassifier,
    BaggingClassifier
)
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier

from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.metrics import (
    f1_score, recall_score, roc_auc_score, accuracy_score,
    classification_report, confusion_matrix, precision_recall_curve, roc_curve
)

warnings.filterwarnings('ignore')

os.makedirs('../figures', exist_ok=True)
os.makedirs('../models', exist_ok=True)
os.makedirs('../reports/markdown', exist_ok=True)

print("1. DataPrep Girdileri Yükleniyor...")
X_train = pd.read_csv('../data/model_ready/X_train.csv')
X_test = pd.read_csv('../data/model_ready/X_test.csv')
y_train = pd.read_csv('../data/model_ready/y_train.csv').values.ravel()
y_test = pd.read_csv('../data/model_ready/y_test.csv').values.ravel()

# 12 Model (Support Vector Machine SVM is excluded to optimize time, 12 other candidates included)
models = {
    "Dummy Classifier": DummyClassifier(strategy="most_frequent"),
    "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
    "Ridge Classifier": RidgeClassifier(random_state=42),
    "KNN": KNeighborsClassifier(),
    "Decision Tree": DecisionTreeClassifier(random_state=42),
    "Random Forest": RandomForestClassifier(random_state=42),
    "Extra Trees": ExtraTreesClassifier(random_state=42),
    "Gradient Boosting": GradientBoostingClassifier(random_state=42),
    "AdaBoost": AdaBoostClassifier(random_state=42),
    "Bagging": BaggingClassifier(random_state=42),
    "Naive Bayes": GaussianNB(),
    "MLP Neural Network": MLPClassifier(max_iter=200, random_state=42)
}

cv_strategy = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

pt = PrettyTable()
pt.field_names = ["Model", "Eğitim S.", "Train F1", "Test F1", "Recall(1)", "ROC-AUC", "CV Mean", "CV Std", "Overfit", "Durum"]

results_list = []
best_model_name = None
best_score = -1
best_model_obj = None

print("\n2. Model Eğitim ve Değerlendirme Döngüsü Başlatılıyor...")
for name, model in models.items():
    start_time = time.time()
    try:
        model.fit(X_train, y_train)
        train_time = time.time() - start_time
        
        train_pred = model.predict(X_train)
        test_pred = model.predict(X_test)
        
        if hasattr(model, "predict_proba"):
            test_prob = model.predict_proba(X_test)[:, 1]
        elif hasattr(model, "decision_function"):
            test_prob = model.decision_function(X_test)
        else:
            test_prob = test_pred 
            
        train_f1 = f1_score(y_train, train_pred, average="weighted")
        test_f1 = f1_score(y_test, test_pred, average="weighted")
        recall = recall_score(y_test, test_pred)
        roc_auc = roc_auc_score(y_test, test_prob)
        
        cv_res = cross_validate(model, X_train, y_train, cv=cv_strategy, scoring="f1_weighted", n_jobs=-1)
        cv_mean = cv_res['test_score'].mean()
        cv_std = cv_res['test_score'].std()
        overfit_gap = train_f1 - test_f1
        
        pt.add_row([
            name, f"{train_time:.2f}s", f"{train_f1:.4f}", f"{test_f1:.4f}", 
            f"{recall:.4f}", f"{roc_auc:.4f}", f"{cv_mean:.4f}", f"{cv_std:.4f}", f"{overfit_gap:.4f}", "Başarılı"
        ])
        
        # Karar Puanı (Recall + Test F1 + ROC-AUC dengesi)
        score = (recall * 0.4) + (test_f1 * 0.3) + (roc_auc * 0.3) - (overfit_gap * 0.2)
        if score > best_score and name != "Dummy Classifier":
            best_score = score
            best_model_name = name
            best_model_obj = model
            
        results_list.append({
            "Model": name, "Train F1": train_f1, "Test F1": test_f1, "Recall": recall, "ROC_AUC": roc_auc, "CV_Mean": cv_mean
        })
    except Exception as e:
        pt.add_row([name, "-", "-", "-", "-", "-", "-", "-", "-", "Hata!"])

print(pt)
res_df = pd.DataFrame(results_list)
res_df.to_csv('../models/all_model_results.csv', index=False)

print(f"\n3. Final Model Seçimi: {best_model_name}")
joblib.dump(best_model_obj, '../models/final_model.pkl')

best_test_pred = best_model_obj.predict(X_test)
cm = confusion_matrix(y_test, best_test_pred)
print("Classification Report:\n", classification_report(y_test, best_test_pred))

# Plotly ile grafikler
fig = px.bar(res_df.sort_values('Test F1', ascending=False), x='Model', y=['Test F1', 'Recall'], barmode='group', title=f"Model Karşılaştırması ({best_model_name} Lidyeliğinde)")
fig.write_html('../figures/model_phase8_model_comparison.html')

cm_fig = px.imshow(cm, text_auto=True, color_continuous_scale='Blues', title=f"Confusion Matrix - {best_model_name}")
cm_fig.write_html('../figures/model_phase10_final_confusion_matrix.html')

print("Modelleme Süreci Tamamlandı! Raporlar Hazırlanıyor...")
