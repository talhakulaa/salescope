import nbformat as nbf

def add_cells():
    nb = nbf.read('project_presentation.ipynb', as_version=4)
    # Find insertion index (after 2. Veriyi Anlama)
    idx = 0
    for i, c in enumerate(nb.cells):
        if '2. Veriyi Anlama' in c.source:
            idx = i
            break
            
    md_tpl = '<div style="background: rgba(0,0,0,0.3); padding: 15px; border-left: 5px solid #1abc9c; margin-top: 10px;">\n\n### {title}\n{content}\n</div>'
    
    new_cells = []
    
    # 2.1 Focus
    new_cells.append(nbf.v4.new_markdown_cell('### 2.1 Dataset Genel Görünümü'))
    new_cells.append(nbf.v4.new_code_cell("import pandas as pd\nimport numpy as np\nimport plotly.express as px\nimport plotly.graph_objects as go\nimport plotly.io as pio\npio.templates.default = 'plotly_dark'\n\ndisplay(df.head())\ndisplay(df.tail())\nprint(f'Dimensions: {df.shape}')\ndisplay(df.dtypes.to_frame('Data Type'))"))
    new_cells.append(nbf.v4.new_markdown_cell(md_tpl.format(title='YBS / İş Stratejisi Yorumu:', content='Veri boyutları ve yapısal özeti hedeflere uygun strateji geliştirmeyi destekleyecek niteliktedir.')))
    
    # 2.2 Stats
    new_cells.append(nbf.v4.new_markdown_cell('### 2.2 İstatistiksel Özet'))
    new_cells.append(nbf.v4.new_code_cell("display(df.describe().T)\n\nskewness = df.select_dtypes(include=[np.number]).skew()\nkurtosis = df.select_dtypes(include=[np.number]).kurt()\ndisplay(pd.DataFrame({'Skewness': skewness, 'Kurtosis': kurtosis}))"))
    new_cells.append(nbf.v4.new_markdown_cell(md_tpl.format(title='YBS / İş Stratejisi Yorumu:', content='Çarpıklık değerleri verinin normalize edilmesi gerekebileceğini veya belirli e-ticaret metriklerinin asimetrik dağıldığını göstermektedir.')))

    # 2.3 Missing
    new_cells.append(nbf.v4.new_markdown_cell('### 2.3 Eksik Değerler'))
    new_cells.append(nbf.v4.new_code_cell("null_counts = df.isnull().sum()\ndisplay(null_counts[null_counts > 0])\n\nfig = px.imshow(df.isnull().T, aspect='auto', color_continuous_scale='gray', title='Eksik Değer Isı Haritası')\nfig.show()"))
    new_cells.append(nbf.v4.new_markdown_cell(md_tpl.format(title='YBS / İş Stratejisi Yorumu:', content='Eksik verilerin yönetim stratejisi, müşteri kayıt kalitesini doğrudan etkilemektedir.')))

    # 2.4 Outliers
    new_cells.append(nbf.v4.new_markdown_cell('### 2.4 Aykırı Değerler'))
    new_cells.append(nbf.v4.new_code_cell("fig = go.Figure()\nfor col in df.select_dtypes(include=[np.number]).columns:\n    fig.add_trace(go.Box(y=df[col], name=col))\nfig.update_layout(title='Sayısal Değişkenlerin Dağılımı ve Aykırı Değerleri', showlegend=False)\nfig.show()"))
    new_cells.append(nbf.v4.new_markdown_cell(md_tpl.format(title='YBS / İş Stratejisi Yorumu:', content='Aykırı gözükebilen aşırı aktif ziyaretçiler aslında satın alma potansiyeli yüksek bir niş kitleyi yansıtıyor olabilir.')))

    # 2.5 Target
    new_cells.append(nbf.v4.new_markdown_cell('### 2.5 Hedef Değişken Analizi'))
    new_cells.append(nbf.v4.new_code_cell("target_counts = df['Revenue'].value_counts().reset_index()\ntarget_counts.columns = ['Revenue', 'Count']\nfig = px.pie(target_counts, names='Revenue', values='Count', title='Revenue (Satın Alma) Dağılımı', hole=0.4)\nfig.show()"))
    new_cells.append(nbf.v4.new_markdown_cell(md_tpl.format(title='YBS / İş Stratejisi Yorumu:', content='Sınıf dengesizliği (Class imbalance) işletmenin dönüşüm oranını (Conversion Rate) yansıtmaktadır ve modelleme aşamasında özel olarak ele alınmalıdır.')))

    # 2.6 Univariate
    new_cells.append(nbf.v4.new_markdown_cell('### 2.6 Tekli Değişken Analizi'))
    new_cells.append(nbf.v4.new_code_cell("fig = px.histogram(df, x='PageValues', marginal='box', title='PageValues Dağılımı')\nfig.show()"))
    new_cells.append(nbf.v4.new_markdown_cell(md_tpl.format(title='YBS / İş Stratejisi Yorumu:', content='PageValues metriğinin dağılımı, platformdaki bazı sayfaların değerinin çok yüksek olduğunu göstermektedir.')))

    # 2.7 Bivariate
    new_cells.append(nbf.v4.new_markdown_cell('### 2.7 İkili Değişken Analizi'))
    new_cells.append(nbf.v4.new_code_cell("fig = px.violin(df, x='Revenue', y='PageValues', color='Revenue', box=True, title='Revenue Durumuna Göre PageValues')\nfig.show()"))
    new_cells.append(nbf.v4.new_markdown_cell(md_tpl.format(title='YBS / İş Stratejisi Yorumu:', content='Sayfa değerinin yüksekliği ile gelir dönüşümü arasında çok net bir ayrım potansiyeli gözlemlenmektedir.')))

    # 2.8 Multivariate
    new_cells.append(nbf.v4.new_markdown_cell('### 2.8 Çoklu Değişken Analizi'))
    new_cells.append(nbf.v4.new_code_cell("numeric_df = df.select_dtypes(include=[np.number])\ncorr = numeric_df.corr()\nfig = px.imshow(corr, text_auto='.2f', aspect='auto', title='Korelasyon Matrisi', color_continuous_scale='RdBu_r')\nfig.show()"))
    new_cells.append(nbf.v4.new_markdown_cell(md_tpl.format(title='YBS / İş Stratejisi Yorumu:', content='Özellikler arası korelasyon haritası, çoklu doğrusallık risklerini tespit etmek ve özellik mühendisliğine yön vermek için kritiktir.')))

    nb.cells[idx+1:idx+1] = new_cells
    nbf.write(nb, 'project_presentation.ipynb')

if __name__ == '__main__':
    add_cells()
