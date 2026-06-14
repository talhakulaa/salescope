# PHASE 3: Bivariate Analysis (İkiye Değişkenli Analiz)

**Yapılan Analiz:**  
Bağımsız değişkenlerin (sayısal ve kategorik) hedef değişken olan `Revenue` (Satın Alma Niyeti) ile olan ilişkisi Boxplot ve Grouped Bar Chart'lar yardımıyla analiz edildi. Ortalamalar karşılaştırıldı.

**🧠 Koddan Elde Edilen Bulgular:**  
- `PageValues` değişkeni satın almayı ayırt etmekte son derece güçlü görünüyor; satın almayanların PageValue ortalaması 1.98 iken, satın alanların ortalaması 27.26!
- Satın alanlar (Revenue=True) sitede ortalama 1876 saniye geçirip 48 ürün incelerken; satın almayanlar (Revenue=False) 1070 saniye geçirip yaklaşık 29 ürün inceliyor.
- `BounceRates` düşük olan kullanıcılar satın almaya çok daha yatkın (%0.5 oranına karşı %2.5).
- Kategorik açılım: `New_Visitor` segmentinin conversion (dönüşüm) oranı %24.9 ile `Returning_Visitor` segmentinden (%13.9) çok daha yüksek.
- Aylara göre en yüksek satın alma oranları Kasım (25.35%) ve Ekim (20.95%) aylarında görülmektedir. Şubat ayı dönüşümleri ise yok denecek kadar az (%1.6).

**💡 Analitik Yorum:**  
PageValues değişkeni modelin en belirleyici (en yüksek feature importance) özelliği olmaya adaydır. Ancak bu durum, bu değişkenin "sepete ekleme" gibi işlemleri işaret etmesinden kaynaklı bir veri sızıntısı (leakage) potansiyeli taşıyabilir. Yeni ziyaretçilerin mevcut ziyaretçilerden daha fazla dönüşmesi, pazarlama metriklerinin (örneğin yeniden hedefleme vs. yeni müşteri kazanımı) değerlendirilmesi açısından işletmeye çok kıymetli bir içgörü sunar. Kasım ayı beklendiği gibi alışveriş festivali (Black Friday) etkisidir.

**⚠️ Risk / Dikkat Edilmesi Gereken Nokta:**  
`PageValues` çok güçlü bir ayırıcı. Data leakage yaratmaması için bu sayfa değerinin "ödeme onay sayfası" (checkout success vs.) gösterip göstermediği iyi araştırılmalı.

**🔁 Agent Etkileşim Notu:**  
Data Prep Expert için Öneri: `PageValues` ile hedef değişken arasında mükemmele yakın bir ayrışma var, leakage kontrolü için audit yapılması, veya model oluşturulurken PageValues ile ve olmadan iki farklı senaryo kurulması değerlendirilmeli.

**📁 Kaydedilen Görseller:**  
- figures/phase3_boxplot_revenue_PageValues.html
- figures/phase3_bar_revenue_Month.html

