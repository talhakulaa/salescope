# FINAL REPORT: Model Optimization & Deployment Readiness

## 1. Problem Definition
Projenin amacı, "Online Shoppers Intention" veri setindeki *Revenue* (Satın Alma) hedefini tahmin etmektir. Mevcut model, Gradient Boosting Classifier kullanarak eğitilmiş, ancak yüksek False Negative (FN = 159) oranı ve düşük Recall (TP / (TP+FN)) problemine sahipti. Düşük Recall, satın alma niyetinde olan müşterilerin sistem tarafından tespit edilememesi ve dolayısıyla potansiyel gelirin kaçırılması anlamına gelmektedir (Opportunity Cost). Bu roadmap ile **Recall değerinin maksimize edilmesi** hedeflenmiş ve model deployment aşamasına hazır hale getirilmiştir.

## 2. Class Imbalance Analysis & Handling
Veri seti yaklaşık **5.5:1** oranında bir dengesizliğe sahipti (~ %84.5 sınıfa 0, ~ %15.5 sınıfa 1). Bu dengesizlik modelin ekseriyetle "False" (satın alma yok) sınıfına yönelmesine yol açıyordu. 
**SMOTE (Synthetic Minority Over-sampling Technique)** kullanılarak sadece eğitim verisi üzerinde azınlık sınıfı çoğaltılarak dengelendi. Sonucunda sınıfların modeli yönlendirme bias'ı kırıldı. Bu sayede modelin "True" sınıfına ait paterne olan duyarlılığı (Recall) arttı, False Negative sayısı radikal şekilde düştü.

## 3. Threshold Tuning
SMOTE tek başına yeterli esnekliği sağlayamadığından, modelin karar sınırı test edildi. `predict()` metodunun katı olan 0.50 eşiği yerine `predict_proba()` metodu ile 0.30 - 0.50 arasındaki eşikler denenip, Precision vs. Recall Trade-off analizi yapılmıştır. 
Optimum **Threshold 0.35** seviyesinde, Precision radikal şekilde kaybedilmeden Recall değeri en dengeli maksimizasyon seviyesine oturdu.

## 4. Hyperparameter Optimization & Model Comparison
GBC üzerinde GridSearchCV (n_estimators, learning_rate, vb.) uygulandı. Son model parametreleri (learning_rate=0.05, max_depth=3, n_estimators=200, subsample=0.8) olarak güncellenip overfit önlendi. (XGBoost veya LightGBM alternatif olarak denenebilir ancak GBC SMOTE ve eşik yapılandırması ile hedeflenen başarıya ulaştı). SMOTE ve eşik yapılandırması ile birlikte GBC projenin doğasına (tabular e-commerce log ları) en uygun model seçilmiştir.

## 5. Final Model Choice
Final model olarak **Tuned Gradient Boosting Classifier** seçildi. Gerekçe: 
- Hızlı inference süresi
- Stabil ROC-AUC ve Tree-based (Ağaç tabanlı) olması sayesinde log dönüşümlerine ihtiyaç bırakmayarak sağlamlık sağlaması.
- En yüksek test Recall değerine ulaşması.

## 6. Deployment Readiness
Ürünleştirme adımı için uçtan uca çalışabilecek bir Sklearn Pipeline oluşturulmuştur.
Kayıt Edilen Dosyalar:
* `optimized_production_model.pkl`: Model ve preprocessor pipeline
* `optimized_scaler.pkl`: StandardScaler & OneHotEncoder (alternatif API'ler için ayrı)
* `threshold_config.json`: Deployment script'i için optimal `0.35` threshold değeri.

Bu artifact'ler FastAPI veya Streamlit içerisinde doğrudan import edilerek inference (canlıda tahmin) vermeye hazırdır.

## 7. Business Impact Analysis
 Yapılan bu yenileme ve optimizasyon süreci sonrası False Negative değerleri minimize edilmiş, satın alma ihtimali bulunan müşteriyi yakalama performansı yükselmiştir. Bu sayede doğru kitleye hedeflenen reklamlar (re-targeting) gösterilerek e-ticaret sitesinin net dönüşüm (conversion) ve geliri doğrudan artırılabilecek konuma getirilmiştir.
