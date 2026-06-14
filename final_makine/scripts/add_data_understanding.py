import nbformat as nbf

def main():
    path = '/Users/sudenazcobanoglu/Desktop/final_makina/final_makine/project_presentation.ipynb'
    with open(path, 'r', encoding='utf-8') as f:
        nb = nbf.read(f, as_version=4)
        
    md1 = """<style>
@keyframes pulseGlowData {
0% { box-shadow: 0 0 10px #16a085, 0 0 20px #1abc9c; }
50% { box-shadow: 0 0 30px #1abc9c, 0 0 50px #16a085; }
100% { box-shadow: 0 0 10px #16a085, 0 0 20px #1abc9c; }
}
.data-glow {
animation: pulseGlowData 4s infinite alternate ease-in-out;
background: linear-gradient(135deg, #0b1c2c 0%, #1a365d 100%);
padding: 25px;
border-left: 8px solid #1abc9c;
border-radius: 15px;
margin-top: 30px;
color: white;
}
</style>

<div class="data-glow">
<h2 style="color: #1abc9c; font-size: 1.8em; border-bottom: 1px solid rgba(255,255,255,0.2); padding-bottom: 10px; text-shadow: 0 0 10px rgba(26,188,156,0.8);">
📊 2. Veriyi Anlama (Data Understanding)
</h2>
<p style="font-size: 1.05em; line-height: 1.8; margin-top: 20px; color: #ecf0f1;">
<strong>CRISP-DM</strong> metodolojimizin ikinci adımı olan veriyi anlama aşamasında, çevrimiçi müşteri davranışlarını yansıtan veri setimizin yapısını, kalitesini ve temel karakteristiklerini inceliyoruz. Sınıf dengesizliği (class imbalance) ve eksik veri yönetimi bu aşamanın en kritik odak noktalarındandır.
</p>
</div>"""

    code1 = """import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Görüntü ayarları
plt.style.use('dark_background')
sns.set_palette("muted")

# Veri setini yükleme
df = pd.read_csv('data/raw/online_shoppers_intention.csv')

print("--- Veri Seti Boyutu ---")
print(f"Satır: {df.shape[0]}, Sütun: {df.shape[1]}\\n")

print("--- Değişken Türleri ---")
df.info()"""

    md2 = """💡 **YBS Uzman Değerlendirmesi | Veri Yapısı:** 
12.330 etkileşim kaydından oluşan veri setimiz müşterinin o anki dijital ayak izini tutuyor. Hem sayısal değişkenlerin (sayfada geçirilen süreler vb.) hem de kategorik değişkenlerin (ziyaretçi tipi, işletim sistemi) mevcudiyeti, modelin **ziyaretçi bağlamını (context)** çok zengin bir şekilde yorumlamasını sağlayacaktır."""

    code2 = """# Eksik Değer Kontrolü
missing_values = df.isnull().sum()
missing_values = missing_values[missing_values > 0]

if missing_values.empty:
    print("✅ Veri setinde eksik değer (Null/NaN) bulunmamaktadır.")
else:
    print("❌ Eksik Değerler:\\n", missing_values)"""

    md3 = """💡 **YBS Uzman Değerlendirmesi | Eksik Değerler:** 
Veride hiç boş (null) kayıt bulunmaması, veri toplama mekanizmamızın (sayfa analitiği tarafı) son derece sağlıklı çalıştığını gösteriyor. Dolgu (imputation) süreçleriyle vakit kaybetmeden doğrudan yapısal analizlere geçiş yapabiliyoruz; bu durum geliştirme adımlarında ciddi **zaman ve efor kazancı** anlamına gelir."""

    code3 = """# Hedef Değişken (Revenue) Dağılımı ve Sınıf Dengesizliği
plt.figure(figsize=(7, 4))
ax = sns.countplot(data=df, x='Revenue', palette=['#ff7675','#55efc4'])
plt.title('Hedef Değişken Dağılımı (Satın Alma Gerçekleşti mi?)')
plt.ylabel('Kullanıcı Sayısı')

total = len(df)
for p in ax.patches:
    height = p.get_height()
    ax.text(p.get_x() + p.get_width()/2., height + 50,
            f'{height} ({height/total:.1%})', ha="center", weight='bold', color='white')
plt.show()"""

    md4 = """💡 **YBS Uzman Değerlendirmesi | Sınıf Dengesizliği:** 
E-ticaretin en klasik problemi karşımızda: Toplam platform trafiğinin sadece **%15.5'i** bir satışla sonuçlanıyor. Bu oran düşük gibi görünse de sektörel olarak son derece normaldir. 
Ancak istatistiksel model inşasında bu tablo devasa bir **Class Imbalance (Sınıf Dengesizliği)** yaratır. Önlem almadığımız senaryoda, algoritmamız kurnazlık yapıp "kimse satın almayacak" derse bile %85 başarı(Accuracy) elde edebilir. Bu yanılgıya düşmemek, fırsatları yakalamayı sağlayan yeteneğimizi (Recall) artırmak ve modeli eğitirken sentetik veri çoğaltma (SMOTE) kullanmak ana görevimizdir."""

    code4 = """# Temel Dağılımlar ve Aykırı Değer (Outlier) İncelemesi
plt.figure(figsize=(12, 5))

# 1. Page Values Dağılımı
plt.subplot(1, 2, 1)
sns.boxplot(y=df['PageValues'], x=df['Revenue'], palette=['#ff7675','#55efc4'])
plt.title('Sayfa Değeri (PageValues) vs Satın Alma (Revenue)')

# 2. Product Related Duration Dağılımı
plt.subplot(1, 2, 2)
sns.boxplot(y=df['ProductRelated_Duration'], x=df['Revenue'], palette=['#ff7675','#55efc4'])
plt.title('Ürün İnceleme Süresi vs Satın Alma')

plt.tight_layout()
plt.show()"""

    md5 = """💡 **YBS Uzman Değerlendirmesi | Aykırı Değerler:** 
Kutu grafiklerinin (Boxplots) yukarısındaki yoğun çizgi/noktalara (outliers) dikkat edin. E-ticarette bu değerler genellikle istatistiksel bir "gürültü (noise)" değil; nadir de olsa astronomik sepetler yapan ya da sitede saatlerini geçiren **"Niş Müşteri Segmentlerini"** işaret eder. 
Bununla birlikte, sağdaki ve soldaki kutuların boyları arasındaki farka baktığımızda; *PageValues* (Ziyaret edilen sayfaların ortalama parasal değeri) değişkeninde, satın alım yapanların müthiş bir yığılması var. Bu değişken, ciroyu (Revenue) tahminlemede **en güçlü prediktif (öngörücü) etken** olacağını daha şimdiden fısıldıyor."""

    nb.cells.extend([
        nbf.v4.new_markdown_cell(md1),
        nbf.v4.new_code_cell(code1),
        nbf.v4.new_markdown_cell(md2),
        nbf.v4.new_code_cell(code2),
        nbf.v4.new_markdown_cell(md3),
        nbf.v4.new_code_cell(code3),
        nbf.v4.new_markdown_cell(md4),
        nbf.v4.new_code_cell(code4),
        nbf.v4.new_markdown_cell(md5),
    ])
    
    with open(path, 'w', encoding='utf-8') as f:
        nbf.write(nb, f)
        
    print("Data understanding cells added to notebook successfully.")

if __name__ == '__main__':
    main()
