import json

filepath = "/Users/sudenazcobanoglu/Desktop/final_makina/final_makine/scripts/final_evaluation_dashboard.ipynb"
with open(filepath, 'r', encoding='utf-8') as f:
    nb = json.load(f)

new_cells = []
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = "".join(cell['source'])
        
        md_text = ""
        # 1. CM
        if "cm_final = confusion_matrix" in source:
             md_text = "### 💡 YBS Analizi: Confusion Matrix\n**Stratejik Kazanım:** Kaçırılan potansiyel alıcı (False Negative) oranındaki dramatik düşüş, şirketimizin Fırsat Maliyetini (Opportunity Cost) minimize etmektedir. Yanlışlıkla alıcı profiline dahil edilenlerin (False Positive) getirdiği operasyonel retargeting maliyeti, kazanılan yeni satışların Müşteri Yaşam Boyu Değeri (CLV) yanında tolere edilebilir düzeydedir."
             # clean up old prints
             source = source.split('print(')[0].rstrip()
             
        # 2. Classification Metrics
        elif "Classification Metrics Comparison" in source:
             md_text = "### 💡 YBS Analizi: Sınıflandırma Metrikleri\nSalt **'Accuracy' (Doğruluk)** metriği yerine, azınlık sınıfı olan gerçek alıcıları bulma yeteneğimizin **(Recall)** maksimize edilmesi hedeflenmiştir. F1-Score dengesinin korunması, algoritmik başarının operasyonel bütçe yönetimiyle eşgüdümlü çalıştığını kanıtlar."
             source = source.split('print(')[0].rstrip()
             
        # 3. Threshold Analysis
        elif "Threshold vs Precision" in source:
             md_text = "### 💡 YBS Analizi: Karar Sınırı (Threshold)\n**Karar Sınırı Optimizasyonu:** Karar Destek Sistemimiz (DSS), e-ticaret dinamiklerine göre risk iştahını (0.35) optimize etmiştir. Precision'da yaşanan olağan düşüş maliyeti, Recall artışının getireceği yüksek ciro (Revenue) hacmi ile kompanse edilecek stratejik bir karardır."
             source = source.split('print(')[0].rstrip()

        # 4. ROC Curve
        elif "ROC Curve Comparison" in source:
             md_text = "### 💡 YBS Analizi: ROC Eğrisi\nModelin ziyaretçi ile alıcıyı ayrıştırmadaki sağlamlığı **(Robustness)** kanıtlanmıştır. Yüksek AUC, Pazarlama biriminin farklı segmentasyon ve kampanya kurgularında da bu veri analitiği çıktılarına güvenebileceğinin bir metrik garantisidir."
             source = source.split('print(')[0].rstrip()

        # 5. Precision Recall
        elif "Precision-Recall Curve Comparison" in source:
             md_text = "### 💡 YBS Analizi: Precision-Recall\n**Kaynak Yönetimi:** Şirket kârlılığını belirleyen asıl %15'lik alıcı kitlesi üzerinde dengeli bir başarı sergilenmiştir. Pazarlama bütçesinin salt tık avcılarına değil, gerçek potansiyel alıcılara (hedef kitle optimizasyonu) odaklanmasını sağlar."
             source = source.split('print(')[0].rstrip()

        # 6. Feature Importance
        elif "Top 15 Feature Importances" in source:
             md_text = "### 💡 YBS Analizi: Özellik Önemi (Feature Importance)\n**Kullanıcı Yolculuğu (Customer Journey):** `PageValues` metriğinin ezici dominansı, kullanıcıların satın alma niyetlerini nihai adımlara kadar taşıdığını gösterir. UI/UX (Kullanıcı Arayüzü/Deneyimi) optimizasyonu ve sayfada kalma (Duration) teşviklerinin dönüşüm oranlarına (Conversion Rate) doğrudan ciro olarak yansıyacağını işaret etmektedir."
             source = source.split('print(')[0].rstrip()

        # 7. False Negative
        elif "False Negative" in source and "Outcome" in source:
             md_text = "### 💡 YBS Analizi: Yanlış Negatifler (False Negatives)\n**Gizli Müşteri Profili Keşfi:** Modelin kaçırdığı spesifik grubun platformda doğrudan aksiyon (Sepet) alan, gezinmeyen **'Impulse Buyer' (Anlık Alıcı)** profili olduğu tespit edilmiştir. İş Birimleri (Business Units), bu spesifik kitle için ana sayfada 'Flash Deal' gibi anlık stratejiler kurgulamalıdır."
             source = source.split('print(')[0].rstrip()

        # 8. Dashboard
        elif "FINAL DEPLOYMENT READINESS DASHBOARD" in source:
             md_text = "### 💡 YBS Analizi: Komuta Paneli (Dashboard)\n**Yönetici Özeti (Executive Summary):** Bu komuta paneli, teknik yapay zeka çıktılarının C-Level (Üst Yönetim) stratejik görünümüdür. Sürekli takip ile model riskleri ve potansiyel Dönüşüm Getirisi (ROI) eşzamanlı ve şeffaf biçimde izlenmeye hazırdır."
             source = source.split('print(')[0].rstrip()

        # 9. Business Impact
        elif "Business Impact Analysis" in source:
             md_text = "### 💡 YBS Analizi: Etki ve Büyüme Potansiyeli (ROI)\n**Büyüme Potansiyeli:** Geliştirilen optimize algoritmalar sayesinde yüzlerce potansiyel müşteri Dönüştürme Hunimize (Sales Funnel) geri kazandırılmıştır.\n\n**Maliyet-Fayda Dengesi:** Doğru segment edilmiş bu kullanıcılara uygulanacak hedefli kampanyalar, **'Müşteri Edinme Maliyetlerini (CAC)'** düşürürken şirket için **Rekabet Avantajı (Competitive Advantage)** sağlayan kritik bir kaldıraç niteliğindedir."
             source = source.split('print(')[0].rstrip()

        # Re-pack source
        cell['source'] = [line + '\n' for line in source.split('\n')]
        if cell['source'] and cell['source'][-1].endswith('\n') and source and not source.endswith('\n'):
            cell['source'][-1] = cell['source'][-1].rstrip('\n')

        new_cells.append(cell)
        
        if md_text:
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

nb['cells'] = new_cells

with open(filepath, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print("Graphs and Markdown integrated successfully!")
