import json

with open('project_presentation.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)
    print(f"Total cells: {len(nb['cells'])}\n")
    print("Last 16 cells (redundant modeling):")
    for i, cell in enumerate(nb['cells'][-16:]):
        cell_id = cell.get('id', 'NO ID')
        cell_type = cell.get('cell_type', '?')
        idx = len(nb['cells']) - 16 + i
        print(f"Cell {idx} (index {idx}): id={cell_id}, type={cell_type}")
