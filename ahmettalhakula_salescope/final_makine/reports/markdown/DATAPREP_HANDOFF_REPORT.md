# MODEL EXPERT HANDOFF REPORT

## Veri Durumu
Temiz ve Modellemeye Hazır (Model-Ready)

## Problem Türü
Binary Classification

## İş Problemi
E-ticaret kullanıcılarının satın alma davranışını tahmin etmek. Data Understanding aşamasından gelen "Aykırı değerler kullanıcı davranışıdır" içgörüsüyle hareket edilmiş olup, session analizleri teknik bir veri sızıntısından ziyade doğal süreç gibi kabul edilmiştir.

## Target
Revenue (0: Satın Almayan, 1: Satın Alan)

## Missing Value Strategy
Orijinal veride %0 eksik veri bulunduğundan, imputasyon aşaması atlanmıştır.

## Encoding Strategy
- `Month` → Numeric Ordinal Mapping kullanıldı ve RobustScaler ile ölçeklendirildi.
- `VisitorType`, `OperatingSystems`, `Browser`, `Region`, `TrafficType` → One-Hot Encoding (Düşük cardinality varsayıldığı için sparse matrix engellendi).
- `Weekend` → Binary Integer (Passthrough).

## Scaling Strategy
EDA Expert'in Extreme Outlier / sağa çarpıklık bulgularına istinaden hedef scaling metodu olarak `RobustScaler` tercih edildi. Böylelikle ekstrem duration verileri silinmeden medyan odağı etrafında değerlendirilmeye alındı.

## Multicollinearity Çözümü
- `ExitRates` ile r=0.91 oranında çok güçlü pozitif korelasyona sahip olan `BounceRates` değişkeni silindi. Redundancy (Gereksiz tekrar) engellendi.

## Imbalance Strategy & Data Leakage (Stratified Split)
Modelde sentetik veri karmaşasını engellemek adına SMOTE gibi class augmentation süreçleri *eğitim / test* aşamasının öncesinde YAPILMADI. Veri %80 - %20 train-test mantığında **Stratified Split** ile bölündü (Target distribution korundu).
SMOTE, Model Expert'in inisiyatifinde olup Pipeline/Cross-Validation adımında fold-bazlı uygulanmalıdır.

## Feature Engineering (Üretilen Yeni Değişkenler)
- `Total_Duration`: Toplam kullanıcı etkileşimini anlamlandırmak amacıyla hesaplandı.
- `Engagement_Score`: Conversion gücünü artırmak amacıyla PageValues * ProductRelated çarpımı eklendi.
- `Bounce_Exit_Ratio`: Terk davranışının harmonik incelemesi.
- `Returning_Visitor_Flag`: Sadık müşterilerin etkisini direk modele yansıtmak amacıyla ikili (Binary) kolon türetildi.

## Leakage Status
- `PageValues` hedef değişkenle yüksek korelasyon göstermekte. Güçlü bir conversion sinyali olmasına rağmen "Sipariş Onay Ekranı" etkisi (Target leakage) oluşturma riski taşır. Modeling aşamasında Feature Importance raporuyla dikkatlice incelenmeli, gerektiğinde `PageValues`'suz bir baseline model de kurulmalıdır.

## Önerilen Model Türleri
Aykırı değerler scale edilmiş olsa da verinin yapısı log/power transform gerektirmeden ağaç yapılı makine öğrenmesi modelleriyle uyumludur:
- XGBoost
- LightGBM
- Random Forest
- CatBoost

## Kritik Uyarılar
- Her türlü scaling işlemi Test Leakage engellenmesi maksadıyla "DataPrep Pipeline" mekanizmasına konarak `fit_transform` (sadece Train) ve `transform` (Test) yaklaşımıyla yürütülmüştür. Bu Pipeline `models/` altında persist edilmiştir. Yeni eklenecek Data'lar için bu pipeline direk kullanılmalıdır.
