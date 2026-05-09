import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# DATA GENERATION FOR FIGURES 4, 5, 6
# ============================================================
print("GENERATING SYNTHETIC SUBGROUP DATASET...\n")

np.random.seed(42)
n = 400 # Larger sample for subgroup analysis
patients = pd.DataFrame({"subject_id": range(1, n+1)})

# Demographic & Surgery Assignment
patients["group"] = np.random.choice(["AI", "Doctor"], size=n)
patients["surgery_type"] = np.random.choice(["Sports Medicine", "Joint Replacement"], size=n)
patients["age"] = np.random.randint(20, 80, size=n)
patients["age_group"] = np.where(patients["age"] < 45, "<45", ">=45")

# Month assignment (0, 1, 3, 6)
# For cross-sectional visualization, we'll assign each patient to a follow-up point
patients["month"] = np.random.choice([0, 1, 3, 6], size=n, p=[0.1, 0.3, 0.3, 0.3])

# Subjective Metrics (Discharge - effectively Month 0 subjective)
def generate_subjective(row):
    # AI group generally higher
    if row["group"] == "AI":
        return (np.random.normal(97, 3), np.random.normal(95, 3), np.random.normal(52, 5))
    else:
        return (np.random.normal(92, 4), np.random.normal(91, 4), np.random.normal(47, 5))

subj_applied = patients.apply(generate_subjective, axis=1)
patients[["satisfaction", "expectation", "knowledge_score"]] = pd.DataFrame(subj_applied.tolist(), index=patients.index)

# Longitudinal Clinical Metrics
def generate_clinical(row):
    m = row["month"]
    grp = row["group"]
    
    # Base values that improve over time
    # GAD7 (Anxiety) - Decreases over time
    # Function Scores - Increase over time
    # PCS/MCS - Increase over time
    
    if m == 0:
        gad = np.random.normal(18, 3) if grp == "AI" else np.random.normal(21, 3)
        func = np.random.normal(45, 5)
        pcs = np.random.normal(40, 5)
        mcs = np.random.normal(45, 5)
    elif m == 1:
        gad = np.random.normal(15, 3) if grp == "AI" else np.random.normal(19, 3)
        func = np.random.normal(55, 6) if grp == "AI" else np.random.normal(50, 6)
        pcs = np.random.normal(48, 5) if grp == "AI" else np.random.normal(43, 5)
        mcs = np.random.normal(50, 5) if grp == "AI" else np.random.normal(48, 5)
    elif m == 3:
        gad = np.random.normal(11, 2) if grp == "AI" else np.random.normal(14, 3)
        func = np.random.normal(68, 6) if grp == "AI" else np.random.normal(63, 6)
        pcs = np.random.normal(58, 5) if grp == "AI" else np.random.normal(54, 5)
        mcs = np.random.normal(56, 5) if grp == "AI" else np.random.normal(55, 5)
    else: # Month 6
        gad = np.random.normal(8, 2) if grp == "AI" else np.random.normal(10, 2)
        func = np.random.normal(74, 5) if grp == "AI" else np.random.normal(72, 5)
        pcs = np.random.normal(64, 4) if grp == "AI" else np.random.normal(62, 4)
        mcs = np.random.normal(62, 4) if grp == "AI" else np.random.normal(61, 4)
        
    return (gad, func, pcs, mcs)

clin_applied = patients.apply(generate_clinical, axis=1)
patients[["GAD7", "function_aggregated", "PCS", "MCS"]] = pd.DataFrame(clin_applied.tolist(), index=patients.index)

# Specific Scores for Subgroups
# IKDC for Sports, FJS for Joint
patients["IKDC"] = np.nan
patients["FJS"] = np.nan
sports_mask = patients["surgery_type"] == "Sports Medicine"
joint_mask = patients["surgery_type"] == "Joint Replacement"

# Reuse the aggregated function score but add some noise for variety
patients.loc[sports_mask, "IKDC"] = patients.loc[sports_mask, "function_aggregated"] + np.random.normal(0, 2, sports_mask.sum())
patients.loc[joint_mask, "FJS"] = patients.loc[joint_mask, "function_aggregated"] + np.random.normal(0, 2, joint_mask.sum())

# Clean ranges
cols_100 = ["satisfaction", "expectation", "knowledge_score", "function_aggregated", "PCS", "MCS", "IKDC", "FJS"]
for c in cols_100:
    patients[c] = patients[c].clip(0, 100)
patients["GAD7"] = patients["GAD7"].clip(0, 21)

# ============================================================
# HELPER PLOTTING FUNCTION
# ============================================================
color_ai = '#FF5C39'
color_doc = '#FCDAB2'
width = 0.35

