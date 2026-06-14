import json
import re
import os

filepath = "/Users/sudenazcobanoglu/Desktop/final_makina/final_makine/scripts/final_evaluation_dashboard.ipynb"
with open(filepath, 'r', encoding='utf-8') as f:
    nb = json.load(f)

plot_names = [
    "final_model_confusion_matrix.png",
    "final_model_metrics_comparison.png",
    "final_model_roc_curve.png",
    "final_model_precision_recall_curve.png",
    "final_model_feature_importance.png",
    "final_model_false_negative_pagevalues.png",
    "final_model_false_negative_duration.png",
    "final_model_business_impact.png",
    "final_model_learning_curve.png"
]

show_idx = 0
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        new_source = []
        for line in cell['source']:
            if "plt.show()" in line:
                if show_idx < len(plot_names):
                    # Add savefig before show
                    indent = line[:len(line) - len(line.lstrip())]
                    new_source.append(f"{indent}plt.savefig(f'../figures/{plot_names[show_idx]}', dpi=300, bbox_inches='tight')\n")
                    show_idx += 1
            new_source.append(line)
        cell['source'] = new_source

with open(filepath, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print(f"Injected savefig for {show_idx} plots.")
