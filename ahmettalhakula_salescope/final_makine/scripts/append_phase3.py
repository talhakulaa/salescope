import nbformat

notebook_path = 'project_presentation.ipynb'
with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = nbformat.read(f, as_version=4)

cells_to_add = [
    # 1. Phase 3 Title (Markdown)
    nbformat.v4.new_markdown_cell("""<style>
@keyframes pulseGlowPrep {
0% { box-shadow: 0 0 10px #e67e22, 0 0 20px #d35400; }
50% { box-shadow: 0 0 30px #d35400, 0 0 50px #e67e22; }
100% { box-shadow: 0 0 10px #e67e22, 0 0 20px #d35400; }
}
.prep-glow {
animation: pulseGlowPrep 4s infinite alternate ease-in-out;
background: linear-gradient(135deg, #1f1105 0%, #3e1f00 100%);
padding: 25px;
border-left: 8px solid #e67e22;
border-radius: 15px;
margin-top: 30px;
color: white;
}
</style>

<div class="prep-glow">
<h2 style="color: #e67e22; font-size: 1.8em; border-bottom: 1px solid rgba(255,255,255,0.2); padding-bottom: 10px; text-shadow: 0 0 10px rgba(230,126,34,0.8);">
⚙️ 3. Veri Hazırlama (Data Preparation)
</h2>
<p style="font-size: 1.05em; line-height: 1.8; margin-top: 20px; color: #ecf0f1;">
<strong>CRISP-DM</strong> metodolojimizin kalbi: Veriyi modele hazır hale getirmek. Bu aşamada; veri temizliği, aykırı değer yönetimi, özellik mühendisliği (Feature Engineering) ve veri ölçekleme adımlarını uyguluyoruz.
</p>
</div>"""),

    # 2. Missing Values (Code)
    nbformat.v4.new_code_cell("""# 1. Eksik Veri Kontrolü (Missing Values)
import pandas as pd

missing_values = df.isnull().sum()
missing_summary = missing_values[missing_values > 0]

if missing_summary.empty:
    print("✅ Veri setinde eksik değer (null/NaN) bulunmamaktadır. Veri bütünlüğü %100'dür.")
else:
    print(missing_summary)
"""),

    # 3. Missing Values (Markdown)
    nbformat.v4.new_markdown_cell("""💡 **YBS Uzman Değerlendirmesi | Eksik Veri Yönetimi:** 
E-ticaret verilerinde eksik veriler çoğunlukla sistem hatalarından veya çerez politikası reddinden kaynaklanır. Veri setimizde hiç eksik veri olmaması, arka plandaki veri ambarı (DWH) altyapısının sağlamlığının bir göstergesidir. Eğer olsaydı; finansal özelliklerde *medyan* atama, kategoriklerde ise *mod* veya makine öğrenmesi tabanlı *KNN imputation* stratejileri uygulayacaktık."""),

    # 4. Outliers & Multicollinearity (Code)
    nbformat.v4.new_code_cell("""# 2. Çoklu Doğrusallık (Multicollinearity) ve Aykırı Değer (Outlier) Stratejisi
# BounceRates & ExitRates (r=0.91)
# ProductRelated & ProductRelated_Duration (r=0.86)
drop_cols = ['BounceRates', 'ProductRelated_Duration']
df_prep = df.drop(columns=drop_cols)

print(f"🗑️ Çoklu doğrusallığı engellemek için {drop_cols} özellikleri veri setinden çıkarıldı.")
print("📉 Aykırı değerler için ise datayı traşlamak (Winsorize) yerine, dağılımı koruyan ancak aykırı uçlara dirençli 'RobustScaler' kullanımı tercih edildi.")
"""),

    # 5. Outliers (Markdown)
    nbformat.v4.new_markdown_cell("""💡 **YBS Uzman Değerlendirmesi | Aykırı Değer (Outlier) Stratejisi:** 
E-ticarette devasa sepetler oluşturan veya sitede saatlerini geçiren müşteriler "aykırı/hatalı data" değil; **"VIP Müşteri Segmenti"** potansiyeli taşırlar. Eğer bu verileri silersek modelimiz yüksek gelir bırakan zengin müşterileri tanıma yeteneğini kaybeder. Bu yüzden aykırı değerleri silmek yerine, onlara dirençli istatistiksel ölçekleyiciler kullanıyoruz. Aynı zamanda yüksek korelasyonlu metrikleri sistemden çıkartarak modelin analiz süresini hızlandırıyoruz (Computing Cost optimizasyonu)."""),

    # 6. Feature Engineering (Code)
    nbformat.v4.new_code_cell("""# 3. Feature Engineering (Özellik Mühendisliği)
# A. Toplam Etkileşim Süresi
df_prep["Total_Duration"] = df_prep["Administrative_Duration"] + df_prep["Informational_Duration"]

# B. Ziyaretçinin Etkileşim Skoru (Sayfa değeri * İncelenen ürün)
df_prep["Engagement_Score"] = df_prep["PageValues"] * df_prep["ProductRelated"]

# C. Risk Endeksi (0'a bölünme hatasını engellemek için +0.0001 eklendi)
df_prep["Risk_Index"] = df_prep["ExitRates"] / (df_prep["PageValues"] + 0.0001)

# D. Ziyaretçi Tipi Flag (Sürekli müşteri mi?)
df_prep["Returning_Visitor_Flag"] = (df_prep["VisitorType"] == "Returning_Visitor").astype(int)

# Veriyi tipe uygun hazırlama
df_prep['Revenue'] = df_prep['Revenue'].astype(int)
df_prep['Weekend'] = df_prep['Weekend'].astype(int)

from IPython.display import display
display(df_prep[['Total_Duration', 'Engagement_Score', 'Risk_Index', 'Returning_Visitor_Flag']].head())
"""),

    # 7. Feature Engineering (Markdown)
    nbformat.v4.new_markdown_cell("""💡 **YBS Uzman Değerlendirmesi | Özellik Mühendisliği (Feature Engineering):** 
Salt datayı **Bilgiye** dönüştürdüğümüz stratejik aşama. Örneğin sadece sayfada kalma süresine bakmak yerine, sayfanın maddi değerini (PageValue) tıklanan ürün sayısıyla çarparak oluşturduğumuz **Engagement_Score (Etkileşim Skoru)**, işletmeye kullanıcının LTV (Müşteri Yaşam Boyu Değeri) potansiyelini özetler. Yeni hedefli metrikler, modelimizin adeta bir C-Level analist mantığıyla karar almasını olanaklı kılar."""),

    # 8. Encoding & Scaling (Code)
    nbformat.v4.new_code_cell("""# 4. Kategorik Dönüştürme (Encoding) ve Ölçekleme (Scaling) Altyapısı
from sklearn.preprocessing import RobustScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

cat_nominal = ['VisitorType', 'OperatingSystems', 'Browser', 'Region', 'TrafficType']
nominal_transformer = Pipeline(steps=[
    ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
])

num_cols = ['Administrative', 'Administrative_Duration', 'Informational', 'Informational_Duration', 
            'ProductRelated', 'ExitRates', 'PageValues', 'SpecialDay', 
            'Total_Duration', 'Engagement_Score', 'Risk_Index']
num_transformer = Pipeline(steps=[
    ('scaler', RobustScaler())
])

print("✅ Pipeline Altyapısı Hazır: OneHotEncoder (Kategorik OHE) & RobustScaler (Sayısal Ölçekleme)")
"""),

    # 9. Encoding & Scaling (Markdown)
    nbformat.v4.new_markdown_cell("""💡 **YBS Uzman Değerlendirmesi | Scaling ve Encoding (Değişken Dönüşümleri):** 
Bilgisayarlar "Geri dönen müşteri" gibi metinleri okuyamazlar. Bu verileri algoritmaların anlayabilmesi için One-Hot Encoding ile matematize ettik. Ayrıca, bir müşterinin sitede kalma süresi 1 ssat iken girdiği ürün sayısı 5 olabilir. Skalaları tamamen farklı boyutlarda olan bu tarz verilerin algoritmayı baskılayarak körleştirmesini engellemek için, istatistiksel standartlaştırma sağlayan **RobustScaler** metodunu uyguladık."""),

    # 10. Data Splitting (Code)
    nbformat.v4.new_code_cell("""# 5. Veri Bölme İşlemi (Train / Test Split)
from sklearn.model_selection import train_test_split

X = df_prep.drop(columns=['Revenue'])
y = df_prep['Revenue']

# Leakage (Sızıntı) durumu oluşmaması adına; modelin eğitimi ve testi tamamen yalıtılmıştır.
# Sınıf dengesizliği bulunduğu için stratify işlemi uyguluyoruz.
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print(f"📊 Eğitim Seti (Train) Veri Boyutu : {X_train.shape[0]} satır")
print(f"🧪 Test Seti (Test) Veri Boyutu    : {X_test.shape[0]} satır")
print(f"🎯 Hedef Sınıf (Revenue=1) Test Seti Dağılımı: %{y_test.mean()*100:.2f}")
"""),

    # 11. Data Splitting (Markdown)
    nbformat.v4.new_markdown_cell("""💡 **YBS Uzman Değerlendirmesi | Veriyi Bölme (Train/Test Split):** 
Bir modeli sınavdan önce çözdüğü sorularla test ederseniz, iyi bir not alır ama buna "Ezber (Overfitting)" denir. Modelin hiç tanımadığı kullanıcılara karşı nasıl tepki vereceğini test etmek için verimizin %20'sini tamamen izole edip rafa kaldırdık. 

Ayrıca sadece %15'lik kısmın ürün satın aldığı bir veri setinde (class imbalance), bu bölümlemenin rassal (random) yapılması durumunda test setinde kalibrasyon bozulabilir. `stratify=y` özelliğiyle VIP (satış yapan) gruptan eğitim ve teste eşit pay düşmesini garanti altına alarak bilimsel stabilite (reliability) oluşturduk.""")
]

nb.cells.extend(cells_to_add)

with open(notebook_path, 'w', encoding='utf-8') as f:
    nbformat.write(nb, f)

print("Phase 3 hücreleri project_presentation.ipynb notebook'una başarıyla eklendi!")
