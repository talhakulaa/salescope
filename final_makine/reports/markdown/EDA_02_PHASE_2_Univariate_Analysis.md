# PHASE 2: Univariate Analysis

**Yapılan Analiz:**  
Sayısal ve kategorik değişkenlerin tekil dağılımları (Histogram ve Bar chartlar) çıkarılarak outlier ve çarpıklık (skewness) durumları incelenmiştir.

**🧠 Koddan Elde Edilen Bulgular:**  
- Sayısal değişkenlerin (özellikle `ProductRelated_Duration` ve `PageValues`) ciddi sağa çarpık (right-skewed) olduğu gözlemlendi. Çarpıklık değerleri: ProductRelated_Duration (7.26), PageValues (6.38).
- `PageValues` değişkeninde %22.14, `BounceRates` değişkeninde %12.58 outlier oranı ölçüldü. Bu, e-ticaret sitelerinde az sayıda insanın çok yüksek satın alma/faaliyet gerçekleştirmesi (veya hiç gerçekleştirmemesi) karakteristiğiyle uyumludur.
- Ziyaretlerin büyük çoğunluğu `Mayıs` (%27.3) ve `Kasım` (%24.3) aylarında gerçekleşmiştir (Kasım ayı Black Friday vb. kampanyaları işaret edebilir).
- Ziyaretçilerin %85.6'sı `Returning_Visitor` (dönen müşteri) kategorisindedir.
- Hafta içi ziyaretleri %76.7 ile ağırlıktadır.

**💡 Analitik Yorum:**  
Sayısal verilerin büyük kısmında "long-tail" (uzun kuyruk) dağılım mevcut. Extreme değerli session’lar var. E-ticarette bu tarz "aykırı" duran değerler (özellikle yüksek sayfa görüntüleme süreleri veya değerleri) çoğunlukla "satın alan" segmenti temsil eder. Outlier'ları modelden çıkarmak yerine log dönüşümüyle düzeltmek daha mantıklıdır. `Returning_Visitor` oranının çok yüksek olması sitenin kemik bir kitleye hitap ettiğini gösterse de yeni ziyaretçilerin davranışlarını da iyi okumak gerekir.

**⚠️ Risk / Dikkat Edilmesi Gereken Nokta:**  
Sayısal değişkenlerde (özellikle süre bazlı olanlarda) extrem değerler ve ciddi çarpıklık var. Linear modeller bu durumdan çok kötü etkilenebilir.

**🔁 Agent Etkileşim Notu:**  
Data Prep Expert için Öneri: Sayısal değişkenlerdeki ekstrem çarpıklık nedeniyle Robust Scaler, log transform veya power transform (Yeo-Johnson) teknikleri mutlaka uygulanmalıdır. Tree-based algoritmalar kullanılacaksa outlier müdahalesine gerek kalmayabilir.

**📁 Kaydedilen Görseller:**  
- figures/phase2_histogram_ProductRelated.html (vb. numerik değişken grafikleri)
- figures/phase2_bar_Month.html (vb. kategorik değişken grafikleri)

