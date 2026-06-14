import json

with open('project_presentation.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

for cell in nb.get('cells', []):
    if cell['cell_type'] == 'code':
        source = cell.get('source', [])
        src_str = "".join(source)
        if 'CONFUSION MATRIX VE SINIFLANDIRMA METRİKLERİ' in src_str:
            # We want to replace the Heatmap generation logic
            new_source = []
            for line in source:
                if "z=cm," in line:
                    new_source.append("    z=[[1, -1], [-1, 1]],\n")
                elif "colorscale='RdYlGn'," in line:
                    new_source.append("    colorscale=[[0, '#EF4444'], [1, '#10B981']],\n")
                    new_source.append("    showscale=False,\n")
                else:
                    new_source.append(line)
            cell['source'] = new_source

with open('project_presentation.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print("Notebook updated successfully.")
