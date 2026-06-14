import json

# Notebook'u yükle
with open('project_presentation.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Silinecek cell ID'lerini tanımla (PHASE 6-12 redundant cells)
delete_cell_ids = [
    '#VSC-74c857cf',  # Cell 53: PHASE 6 markdown
    '#VSC-d9b95cd5',  # Cell 54: PHASE 6 code
    '#VSC-60f3500d',  # Cell 55: PHASE 7 markdown
    '#VSC-b92f8fa4',  # Cell 56: PHASE 7 code
    '#VSC-b13ceebe',  # Cell 57: PHASE 8 markdown
    '#VSC-c461962b',  # Cell 58: PHASE 8 code
    '#VSC-e2bdc351',  # Cell 59: PHASE 9 markdown
    '#VSC-41698329',  # Cell 60: PHASE 9 code
    '#VSC-53308f22',  # Cell 61: PHASE 10 markdown
    '#VSC-0efd10de',  # Cell 62: PHASE 10 code
    '#VSC-7c480ec3',  # Cell 63: PHASE 11 markdown
    '#VSC-705f0aac',  # Cell 64: PHASE 11 code
    '#VSC-8cfcdea5',  # Cell 65: PHASE 12 markdown
    '#VSC-41458a84',  # Cell 66: PHASE 12 code
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
print(f"✓ Sadece sunum kısımları kaldı (eski Cells 44-52)")
