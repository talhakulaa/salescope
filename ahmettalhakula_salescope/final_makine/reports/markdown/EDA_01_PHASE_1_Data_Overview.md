# PHASE 1: Data Overview

**Yapılan Analiz:**  
Veri setinin temel boyutları, değişken türleri, eksik veri durumu ve sınıf (hedef) değişken dağılımı incelendi.

**🧠 Koddan Elde Edilen Bulgular:**  
- Veri seti 12,330 satır ve 18 değişkenden oluşmaktadır.
- Eksik veri bulunmamaktadır.
- Hedef değişken (`Revenue`) boolean tiptedir ve dağılımı şöyledir: Satın alma yapmayanlar (`False`) %84.53, Satın alma yapanlar (`True`) %15.47 oranındadır.

**💡 Analitik Yorum:**  
Veri setinde belirgin bir sınıf dengesizliği (class imbalance) tespit edilmiştir. Modellerin sınıf çoğunluğunu tahmin etme eğilimini engellemek adına Data Prep aşamasında sınıf dengeleme yöntemlerine başvurulması kritik olacaktır. Kategorik ve sayısal değişkenlerin birbirinden doğru ayrıştırılmış olması olumludur.

**⚠️ Risk / Dikkat Edilmesi Gereken Nokta:**  
Revenue hedef değişkenindeki %84.5'e %15.5'lik yüksek dengesizlik.

**🔁 Agent Etkileşim Notu:**  
Data Prep Expert için Öneri: SMOTE, class weighting veya stratified sampling seçeneklerini değerlendirmelidir.

