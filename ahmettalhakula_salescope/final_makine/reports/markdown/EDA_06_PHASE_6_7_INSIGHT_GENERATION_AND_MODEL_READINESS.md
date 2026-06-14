# PHASE 6 & 7: INSIGHT GENERATION AND MODEL READINESS

**İş Değeri Açısından İçgörüler (Insights):**
1. **Dönüşüm Süresi Etkisi:** Satın alan müşteriler sitede çok daha fazla vakit harcıyor (1876 sn vs 1070 sn).
2. **PageValue Başarısı:** 'PageValue' değişkeni yüksekse, müşterinin satın alma ihtimali çok yüksektir. Bu metrik anlık bir gösterge olarak CRM tarafında trigger tetiklemek maksatlı (anında indirim kuponu) kullanılabilir.
3. **Yeni Müşteri Avı Değerli:** Sitenin kalabalık kitlesi sadık (returning) olsa da "Yeni (New_Visitor)" olanların satın alımla sonuçlanma oranı daha yüksektir. Yeni müşteri kazanım kampanyalarına ağırlık verilebilir.
4. **Hemen Çıkma Tehlikesi:** Sayfadan hemen çıkma ("Bounce") oranları ne kadar düşükse satış işlemi o kadar garanti altına alınıyor. Site hızı ve ilk sayfa arayüz tasarımı bu yüzden hayati.

**Model Hazırlık Kararı (Model Readiness): KISMEN HAZIR**
Veride eksik değer olmamasına rağmen, kategorik değerler string tipli ("Month", "VisitorType") - **Encoding gerekli**. Süre tabanlı özellikler farklı ölçekte (scaler şart). Sınıf dengesizliği (Imbalance) %85/%15 civarı yüksek olduğundan (Örneğin: SMOTE ile düzeltme) şarttır.
Veri sızıntısı analizi özellikle `PageValues` için titizlikle gözden geçirilerek, data preprocessing (Veri Hazırlama) uzmanına devredebileceğimiz seviyeye gelmiştir.

