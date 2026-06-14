import json

with open('project_presentation.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)
    print("Cells 50-60:")
    for i, cell in enumerate(nb['cells'][50:60]):
        cell_id = cell.get('id', 'NO ID')
        cell_type = cell.get('cell_type', '?')
        print(f"Cell {50+i}: id={cell_id}, type={cell_type}")
