import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import os

# ============================================================
# 1. DATA GENERATION (Unified Master Cohort)
# ============================================================
print("--- INITIALIZING MASTER CLINICAL TRIAL DATASET ---")
np.random.seed(42)
n = 300 # Master cohort size

df = pd.DataFrame({"subject_id": range(1, n+1)})
df["group"] = np.random.choice(["AI", "Doctor"], size=n)
df["surgery_type"] = np.random.choice(["Sports Medicine", "Joint Replacement"], size=n)
df["age"] = np.random.randint(20, 85, size=n)
df["age_group"] = np.where(df["age"] < 45, "<45", ">=45")
df["month"] = np.random.choice([0, 1, 3, 6], size=n, p=[0.1, 0.3, 0.3, 0.3])

# Subjective Metrics (Discharge/Baseline)
def gen_subj(row):
    if row["group"] == "AI":
        return (np.random.normal(97.5, 2.5), np.random.normal(96, 2.5), np.random.normal(51, 6))
    return (np.random.normal(93, 4), np.random.normal(91.5, 4), np.random.normal(47.5, 6))

df[["satisfaction", "expectation", "knowledge_score"]] = pd.DataFrame(df.apply(gen_subj, axis=1).tolist(), index=df.index)

# Longitudinal Clinical Metrics
def gen_clin(row):
    m, grp = row["month"], row["group"]
    if m == 0: return (np.random.normal(19, 3), np.random.normal(45, 5), np.random.normal(40, 5), np.random.normal(45, 5))
    elif m == 1:
        if grp == "AI": return (np.random.normal(14.5, 2.5), np.random.normal(57, 6), np.random.normal(48, 5), np.random.normal(51, 5))
        return (np.random.normal(19.5, 3), np.random.normal(49, 6), np.random.normal(42, 5), np.random.normal(48, 5))
    elif m == 3:
        if grp == "AI": return (np.random.normal(11, 2), np.random.normal(68, 6), np.random.normal(58, 5), np.random.normal(56, 5))
        return (np.random.normal(14, 3), np.random.normal(63, 6), np.random.normal(53, 5), np.random.normal(54, 5))
    else: # Month 6
        if grp == "AI": return (np.random.normal(8.5, 2), np.random.normal(74, 5), np.random.normal(63, 4), np.random.normal(62, 4))
        return (np.random.normal(10.5, 2), np.random.normal(71, 5), np.random.normal(61, 4), np.random.normal(61, 4))

df[["GAD7", "function_general", "PCS", "MCS"]] = pd.DataFrame(df.apply(gen_clin, axis=1).tolist(), index=df.index)

# Specialized Scores
df["IKDC"] = np.nan; df["FJS"] = np.nan
df.loc[df["surgery_type"] == "Sports Medicine", "IKDC"] = df.loc[df["surgery_type"] == "Sports Medicine", "function_general"] + np.random.normal(0, 2, (df["surgery_type"] == "Sports Medicine").sum())
df.loc[df["surgery_type"] == "Joint Replacement", "FJS"] = df.loc[df["surgery_type"] == "Joint Replacement", "function_general"] + np.random.normal(0, 2, (df["surgery_type"] == "Joint Replacement").sum())

# Query Types (Using correct probabilities)
query_categories = ["A", "B", "C", "D", "E", "F", "G", "H"]
cat_labels = {"A": "Symptom consultation", "B": "Surgical information", "C": "Postoperative care", "D": "Postoperative recovery", "E": "Medication consultation", "F": "Complications", "G": "Lifestyle recommendations", "H": "Other"}
ai_probs = [0.114, 0.128, 0.092, 0.422, 0.026, 0.040, 0.070, 0.108]
doc_probs = [0.271, 0.067, 0.069, 0.166, 0.162, 0.055, 0.084, 0.126]
df["query_type"] = np.where(df["group"] == "AI", np.random.choice(query_categories, size=n, p=ai_probs), np.random.choice(query_categories, size=n, p=doc_probs))

# Performance Metrics
df["response_time_min"] = np.where(df["group"] == "AI", np.random.normal(0.5, 0.2, n), np.random.normal(358, 40, n))
df["accuracy"] = np.where(df["group"] == "AI", np.random.normal(93.9, 1, n), np.random.normal(98.1, 0.5, n))

# Cleaning
for c in ["satisfaction", "expectation", "knowledge_score", "function_general", "PCS", "MCS", "IKDC", "FJS", "accuracy"]: df[c] = df[c].clip(0, 100)
df["GAD7"] = df["GAD7"].clip(0, 21)
df["response_time_min"] = df["response_time_min"].clip(0.1, 1000)

df.to_csv("orthopedic_master_dataset.csv", index=False)
print("SUCCESS: Unified dataset saved to orthopedic_master_dataset.csv\n")

# ============================================================
# 2. STATISTICAL ANALYSIS (Table Generation)
# ============================================================
print("--- CALCULATING STATISTICAL METRICS ---")
stats_res = []
def add_stat(name, data_ai, data_doc):
    t, p = stats.ttest_ind(data_ai.dropna(), data_doc.dropna())
    stats_res.append({"Metric": name, "AI Mean": f"{data_ai.mean():.2f}", "Doc Mean": f"{data_doc.mean():.2f}", "P-value": f"{p:.4f}" if p >= 0.001 else "<0.001"})

add_stat("Satisfaction", df[df["group"] == "AI"]["satisfaction"], df[df["group"] == "Doctor"]["satisfaction"])
add_stat("Expectation", df[df["group"] == "AI"]["expectation"], df[df["group"] == "Doctor"]["expectation"])
add_stat("Knowledge Score", df[df["group"] == "AI"]["knowledge_score"], df[df["group"] == "Doctor"]["knowledge_score"])

