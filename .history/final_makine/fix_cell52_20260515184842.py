import json

with open('project_presentation.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Cell 52'yi bul ve düzelt
for cell in nb['cells']:
    if cell.get('id') == '0ce0b3ea':
        code = cell['source']
        if isinstance(code, list):
            code_str = ''.join(code)
        else:
            code_str = code
        
        # Replace best_info with successful_models_sorted[0]
        code_str = code_str.replace(
            'print(f"   • Perfor Metriği (Test F1): {best_info[\'Test F1\']}")',
            'print(f"   • Perfor Metriği (Test F1): {successful_models_sorted[0][\'Test F1\']}")\nprint(f"   • Test Recall: {successful_models_sorted[0][\'Test Recall\']}")'
        )
        
        cell['source'] = code_str.split('\n')
        break

with open('project_presentation.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("✅ Cell 52 fixed!")
