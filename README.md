# Online Alışveriş Niyeti Tahmini

Sınıflandırma modelleri ve gelişmiş veri analiz teknikleri kullanarak çevrimiçi alışverişçilerin satın alma niyetini tahmin etmek için bir makine öğrenmesi projesi.

## 📋 Proje Özeti

Bu proje çevrimiçi alışveriş davranışını analiz eder ve satın alma yapması olası müşterileri tanımlamak için tahminsel modeller oluşturur. Kapsamlı keşifsel veri analizi (EDA), veri ön işleme, model eğitimi, optimizasyon ve etkileşimli görselleştirmeler içerir.

**Veri Seti**: Online Alışveriş Niyeti Veri Seti  
**Hedef**: Revenue (ikili sınıflandırma - satın alma/satın almama)

## 📁 Proje Yapısı

```
final_makine/
├── README.md                          # Proje belgelendirmesi
├── app.py                             # Ana uygulama
├── project_presentation.ipynb         # Etkileşimli sunum defteri
├── online_shoppers_intention.csv      # Ham veri seti
│
├── agents/                            # Her aşama için uzman aracı kılavuzları
│   ├── dataprep-expert-agent.md       # Veri hazırlama yönergeleri
│   ├── eda-expert-agent.md            # EDA yönergeleri
│   ├── model-expert-agent.md          # Model eğitimi yönergeleri
│   ├── deployment-expert-agent.md     # Dağıtım yönergeleri
│   └── sunum-dosyası-hazırlama-agent.md
│
├── data/                              # Veri dizini
│   ├── raw/                           # Orijinal veri seti
│   ├── processed/                     # Temizlenmiş ve ön işlenmiş veriler
│   └── model_ready/                   # Eğitim/test bölünmesi (X_train, X_test, y_train, y_test)
│
├── scripts/                           # Pipeline için Python betikleri
│   ├── phase1_data_overview.py        # Veri yükleme ve özeti
│   ├── phase2_univariate.py           # Tek değişken analizi
│   ├── phase3_bivariate.py            # İki değişken ilişkileri
│   ├── phase4_multivariate.py         # Çok değişken analizi
│   ├── dataprep_pipeline.py           # Veri ön işleme
│   ├── model_training.py              # Model eğitimi ve değerlendirme
│   ├── run_optimization.py            # Model optimizasyonu
│   └── [diğer yardımcı betikler]
│
├── figures/                           # Oluşturulan görselleştirmeler (HTML)
│   ├── phase2_*.html                  # Tek değişken analizi grafikleri
│   ├── phase3_*.html                  # İki değişken analizi grafikleri
│   ├── phase4_correlation_matrix.html # Korelasyon ısı haritası
│   ├── single_roc_curve.html          # ROC eğrisi
│   ├── single_pr_curve.html           # Kesinlik-Duyarlılık eğrisi
│   └── [diğer metrikler/grafikler]
│
├── models/                            # Eğitilmiş modeller ve sonuçlar
│   ├── all_model_results.csv          # Model karşılaştırma sonuçları
│   └── threshold_config.json          # Optimal eşik yapılandırması
│
└── reports/                           # Dışa aktarılan raporlar
    ├── csv/                           # Tablo raporları
    └── markdown/                      # Markdown formatında raporlar
```

## 🚀 Başlarken

### Ön Koşullar

- Python 3.8+
- Sanal ortam (venv veya conda)

### Kurulum

1. **Proje dizinine gidin:**
   ```bash
   cd final_makine
   ```