# Longitudinal Outcomes at Month 6
m6 = df[df["month"] == 6]
add_stat("GAD7 (Month 6)", m6[m6["group"] == "AI"]["GAD7"], m6[m6["group"] == "Doctor"]["GAD7"])
add_stat("Function (Month 6)", m6[m6["group"] == "AI"]["function_general"], m6[m6["group"] == "Doctor"]["function_general"])
add_stat("PCS (Month 6)", m6[m6["group"] == "AI"]["PCS"], m6[m6["group"] == "Doctor"]["PCS"])
add_stat("MCS (Month 6)", m6[m6["group"] == "AI"]["MCS"], m6[m6["group"] == "Doctor"]["MCS"])

# Efficiency and Performance
add_stat("Response Time (min)", df[df["group"] == "AI"]["response_time_min"], df[df["group"] == "Doctor"]["response_time_min"])
add_stat("Accuracy (%)", df[df["group"] == "AI"]["accuracy"], df[df["group"] == "Doctor"]["accuracy"])
pd.DataFrame(stats_res).to_csv("master_metrics_summary.csv", index=False)

# ============================================================
# 3. VISUALIZATION (Figures 1-6)
# ============================================================
color_ai, color_doc = '#FF5C39', '#FCDAB2'

# Figure 2: Longitudinal
fig2, axes = plt.subplots(2, 2, figsize=(12, 10))
mets = ["GAD7", "function_general", "PCS", "MCS"]
for i, m in enumerate(mets):
    ax = axes[i//2, i%2]; ax.grid(True, alpha=0.3)
    for g, c, l in [("AI", color_ai, "AI"), ("Doctor", color_doc, "Doc")]:
        means = [df[(df["group"] == g) & (df["month"] == t)][m].mean() for t in [0, 1, 3, 6]]
        ax.plot([0, 1, 3, 6], means, '-o', color=c, label=l)
    ax.set_title(m); ax.legend()
fig2.tight_layout(); fig2.savefig("fig2_longitudinal.png", dpi=200)

# Figure 3: Pie Charts (Calculated)
fig3, axes = plt.subplots(1, 2, figsize=(14, 6))
for i, g in enumerate(["AI", "Doctor"]):
    counts = df[df["group"] == g]["query_type"].value_counts().reindex(query_categories, fill_value=0)
    axes[i].pie(counts, labels=query_categories, autopct='%1.1f%%', startangle=90, colors=plt.cm.Pastel1.colors)
    axes[i].set_title(f"Figure 3: {g} Question Distribution")
fig3.savefig("fig3_distributions.png", dpi=200)

# Figure 4 & 5: Subgroups
for fnum, stype, score in [(4, "Sports Medicine", "IKDC"), (5, "Joint Replacement", "FJS")]:
    sub = df[df["surgery_type"] == stype]
    fig, axes = plt.subplots(1, 4, figsize=(20, 5))
    # Subjective
    ax = axes[0]; ai_s = sub[sub["group"] == "AI"]; doc_s = sub[sub["group"] == "Doctor"]
    ax.bar([0, 1, 2], [ai_s["satisfaction"].mean(), ai_s["expectation"].mean(), ai_s["knowledge_score"].mean()], 0.35, color=color_ai, label="AI")
    ax.bar([0.35, 1.35, 2.35], [doc_s["satisfaction"].mean(), doc_s["expectation"].mean(), doc_s["knowledge_score"].mean()], 0.35, color=color_doc, label="Doc")
    ax.set_xticks([0.17, 1.17, 2.17]); ax.set_xticklabels(["Sat", "Exp", "Know"]); ax.set_title("Subjective")
    # Months
    for i, m in enumerate([1, 3, 6]):
        ax = axes[i+1]; ai_m = ai_s[ai_s["month"] == m]; doc_m = doc_s[doc_s["month"] == m]
        ax.bar([0, 1], [ai_m[score].mean() if not ai_m.empty else 0, ai_m["GAD7"].mean() if not ai_m.empty else 0], 0.35, color=color_ai)
        ax.bar([0.35, 1.35], [doc_m[score].mean() if not doc_m.empty else 0, doc_m["GAD7"].mean() if not doc_m.empty else 0], 0.35, color=color_doc)
        ax.set_xticks([0.17, 1.17]); ax.set_xticklabels([score, "GAD7"]); ax.set_title(f"Month {m}")
    fig.tight_layout(); fig.savefig(f"fig{fnum}_{stype.replace(' ', '_')}.png", dpi=200)

# Figure 6: Age Subgroups Trajectory
fig6, axes6 = plt.subplots(1, 2, figsize=(14, 6))
traj_mets = ["GAD7", "function_general"]
for i, met in enumerate(traj_mets):
    ax = axes6[i]; ax.grid(True, alpha=0.3)
    for grp, age, lbl, clr, ls in [("AI", "<45", "AI <45", color_ai, "-"), ("AI", ">=45", "AI >=45", color_ai, "--"), ("Doctor", "<45", "Doc <45", color_doc, "-"), ("Doctor", ">=45", "Doc >=45", color_doc, "--")]:
        subset = df[(df["group"] == grp) & (df["age_group"] == age)]
        means = [subset[subset["month"] == m][met].mean() for m in [0, 1, 3, 6]]
        ax.plot([0, 1, 3, 6], means, label=lbl, color=clr, linestyle=ls, marker='o')
    ax.set_title(f"Figure 6: {met} Trajectory by Age")
    ax.legend(fontsize='small')
fig6.savefig("fig6_age_trajectories.png", dpi=200)

print("--- ALL FIGURES GENERATED SUCCESSFULLY ---")
