import json

# Notebook'u yükle
with open('project_presentation.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Silinecek cell ID'lerini tanımla (PHASE 6-12 redundant cells)
delete_cell_ids = [
    '#VSC-3d67d73b',  # PHASE 6 markdown
    '#VSC-1729c591',  # PHASE 6 code
    '#VSC-6ad65060',  # PHASE 7 markdown
    '#VSC-fb8172d0',  # PHASE 7 code
    '#VSC-9f05aeaa',  # PHASE 8 markdown
    '#VSC-03950502',  # PHASE 8 code
    '#VSC-50fbb787',  # PHASE 9 markdown
    '#VSC-6018036c',  # PHASE 9 code
    '#VSC-3553463f',  # PHASE 10 markdown
    '#VSC-43924fbe',  # PHASE 10 code
    '#VSC-0d85cdb7',  # PHASE 11 markdown
    '#VSC-4293b5ed',  # PHASE 11 code (first part)
    '#VSC-098c2745',  # PHASE 12 markdown
    '#VSC-9d514f17',  # PHASE 12 code
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
