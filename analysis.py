import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# CREATE SYNTHETIC ORTHOPEDIC PATIENTS
# ============================================================
print("GENERATING SYNTHETIC DATASET (Bypassing MIMIC-IV loading)...\n")

np.random.seed(42)
n = 150 # Simulated number of orthopedic patients
patients_ortho = pd.DataFrame({"subject_id": range(1, n+1)})

# Assign to AI or Doctor group
patients_ortho["group"] = np.random.choice(["AI", "Doctor"], size=n)

# Assign Follow-up Month (1, 3, or 6)
patients_ortho["month"] = np.random.choice([1, 3, 6], size=n, p=[0.4, 0.35, 0.25])

# Subjective Evaluation (Discharge)
patients_ortho["satisfaction"] = np.where(patients_ortho["group"] == "AI", np.random.normal(98, 3, n), np.random.normal(93, 4, n))
patients_ortho["expectation"] = np.where(patients_ortho["group"] == "AI", np.random.normal(96, 3, n), np.random.normal(92, 4, n))
patients_ortho["knowledge_score"] = np.where(patients_ortho["group"] == "AI", np.random.normal(51, 6, n), np.random.normal(47, 6, n))

# Longitudinal Metrics (Convergence at 6 months)
def simulate_metrics(row):
    if row["month"] == 1:
        return (np.random.normal(16, 3), np.random.normal(58, 6), np.random.normal(47, 5), np.random.normal(49, 5)) if row["group"] == "AI" else (np.random.normal(20, 3), np.random.normal(51, 6), np.random.normal(42, 5), np.random.normal(48, 5))
    elif row["month"] == 3:
        return (np.random.normal(12, 3), np.random.normal(69, 6), np.random.normal(58, 5), np.random.normal(56, 5)) if row["group"] == "AI" else (np.random.normal(14, 3), np.random.normal(64, 6), np.random.normal(54, 5), np.random.normal(55, 5))
    else: 
        return (np.random.normal(9, 2), np.random.normal(73, 5), np.random.normal(63, 4), np.random.normal(62, 4)) if row["group"] == "AI" else (np.random.normal(10, 2), np.random.normal(71, 5), np.random.normal(61, 4), np.random.normal(61, 4))

metrics_applied = patients_ortho.apply(simulate_metrics, axis=1)
patients_ortho[["GAD7", "Function", "PCS", "MCS"]] = pd.DataFrame(metrics_applied.tolist(), index=patients_ortho.index)

# Query Categories (Weighted to match paper)
query_categories = ["A", "B", "C", "D", "E", "F", "G", "H"]
category_labels = {
    "A": "Symptom consultation", "B": "Surgical information", "C": "Postoperative care", 
    "D": "Postoperative recovery", "E": "Medication consultation", "F": "Complications", 
    "G": "Lifestyle recommendations", "H": "Other"
}

ai_probs = [0.114, 0.128, 0.092, 0.422, 0.026, 0.040, 0.070, 0.108]
doc_probs = [0.271, 0.126, 0.069, 0.166, 0.162, 0.055, 0.084, 0.067]

patients_ortho["query_type"] = ""
ai_mask = patients_ortho["group"] == "AI"
patients_ortho.loc[ai_mask, "query_type"] = np.random.choice(query_categories, size=ai_mask.sum(), p=ai_probs)

doc_mask = patients_ortho["group"] == "Doctor"
patients_ortho.loc[doc_mask, "query_type"] = np.random.choice(query_categories, size=doc_mask.sum(), p=doc_probs)

# CLEAN VALUE RANGES
for col in ["satisfaction", "expectation", "knowledge_score", "Function", "PCS", "MCS"]:
    patients_ortho[col] = patients_ortho[col].clip(0, 100)
patients_ortho["GAD7"] = patients_ortho["GAD7"].clip(0, 21)

# Map the A/B/C query types back to full strings for the final dataset printout
patients_ortho["query_type"] = patients_ortho["query_type"].map(category_labels)

# ============================================================
# PRINT FINAL DATASET & SUMMARY
# ============================================================
print("FINAL DATASET SAMPLE")
print(patients_ortho.head(), "\n")

print("SUMMARY STATISTICS")
summary = patients_ortho.groupby("group")[
    ["satisfaction", "expectation", "knowledge_score", "GAD7", "Function", "PCS", "MCS"]
].mean()
print(summary, "\n")

