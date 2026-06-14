# PHASE 4: Multivariate Analysis

**Yapılan Analiz:**  
Tüm sayısal değişkenler arasındaki korelasyon ilişkileri matris halinde incelendi (Pearson korelasyonu) ve multicollinearity (çoklu doğrusal bağlantı) kontrolleri yapıldı.

**🧠 Koddan Elde Edilen Bulgular:**  
- `ProductRelated` ve `ProductRelated_Duration` arasında r = 0.86 düzeyinde çok yüksek korelasyon var. (Ürüne bakmak ve sitede geçen süre mantıken iç içe)
- `ExitRates` ve `BounceRates` arasında r = 0.91 düzeyinde çok yüksek pozitif korelasyon saptandı. 
- Hedef değişken (`Revenue`) ile en yüksek korelasyona sahip değişken `PageValues` (r = +0.49).

**💡 Analitik Yorum:**  
Yüksek korelasyon gösteren çiftler (örn. BounceRates ve ExitRates), algoritmik temelde *multicollinearity* problemi yaratabilir. Özellikle Logistic Regression vb. bağımsız ilişkiler bekleyen modeller bu durumdan olumsuz etkilenir. Bu değişkenlerden birinin elenmesi (veya PCA gibi boyut indirgeme uygulanması) modelin kararlılığını artıracaktır. 

**⚠️ Risk / Dikkat Edilmesi Gereken Nokta:**  
ExitRates ve BounceRates arasındaki aşırı güçlü bağlantı, feature redundancy oluşturur.

**🔁 Agent Etkileşim Notu:**  
Data Prep Expert için Öneri: Çoklu doğrusal bağlantı olan değişkenlerden birini `ExitRates` veya `BounceRates` gibi drop edilmesi değerlendirilmelidir (veya Lasso gibi feature selection/regularization tekniklerine başvurulmalıdır).

**📁 Kaydedilen Görseller:**  
- figures/phase4_correlation_matrix.html

---

