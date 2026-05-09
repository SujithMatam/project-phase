import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load the synthesized subgroup dataset which has Months 0, 1, 3, 6
df = pd.read_csv("subgroup_analysis_dataset.csv")

# ============================================================
# FIGURE 2: LONGITUDINAL OUTCOMES (AI vs Doctor)
# ============================================================
print("GENERATING FIGURE 2: LONGITUDINAL OUTCOMES...\n")

fig, axes = plt.subplots(2, 2, figsize=(14, 12))
metrics = ["GAD7", "function_aggregated", "PCS", "MCS"]
titles = ["A: GAD-7 (Anxiety)", "B: Function Score", "C: PCS (Physical Health)", "D: MCS (Mental Health)"]
months = [0, 1, 3, 6]
month_labels = ["Pre-op", "1-Month", "3-Month", "6-Month"]

color_ai = '#FF5C39'
color_doc = '#FCDAB2'

for i, met in enumerate(metrics):
    ax = axes[i//2, i%2]
    
    # Calculate means and errors for each group at each timepoint
    ai_means = []
    ai_errs = []
    doc_means = []
    doc_errs = []
    
    for m in months:
        ai_data = df[(df["group"] == "AI") & (df["month"] == m)][met]
        doc_data = df[(df["group"] == "Doctor") & (df["month"] == m)][met]
        
        ai_means.append(ai_data.mean())
        ai_errs.append(ai_data.std() / np.sqrt(len(ai_data)) if len(ai_data) > 0 else 0)
        
        doc_means.append(doc_data.mean())
        doc_errs.append(doc_data.std() / np.sqrt(len(doc_data)) if len(doc_data) > 0 else 0)
    
    # Plotting lines with error bars
    ax.errorbar(months, ai_means, yerr=ai_errs, fmt='-o', color=color_ai, label="AI Group", capsize=5, linewidth=2)
    ax.errorbar(months, doc_means, yerr=doc_errs, fmt='-o', color=color_doc, label="Doctor Group", capsize=5, linewidth=2)
    
    ax.set_xticks(months)
    ax.set_xticklabels(month_labels)
    ax.set_title(titles[i], fontsize=14, pad=15)
    ax.set_xlabel("Time Point")
    ax.set_ylabel("Score")
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend()

plt.tight_layout()
fig.savefig("figure2_longitudinal_outcomes.png", dpi=300)
print("SAVED: figure2_longitudinal_outcomes.png")