def plot_subgroup_metrics(axes_row, df, subgroup_name, func_col_name):
    ai_df = df[df["group"] == "AI"]
    doc_df = df[df["group"] == "Doctor"]
    
    # Panel A: Subjective
    ax0 = axes_row[0]
    metrics_a = ["satisfaction", "expectation", "knowledge_score"]
    labels_a = ["Satisfaction", "Expectation", "Knowledge"]
    x = np.arange(len(metrics_a))
    ax0.bar(x - width/2, [ai_df[m].mean() for m in metrics_a], width, color=color_ai, label="AI", capsize=5, yerr=[ai_df[m].std()/2 for m in metrics_a])
    ax0.bar(x + width/2, [doc_df[m].mean() for m in metrics_a], width, color=color_doc, label="Doc", capsize=5, yerr=[doc_df[m].std()/2 for m in metrics_a])
    ax0.set_xticks(x)
    ax0.set_xticklabels(labels_a)
    ax0.set_title(f"A: Subjective ({subgroup_name})")
    ax0.legend()

    # Panel B, C, D: Months 1, 3, 6
    metrics_clin = ["GAD7", func_col_name, "PCS", "MCS"]
    for i, m in enumerate([1, 3, 6]):
        ax = axes_row[i+1]
        m_ai = ai_df[ai_df["month"] == m]
        m_doc = doc_df[doc_df["month"] == m]
        x = np.arange(len(metrics_clin))
        ax.bar(x - width/2, [m_ai[met].mean() if not m_ai.empty else 0 for met in metrics_clin], width, color=color_ai, capsize=3)
        ax.bar(x + width/2, [m_doc[met].mean() if not m_doc.empty else 0 for met in metrics_clin], width, color=color_doc, capsize=3)
        ax.set_xticks(x)
        ax.set_xticklabels(metrics_clin)
        ax.set_title(f"{chr(66+i)}: {m}-Month")

# ============================================================
# FIGURE 4: SPORTS MEDICINE
# ============================================================
fig4, axes4 = plt.subplots(1, 4, figsize=(20, 5))
plot_subgroup_metrics(axes4, patients[patients["surgery_type"] == "Sports Medicine"], "Sports Medicine", "IKDC")
plt.tight_layout()
fig4.savefig("figure4_sports_medicine.png", dpi=300)
print("SAVED: figure4_sports_medicine.png")

# ============================================================
# FIGURE 5: JOINT REPLACEMENT
# ============================================================
fig5, axes5 = plt.subplots(1, 4, figsize=(20, 5))
plot_subgroup_metrics(axes5, patients[patients["surgery_type"] == "Joint Replacement"], "Joint Replacement", "FJS")
plt.tight_layout()
fig5.savefig("figure5_joint_replacement.png", dpi=300)
print("SAVED: figure5_joint_replacement.png")

# ============================================================
# FIGURE 6: AGE SUBGROUPS
# ============================================================
fig6, axes6 = plt.subplots(2, 4, figsize=(20, 10))

# Fig 6 A-D: Subjective comparisons
# AI <45 vs AI >=45, Doc <45 vs Doc >=45, AI <45 vs Doc <45, AI >=45 vs Doc >=45
comparisons = [
    (patients[(patients["group"] == "AI") & (patients["age_group"] == "<45")], patients[(patients["group"] == "AI") & (patients["age_group"] == ">=45")], "AI: <45 vs >=45"),
    (patients[(patients["group"] == "Doctor") & (patients["age_group"] == "<45")], patients[(patients["group"] == "Doctor") & (patients["age_group"] == ">=45")], "Doc: <45 vs >=45"),
    (patients[(patients["group"] == "AI") & (patients["age_group"] == "<45")], patients[(patients["group"] == "Doctor") & (patients["age_group"] == "<45")], "AI vs Doc (<45)"),
    (patients[(patients["group"] == "AI") & (patients["age_group"] == ">=45")], patients[(patients["group"] == "Doctor") & (patients["age_group"] == ">=45")], "AI vs Doc (>=45)")
]

for i, (df1, df2, title) in enumerate(comparisons):
    ax = axes6[0, i]
    metrics = ["satisfaction", "expectation", "knowledge_score"]
    x = np.arange(len(metrics))
    ax.bar(x - width/2, [df1[m].mean() for m in metrics], width, color=color_ai, label="Group 1")
    ax.bar(x + width/2, [df2[m].mean() for m in metrics], width, color=color_doc, label="Group 2")
    ax.set_xticks(x)
    ax.set_xticklabels(["Satisf", "Expect", "Knowl"])
    ax.set_title(title)

# Fig 6 E-H: Longitudinal trajectories (GAD7, Function, PCS, MCS)
traj_metrics = ["GAD7", "function_aggregated", "PCS", "MCS"]
traj_titles = ["E: GAD-7 Trajectory", "F: Function Trajectory", "G: PCS Trajectory", "H: MCS Trajectory"]
months = [0, 1, 3, 6]

for i, met in enumerate(traj_metrics):
    ax = axes6[1, i]
    # Plot 4 lines
    for (grp, age, lbl, clr, ls) in [
        ("AI", "<45", "AI <45", color_ai, "-"),
        ("AI", ">=45", "AI >=45", color_ai, "--"),
        ("Doctor", "<45", "Doc <45", color_doc, "-"),
        ("Doctor", ">=45", "Doc >=45", color_doc, "--")
    ]:
        subset = patients[(patients["group"] == grp) & (patients["age_group"] == age)]
        means = [subset[subset["month"] == m][met].mean() for m in months]
        ax.plot(months, means, label=lbl, color=clr, linestyle=ls, marker='o')
    ax.set_title(traj_titles[i])
    ax.set_xlabel("Month")
    ax.legend(fontsize='small')

plt.tight_layout()
fig6.savefig("figure6_age_subgroups.png", dpi=300)
print("SAVED: figure6_age_subgroups.png")

patients.to_csv("subgroup_analysis_dataset.csv", index=False)
print("DATASET SAVED: subgroup_analysis_dataset.csv")
