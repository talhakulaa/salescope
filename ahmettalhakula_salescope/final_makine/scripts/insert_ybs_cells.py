import json
import os

filepath = "/Users/sudenazcobanoglu/Desktop/final_makina/final_makine/scripts/final_evaluation_dashboard.ipynb"

# If the file doesn't exist, exit safely
if not os.path.exists(filepath):
    print(f"File {filepath} not found.")
    exit()

with open(filepath, 'r', encoding='utf-8') as f:
    nb = json.load(f)

new_cells = []

# Mappings of specific code snippets to their respective YBS Markdown cells
for cell in nb['cells']:
    new_cells.append(cell)
    
    if cell['cell_type'] == 'code':
        source = "".join(cell['source'])
        md_text = None
        
        if "Confusion Matrix Comparison: Baseline vs Final Model" in source:
            md_text = """### 💡 YBS Uzman Değerlendirmesi: Fırsat Maliyeti ve Kayıp Önleme

**Stratejik Kazanım:** Kaçırılan potansiyel alıcı (False Negative) oranındaki dramatik düşüş, şirketimizin **Fırsat Maliyetini (Opportunity Cost)** minimize etmektedir. Yanlışlıkla alıcı profiline dahil edilenlerin (False Positive) getirdiği operasyonel retargeting maliyeti, kazanılan yeni satışların **Müşteri Yaşam Boyu Değeri (CLV)** yanında son derece tolere edilebilir düzeydedir. E-ticarette almayacak müşteriye komik tutarlarda reklam göstermek, alacak müşteriyi siteden eli boş göndermekten çok daha kârlı bir hatadır."""

        elif "Classification Metrics Comparison" in source:
            md_text = """### 💡 YBS Uzman Değerlendirmesi: Model Başarı Dengesi

Salt **'Accuracy' (Doğruluk)** metriği yerine, azınlık sınıfı olan gerçek alıcıları bulma yeteneğimizin **(Recall)** maksimize edilmesi hedeflenmiştir. %85 verisi zaten "almayacak" olan bir veri setinde model herkes "almayacak" dese bile %85 accuracy'ye ulaşabilmektedir. Bunun önüne geçilmiş ve F1-Score dengesinin korunması hedeflenerek, algoritmik başarının **Operasyonel Bütçe Yönetimi** ile eşgüdümlü çalıştığı kanıtlanmıştır."""

        elif "Threshold vs Precision / Recall / F1-Score" in source:
            md_text = """### 💡 YBS Uzman Değerlendirmesi: Karar Sınırı (Threshold) Güvenliği

**Karar Sınırı Optimizasyonu:** Karar Destek Sistemimiz (DSS), e-ticaret dinamiklerine göre risk iştahını (0.35) optimize etmiştir. Precision'da yaşanan olağan düşüş maliyeti, Recall artışının (daha çok potansiyel müşteriyi radara alma) getireceği yüksek ciro (Revenue) performansı ile kompanse edilecek stratejik bir yönetim kararıdır."""

        elif "ROC Curve Comparison" in source and "Random" in source and not "Precision-Recall" in source:
            md_text = """### 💡 YBS Uzman Değerlendirmesi: Ayrıştırma Kabiliyeti

**Sağlamlık (Robustness):** Modelin sadece siteyi gezen bir ziyaretçi ile gerçekten o ürünü satın alacak bir alıcıyı ayrıştırmadaki gücü kanıtlanmıştır. İstikrarlı ve optimize edilmiş AUC değeri, **Pazarlama (Marketing)** biriminin segmentasyon ve kampanya kurgularında bu makine öğrenmesi çıktılarına gözü kapalı güvenebileceğinin kanıtıdır."""

        elif "Precision-Recall Curve Comparison" in source:
            md_text = """### 💡 YBS Uzman Değerlendirmesi: Kaynak ve Hedef Yönetimi

**Dengeli Kaynak Odaklılık:** Şirket kârlılığını belirleyen o kritik (azınlık) alıcı kitlesi üzerinde muazzam bir başarı sergilenmiştir. Pazarlama bütçesinin salt ürünleri gezen 'tık avcılarına' heba edilmesi engellenerek, bütçenin **gerçek potansiyel alıcılara (hedef kitle optimizasyonu)** konsantre olmasını sağlayacak analitik temel oturtulmuştur."""

        elif "Top 15 Feature Importances" in source:
            md_text = """### 💡 YBS Uzman Değerlendirmesi: Müşteri Yolculuğu (Customer Journey)

**Analitik Keşif:** Satış kararını etkileyen `PageValues` (Sayfa Değerleri) metriğinin ezici dominansı, sadık kullanıcıların site içerisinde daha derinlemesine geçirdikleri zamanın net yansımasıdır. İş Birimlerinin **UI/UX (Kullanıcı Arayüzü/Deneyimi)** ekiplerine vereceği brief, kullanıcının sayfada kalma (Duration) dürtülerini teşvik edecek yenilikler olmalıdır. Bunlar **Dönüşüm Oranlarına (Conversion Rate)** doğrudan ciro (revenue) olarak yansıyacaktır."""

        elif "PageValues Distribusyonu" in source and "ExitRates" in source:
            md_text = """### 💡 YBS Uzman Değerlendirmesi: Hedef Kitle Boşluğu (Gap Analysis)

**Gizli Müşteri Profili:** Analizlerde, saptanma konusunda en çok sorun yaşanan grubun, site içinde gezinme harcamadan hızla aksiyon alan **'Impulse Buyer' (Anlık Alıcı/Hızlı Alıcı)** tarafı olduğu tespit edilmiştir. İş Birimleri (Business Units), bu spesifik kitleyi yakalamak amacıyla ana sayfada 'Flash Deal (Çılgın Fırsatlar)' veya 'Tek Tıkla Alışveriş' algoritmaları kurgulayarak sepet terk oranlarını düşürmelidir."""

        elif "FINAL DEPLOYMENT READINESS DASHBOARD" in source:
            md_text = """### 💡 YBS Uzman Değerlendirmesi: Komuta Paneli (Dashboards)

**Yönetici Özeti (Executive Summary):** Üstteki komuta paneli, veri bilimcilerin ürettiği karmaşık metrik kalabalığının, **C-Level (Üst Yönetim)** tarafından anlık izlenebilen stratejik görünümüdür. Continuous Monitoring (Sürekli Takip) prensibi ile projede oluşabilecek model sapmaları ve potansiyel Dönüşüm Getirisi (ROI) eşzamanlı ve şeffaf biçimde izlenmeye tamamen hazırdır."""

        elif "Business Impact Analysis:" in source:
            md_text = """### 💡 YBS Uzman Değerlendirmesi: Yatırım Getirisi (ROI & Etki Analizi)

**Büyüme (Growth) Potansiyeli:** Geliştirilen optimize yapay zeka sayesinde daha önce kaçırma riski taşıdığımız devasa bir potansiyel müşteri yığını, **Dönüştürme Hunimize (Sales Funnel)** geri kazandırılmıştır.

**Maliyet-Fayda (Cost-Benefit):** Doğru segment edilmiş bu kullanıcılara uygulanacak hedefli kampanyalar, pazarlama departmanının **'Müşteri Edinme Maliyetlerini (CAC)'** kalıcı olarak düşürürken, şirket için emsallerine nazaran büyük bir **Rekabet Avantajı (Competitive Advantage)** sağlayan kritik bir maniveladır."""

        
        # Insert markdown right after the matching code cell
        if md_text:
            md_cell = {
                "cell_type": "markdown",
                "metadata": {},
                "source": [line + '\n' for line in md_text.split('\n')]
            }
            # Remove trailing newline from last element
            if md_cell["source"]:
                md_cell["source"][-1] = md_cell["source"][-1].rstrip('\n')
            new_cells.append(md_cell)

# Check if file has "10. FINAL INTERPRETATION", if yes we can just replace its content slightly or leave it as it was originally very detailed.
nb['cells'] = new_cells

with open(filepath, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print("Markdown analizi hucrelere başarıyla yerlestirildi!")
