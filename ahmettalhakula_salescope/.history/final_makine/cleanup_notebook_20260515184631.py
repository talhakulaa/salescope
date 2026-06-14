import json

# Notebook'u yükle
with open('project_presentation.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Silinecek cell ID'lerini tanımla (Cells 53-66 redundant modeling)
delete_cell_ids = [
    'a569f223',  # Cell 53: code
    'dc598567',  # Cell 54: markdown
    '6836ab39',  # Cell 55: code
    '5eea975d',  # Cell 56: markdown
    'bf622a12',  # Cell 57: code
    '82f3e975',  # Cell 58: markdown
    '0c237922',  # Cell 59: code
    '0797b7d2',  # Cell 60: markdown
    '1372b82e',  # Cell 61: code
    '55579e10',  # Cell 62: markdown
    'fbdff883',  # Cell 63: code
    'b7685493',  # Cell 64: markdown
    'c9ab65d8',  # Cell 65: code
    '1d76bf2e',  # Cell 66: markdown
]

# Cells'leri filtrele
original_count = len(nb['cells'])
nb['cells'] = [c for c in nb['cells'] if c.get('id', '') not in delete_cell_ids]
new_count = len(nb['cells'])

# Notebook'u kaydet
with open('project_presentation.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f"✅ Başarı!")
print(f"   Orijinal hücre sayısı: {original_count}")
print(f"   Silinen hücreler: {original_count - new_count}")
print(f"   Yeni hücre sayısı: {new_count}")
print(f"\n✓ Redundant modelleme işlemleri silindi (eski Cells 53-66)")
print(f"✓ Sunum ve Conclusions kısımları kaldı")
