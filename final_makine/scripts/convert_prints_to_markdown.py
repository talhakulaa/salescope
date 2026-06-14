import json

filepath = "/Users/sudenazcobanoglu/Desktop/final_makina/final_makine/scripts/final_evaluation_dashboard.ipynb"
with open(filepath, 'r', encoding='utf-8') as f:
    nb = json.load(f)

new_cells = []
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = "".join(cell['source'])
        if '--- YBS Uzman Değerlendirmesi' in source:
            # We split the source code
            parts = source.split('print("\\n--- YBS Uzman')
            code_part = parts[0].rstrip()
            
            cell['source'] = [line + '\n' for line in code_part.split('\n')]
            # removing the last newline added
            if cell['source']:
                cell['source'][-1] = cell['source'][-1].rstrip('\n')
                
            new_cells.append(cell)
            
            # Create a Markdown Cell
            # We'll map the known print statements to nice markdown text.
            md_text = "### 💡 YBS Uzman Değerlendirmesi\n\n"
            
            if "Stratejik Kazanım" in source:
                md_text += "**Stratejik Kazanım:** Kaçırılan potansiyel alıcı (False Negative) oranındaki dramatik düşüş, şirketimizin Fırsat Maliyetini (Opportunity Cost) minimize etmektedir. Yanlışlıkla alıcı profiline dahil edilenlerin (False Positive) getirdiği operasyonel retargeting maliyeti, kazanılan yeni satışların Müşteri Yaşam Boyu Değeri (CLV) yanında tolere edilebilir düzeydedir."
            elif "Salt 'Accuracy'" in source:
                md_text += "Salt **'Accuracy' (Doğruluk)** metriği yerine, azınlık sınıfı olan gerçek alıcıları bulma yeteneğimizin **(Recall)** maksimize edilmesi hedeflenmiştir. F1-Score dengesinin korunması, algoritmik başarının operasyonel bütçe yönetimiyle eşgüdümlü çalıştığını kanıtlar."
            elif "Karar Sınırı (Threshold) Optimizasyonu" in source:
                md_text += "**Karar Sınırı (Threshold) Optimizasyonu:** Karar Destek Sistemimiz (DSS), e-ticaret dinamiklerine göre risk iştahını (0.35) optimize etmiştir. Precision'da yaşanan olağan düşüş maliyeti, Recall artışının getireceği yüksek ciro (Revenue) hacmi ile kompanse edilecek stratejik bir karardır."
            elif "Modelin ziyaretçi ile alıcıyı ayrıştırmadaki sağlamlığı" in source:
                md_text += "Modelin ziyaretçi ile alıcıyı ayrıştırmadaki sağlamlığı **(Robustness)** kanıtlanmıştır. Yüksek AUC, Pazarlama biriminin farklı segmentasyon ve kampanya kurgularında da bu veri analitiği çıktılarına güvenebileceğinin bir metrik garantisidir."
            elif "Precision-Recall Dengesi" in source:
                md_text += "**Precision-Recall Dengesi ve Kaynak Yönetimi:** Şirket kârlılığını belirleyen asıl %15'lik alıcı kitlesi üzerinde dengeli bir başarı sergilenmiştir. Pazarlama bütçesinin salt tık avcılarına değil, gerçek potansiyel alıcılara (hedef kitle optimizasyonu) odaklanmasını sağlar."
            elif "Kullanıcı Yolculuğu (Customer Journey)" in source:
                md_text += "**Kullanıcı Yolculuğu (Customer Journey) Analizi:** `PageValues` metriğinin ezici dominansı, kullanıcıların satın alma niyetlerini nihai adımlara kadar taşıdığını gösterir. UI/UX (Kullanıcı Arayüzü/Deneyimi) optimizasyonu ve sayfada kalma (Duration) teşviklerinin dönüşüm oranlarına (Conversion Rate) doğrudan ciro olarak yansıyacağını işaret etmektedir."
            elif "Gizli Müşteri Profili Keşfi:" in source:
                md_text += "**Gizli Müşteri Profili Keşfi:** Modelin kaçırdığı spesifik grubun platformda doğrudan aksiyon (Sepet) alan, gezinmeyen **'Impulse Buyer' (Anlık Alıcı)** profili olduğu tespit edilmiştir. İş Birimleri (Business Units), bu spesifik kitle için ana sayfada 'Flash Deal' gibi anlık stratejiler kurgulamalıdır."
            elif "Yönetici Özeti (Executive Summary):" in source:
                md_text = "### 💡 YBS Uzman Değerlendirmesi (Komuta Paneli)\n\n**Yönetici Özeti (Executive Summary):** Bu komuta paneli, teknik yapay zeka çıktılarının C-Level (Üst Yönetim) stratejik görünümüdür. Sürekli takip ile model riskleri ve potansiyel Dönüşüm Getirisi (ROI) eşzamanlı ve şeffaf biçimde izlenmeye hazırdır."
            elif "Büyüme Potansiyeli:" in source:
                md_text = "### 💡 YBS Uzman Değerlendirmesi (ROI & Etki Analizi)\n\n**Büyüme Potansiyeli:** Geliştirilen optimize DSS algoritması sayesinde ciddi oranda potansiyel müşteri Dönüştürme Hunimize (Sales Funnel) geri kazandırılmıştır.\n\n**Maliyet-Fayda Dengesi:** Doğru segment edilmiş bu kullanıcılara uygulanacak hedefli kampanyalar, **'Müşteri Edinme Maliyetlerini (CAC)'** düşürürken şirket için **Rekabet Avantajı (Competitive Advantage)** sağlayan kritik bir kaldıraç niteliğindedir."

            md_cell = {
                "cell_type": "markdown",
                "metadata": {},
                "source": [line + '\n' for line in md_text.split('\n')]
            }
            if md_cell["source"]:
                md_cell["source"][-1] = md_cell["source"][-1].rstrip('\n')
                
            new_cells.append(md_cell)
        else:
            new_cells.append(cell)
    else:
        new_cells.append(cell)

nb['cells'] = new_cells

with open(filepath, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print("Markdown cells created!")
