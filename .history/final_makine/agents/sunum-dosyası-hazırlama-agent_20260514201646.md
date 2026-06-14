# AGENT.md

## Notebook Yapısı

1. Hero Section
2. İşi Anlama
3. Veriyi Anlama
4. Veriyi Hazırlama
5. Modelleme
6. Sonuç ve Stratejik Değerlendirme

---

# Genel Kurallar

- Notebook boyunca aynı:
  - renk paleti
  - font yapısı
  - markdown tasarımı
  - grafik dili
  kullanılmalıdır.

- Tüm grafikler interaktif olmalıdır.
- Plotly kullanılmalıdır.
- Grafiklerde tutarlı renkler kullanılmalıdır.
- Koyu tema kullanılmalıdır.
- Her kod hücresinden sonra kısa markdown açıklaması yazılmalıdır.
- Markdown açıklamaları:
  - kısa
  - profesyonel
  - stratejik
  olmalıdır.
- Her yorum:
  - veri bilimi açısından
  - iş açısından
  - YBS açısından
  değerlendirme içermelidir.

---

# 1. Hero Section

Bu bölümde:

- proje adı
- dataset adı
- problem cümlesi
- takım üyeleri
- kullanılan teknolojiler
- classification etiketi

yer almalıdır.

Modern glassmorphism tasarım kullanılmalıdır.

---

# 2. İşi Anlama

Bu bölüm iş problemi odaklı ilerlemelidir.

Yer alması gerekenler:

- problem hikayesi
- sektör bilgisi
- iş hedefleri
- veri bilimi hedefleri
- başarı kriterleri
- riskler
- ekip üyeleri ve rolleri

Markdown yapısı yönetici sunumu gibi olmalıdır.

---

# 3. Veriyi Anlama

Bu aşama sırasında `@eda-expert` agent dosyasında gerçekleştirilen tüm işlemler gösterilmelidir.

Aşağıdaki analizlerin tamamı yapılmalıdır:

- ilk 5 satır
- son 5 satır
- dataset shape
- veri tipleri
- istatistiksel özet
- eksik değer analizi
- aykırı değer analizi
- hedef değişken analizi
- tekli değişken analizleri
- ikili değişken analizleri
- çoklu değişken analizleri

Zorunlu grafikler:

- histogram
- boxplot
- correlation heatmap
- scatter plot
- violin plot
- grouped chart
- class distribution chart

Tüm grafikler interaktif olmalıdır.

Her analiz sonrası kısa markdown yorumları yazılmalıdır.

---

# 4. Veriyi Hazırlama

Bu aşama sırasında `@data-prep-expert` agent dosyasında gerçekleştirilen tüm işlemler uygulanmalıdır.

Yapılan tüm preprocessing işlemleri:
- grafiklerle
- önce/sonra karşılaştırmalarıyla
- kısa markdown açıklamalarıyla
sunulmalıdır.

Yer alması gerekenler:

- eksik veri yönetimi
- aykırı değer yönetimi
- encoding
- feature scaling
- feature engineering
- train test split

Her adım stratejik olarak yorumlanmalıdır.

---

# 5. Modelleme

Bu aşama sırasında `@model-expert-agent` agent dosyasında gerçekleştirilen tüm işlemler uygulanmalıdır.

Modelleme sürecinde gerçekleştirilen:
- model kurulumları
- model karşılaştırmaları
- performans analizleri
- optimizasyon işlemleri
- değerlendirme metrikleri
- feature importance analizleri
- hata analizleri
- final model seçim süreçleri

tamamı grafiklerle ve markdown açıklamalarıyla sunulmalıdır.

Yer alması gerekenler:

- baseline model
- çoklu model karşılaştırması
- performans analizleri
- confusion matrix
- ROC Curve
- Precision Recall Curve
- feature importance
- hyperparameter optimization
- final model seçimi

Kullanılması gereken modeller:

- Logistic Regression
- Decision Tree
- Random Forest
- XGBoost
- LightGBM
- CatBoost
- KNN
- SVM
- Naive Bayes
- AdaBoost

Tüm sonuçlar:
- interaktif grafiklerle
- karşılaştırmalı tablolarla
sunulmalıdır.

Her model sonrası kısa markdown değerlendirmesi yapılmalıdır.

---

# 6. Sonuç ve Stratejik Değerlendirme

Bu bölüm yönetici özeti gibi hazırlanmalıdır.

Yer alması gerekenler:

- iş değeri
- operasyonel katkı
- model riskleri
- stratejik çıkarımlar
- geliştirme önerileri

---

# Grafik Kuralları

- Plotly kullanılmalıdır.
- Dark theme kullanılmalıdır.
- Aynı renk paleti korunmalıdır.
- Hover desteklenmelidir.
- Başlık yapıları tutarlı olmalıdır.

---

# Kod Kuralları

- Kod temiz olmalıdır.
- Modüler yapı kullanılmalıdır.
- Gereksiz kod tekrarından kaçınılmalıdır.
- Notebook profesyonel görünmelidir.

---

# YBS Yaklaşımı

Notebook yalnızca teknik olmamalıdır.

Her bölüm:
- karar desteği
- iş etkisi
- stratejik anlam
- yönetsel çıkarım

içermelidir.

Bu proje:
“Makine öğrenmesi modeli”
değil,

“Veri destekli karar sistemi”
olarak anlatılmalıdır.