2. **Sanal ortam oluşturun ve etkinleştirin:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows'ta: .venv\Scripts\activate
   ```

3. **Bağımlılıkları yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

## 📊 Proje Aşamaları

### Aşama 1: Veri Özeti
- Ham veri setini yükleyin ve keşfedin
- Temel istatistikleri ve veri türlerini görüntüleyin
- Eksik değerleri kontrol edin
- **Betik**: `scripts/phase1_data_overview.py`

### Aşama 2: Tek Değişken Analizi
- Bireysel özellikleri analiz edin
- Histogramlar ve çubuk grafikler oluşturun
- Dağılımları gelire göre inceleyin
- **Betik**: `scripts/phase2_univariate.py`

### Aşama 3: İki Değişken Analizi
- Değişken çiftleri arasındaki ilişkileri analiz edin
- Kutu grafikleri ve dağılım grafikleri oluşturun
- Hedef değişkene göre özellik önemini inceleyin
- **Betik**: `scripts/phase3_bivariate.py`

### Aşama 4: Çok Değişken Analizi
- Birden fazla özellik arasındaki karmaşık ilişkileri inceleyin
- Korelasyon matrisleri oluşturun
- Gelişmiş görselleştirmeler oluşturun
- **Betik**: `scripts/phase4_multivariate.py`

### Veri Ön İşleme
- Eksik değerleri işleyin
- Aykırı değerleri kaldırın
- Özellik ölçeklemesi ve normalleştirmesi
- Kategorik değişkenleri kodlayın
- **Betik**: `scripts/dataprep_pipeline.py`

### Model Eğitimi ve Değerlendirme
- Birden fazla sınıflandırma modeli eğitin
- Performans metriklerini değerlendirin (doğruluk, kesinlik, duyarlılık, F1, ROC-AUC)
- ROC ve Kesinlik-Duyarlılık eğrileri oluşturun
- Karışıklık matrisleri oluşturun
- **Betik**: `scripts/model_training.py`

### Model Optimizasyonu
- Model hiperparametrelerini ince ayarla
- Kesinlik/duyarlılık ödünleşmesi için karar eşiklerini optimize et
- Optimizasyon raporları oluştur
- **Betik**: `scripts/run_optimization.py`

## 🔧 Kullanım

### Tam pipeline'ı çalıştırın:
```bash
python scripts/dataprep_pipeline.py
python scripts/model_training.py
python scripts/run_optimization.py
```

### Etkileşimli sunumu görüntüleyin:
```bash
jupyter notebook project_presentation.ipynb
```

### Ana uygulamayı çalıştırın:
```bash
python app.py
```

### Görselleştirmeler oluşturun:
```bash
python scripts/export_separated_figures.py
```

## 📈 Ana Sonuçlar

- **Eğitilen Modeller**: Birden fazla sınıflandırma modeli (Lojistik Regresyon, Rastgele Orman, Gradient Boosting, vb.)
- **En İyi Performans**: Ayrıntılı sonuçlar `models/all_model_results.csv` dosyasında saklanır
- **Görselleştirmeler**: `figures/` dizininde 20+ etkileşimli HTML grafiği
- **Optimal Eşik**: `models/threshold_config.json` dosyasında yapılandırılmış

## 📊 Veri Açıklaması

**Veri Seti**: Online Alışveriş Niyeti Veri Seti  
**Örnekler**: ~12,330 oturum  
**Özellikler**: 17 sayısal ve kategorik özellik
- Oturum Süresi, Sayfa Değerleri, Geri Dönüş Oranları, Çıkış Oranları
- Ürünle ilgili bilgiler
- Ziyaretçi türü, ay, hafta sonu göstergesi, trafik kaynağı
- Özel gün göstergesi, tarayıcı, işletim sistemi, bölge

**Hedef Değişken**: 
- `Revenue`: İkili (Evet=1 / Hayır=0) - oturumun satın alma ile sonuçlanıp sonuçlanmadığı

## 📁 Veri Bölünmesi

```
data/model_ready/
├── X_train.csv        # Eğitim özellikleri
├── X_test.csv         # Test özellikleri
├── y_train.csv        # Eğitim etiketleri
└── y_test.csv         # Test etiketleri
```

## 📑 Raporlar ve Analiz

- Ayrıntılı analiz raporları `reports/markdown/` dizininde
- Ara sonuçların CSV dışa aktarımları `reports/csv/` dizininde
- Tahmin sonuçları `analysis_history/predictions.csv` dosyasında

## 🤝 Uzman Aracılar

Bu proje farklı aşamalar için uzmanlaşmış aracı kılavuzlarını içerir:
- **Veri Hazırlama Uzmanı**: Veri temizleme ve ön işleme yönergeleri
- **EDA Uzmanı**: Keşifsel veri analizi en iyi uygulamaları
- **Model Uzmanı**: Model seçimi ve eğitim stratejileri
- **Dağıtım Uzmanı**: Üretim dağıtım yönergeleri

Ayrıntılı kılavuz için `agents/` dizinindeki dosyalara başvurun.

## 📝 Defterler

- **project_presentation.ipynb**: Tüm analizler ve sonuçlarla etkileşimli sunum
- **scripts/recall_optimization.ipynb**: Ayrıntılı duyarlılık optimizasyonu analizi
- **scripts/final_evaluation_dashboard.ipynb**: Kapsamlı değerlendirme gösterge paneli

## 🔍 Analiz Geçmişi

Önceki tahminler ve analizler `analysis_history/predictions.csv` dosyasında saklanır

## 📦 Çıktı Dosyaları

### Görselleştirmeler (HTML)
- Dağılım grafikleri
- Korelasyon matrisleri
- ROC eğrileri
- Kesinlik-Duyarlılık eğrileri
- Karışıklık matrisleri
- Performans metrikleri özeti

### Modeller
- Değerlendirme metriklerine sahip tüm eğitilmiş modeller
- Karar verme için optimal eşik yapılandırması

### Raporlar
- Ayrıntılı markdown raporları
- Analiz sonuçlarının CSV dışa aktarımları

## 🛠️ Yardımcı Araçlar

Çeşitli yardımcı betikler mevcuttur:
- `fix_notebook_markdown.py`: Notebook markdown biçimlendirmesi
- `convert_prints_to_markdown.py`: Print ifadelerini markdown'a dönüştür
- `save_processed_data.py`: İşlenmiş veri setlerini kaydet
- `add_learning_curve.py`: Analize öğrenme eğrileri ekle
- Ve daha fazlası...

## 📋 Gereksinimler

Ana bağımlılıklar (`requirements.txt` dosyasında tam liste):
- pandas
- numpy
- scikit-learn
- matplotlib
- seaborn
- plotly
- jupyter

## 📄 Lisans

Bu proje eğitim ve araştırma amaçları içindir.

## ✅ Sonraki Adımlar

1. Proje yapısını ve verileri inceyin
2. Veri hazırlama pipeline'ını çalıştırın
3. Etkileşimli sunum defterini keşfedin
4. Odak alanınız için uzman aracı kılavuzlarını gözden geçirin
5. Model eğitimi ve optimizasyonunu çalıştırın
6. Dağıtım uzmanından gelen yönergeleri kullanarak dağıtın

---

**Son Güncelleme**: Haziran 2026  
**Proje Durumu**: Aktif Geliştirme

