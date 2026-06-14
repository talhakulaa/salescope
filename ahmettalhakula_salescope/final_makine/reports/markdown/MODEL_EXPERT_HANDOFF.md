# DEPLOYMENT EXPERT HANDOFF

## Final Model:
Gradient Boosting Classifier

## Problem Türü:
Binary Classification

## Target:
Revenue (0: Satın Almayan, 1: Satın Alan)

## İş Problemi ve Pipeline Güncellemesi:
DataPrep aşamasında "ProductRelated" ile yüksek oranda korele olan (r=0.86) `ProductRelated_Duration` özelliği "redundancy" yaratmaması adına `Total_Duration` özelliği türetildikten sonra makine öğrenmesi testlerinden **düşürülmüş/silinmiştir**. 

## Output:
Kullanıcının o session içerisinde satın alma işlemi gerçekleştirip gerçekleştirmeyeceğinin tahmini (TRUE / FALSE).

## Model Seçim Kriterleri ve Başarı (Yeni Pipeline):
Overfit yaratabilecek süre değişkeninin silinmesinin ardından 12 farklı model tekrar değerlendirildiğinde:

* **Gradient Boosting (GB):** Weighted F1 score (uyum) bakımından yine yaklaşık %89.5, ROC-AUC alanında %92.6 başarı vererek liderliği korumuştur. 
* Random Forest gibi mimarilerin Overfit-Gap'i ~%0.10 iken, Gradient Boosting %0.02'lik overfit-gap (genellenebilirlik marjı) tablosunda yerini çok daha sağlamlaştırmış ve gereksiz "noise"lardan (Duration redundancy) kurtulmuştur.
* Sınıf dengesizliğine (Imbalance) çok fazla kapılmayıp True (Satın Alan) sınıfta anlamlı bir ayrım gücü test edildi. Ancak yine de Baseline bir yöntem olduğu için False Negatifler (Ziyaretçiyi satın almayacak sanmak) Recall noktasında mevcuttur. (Yeni model ~222 siparişi doğru tahmin ederken ~160 tanesini kaçırmıştır.)

## Riskler & Öneriler:
1. **False Negative (Müşteri Kaçırma) Riski:** Model Recall tarafında (1 sınıfı için %58 yakalama payı) eksikliğini sürdürmektedir. Eğer agresif bir indirim kuponu kampanyası hedefliyorsanız, Threshold tuning (Eşik kaydırma) operasyonları can kurtarabilir.
2. **PageValues Leakage Uyarısı:** Model büyük oranda PageValues (Sayfa Değeri) metriğine odaklanmayı sürdürmektedir. Production aşamasında Session bittikten sonra değil de sessionın ortalarında canlı tahmin yapmak arzu ediliyorsa `PageValues` metriğinin "Satın alma gerçekleşmeden anlık üretilip üretilemediği" doğrulanmalıdır.

## Dosya Bilgileri:
- Eğitim Boru Hattı: `models/preprocessing_pipeline.pkl`
- Seçilen Final Model: `models/final_model.pkl`
- Grafik/Değerlendirme: `figures/model_phase10_final_confusion_matrix.html` (ve değerleri)