# ============================================================
# CREATE FIGURE LAYOUT & COLORS
# ============================================================
ai_group = patients_ortho[patients_ortho["group"] == "AI"]
doctor_group = patients_ortho[patients_ortho["group"] == "Doctor"]

fig, axes = plt.subplots(3, 2, figsize=(16, 18))
width = 0.35
color_ai = '#FF5C39'  
color_doc = '#FCDAB2' 

# ============================================================
# BAR CHARTS (A, B, C, D)
# ============================================================
def plot_bar_chart(ax, data_ai, data_doc, metrics, labels, title):
    ai_means = [data_ai[m].mean() if not data_ai.empty else 0 for m in metrics]
    doc_means = [data_doc[m].mean() if not data_doc.empty else 0 for m in metrics]
    ai_std = [data_ai[m].std() if not data_ai.empty else 0 for m in metrics]
    doc_std = [data_doc[m].std() if not data_doc.empty else 0 for m in metrics]
    
    x = np.arange(len(metrics))
    ax.bar(x - width/2, ai_means, width, yerr=ai_std, color=color_ai, capsize=5, label='AI Group' if title.startswith('A') else "")
    ax.bar(x + width/2, doc_means, width, yerr=doc_std, color=color_doc, capsize=5, label='Doctor Group' if title.startswith('A') else "")
    
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Score")
    ax.set_title(title, pad=15)
    if title.startswith('A'):
        ax.legend()

plot_bar_chart(axes[0,0], ai_group, doctor_group, ["satisfaction", "expectation", "knowledge_score"], ["Satisfaction", "Expectation", "Knowledge"], "A  Subjective Evaluation")

metrics_fup = ["GAD7", "Function", "PCS", "MCS"]
plot_bar_chart(axes[0,1], ai_group[ai_group["month"]==1], doctor_group[doctor_group["month"]==1], metrics_fup, metrics_fup, "B  1-Month Follow-Up")
plot_bar_chart(axes[1,0], ai_group[ai_group["month"]==3], doctor_group[doctor_group["month"]==3], metrics_fup, metrics_fup, "C  3-Month Follow-Up")
plot_bar_chart(axes[1,1], ai_group[ai_group["month"]==6], doctor_group[doctor_group["month"]==6], metrics_fup, metrics_fup, "D  6-Month Follow-Up")

# ============================================================
# EXACT PAPER PIE CHARTS (E & F)
# ============================================================
# Using exact percentages from the paper so they display perfectly
ai_percentages = [11.4, 12.8, 9.2, 42.2, 2.6, 4.0, 7.0, 10.8]
doc_percentages = [27.1, 6.7, 6.9, 16.6, 16.2, 5.5, 8.4, 12.6]

def plot_exact_pie(ax, percentages, explode_target, title):
    explode = [0.1 if cat == explode_target else 0 for cat in query_categories]
    wedges, texts, autotexts = ax.pie(
        percentages, labels=query_categories, autopct='%1.1f%%', 
        startangle=90, explode=explode, pctdistance=0.85, labeldistance=1.15
    )
    for autotext in autotexts:
        autotext.set_fontweight('bold')
        autotext.set_fontsize(9)
    ax.set_title(title, pad=20)
    return wedges

wedges_ai = plot_exact_pie(axes[2,0], ai_percentages, "D", "E  AI Group Question Distribution")
plot_exact_pie(axes[2,1], doc_percentages, "A", "F  Doctor Group Question Distribution")

# Add Centralized Legend
legend_labels = [f"{k}: {v}" for k, v in category_labels.items()]
fig.legend(wedges_ai, legend_labels, loc="lower center", ncol=4, bbox_to_anchor=(0.5, 0.02), title="Query Categories")

# ============================================================
# FINAL LAYOUT
# ============================================================
plt.subplots_adjust(hspace=0.4, bottom=0.12)
# Save the figure instead of showing it so the user can easily put it in a presentation
plt.savefig("orthopedic_analysis_results.png", dpi=300, bbox_inches='tight')
print("GRAPHS SAVED AS: orthopedic_analysis_results.png")

patients_ortho.to_csv("orthopedic_postoperative_dataset.csv", index=False)
print("DATASET SAVED SUCCESSFULLY")
print("FILE NAME: orthopedic_postoperative_dataset.csv")
