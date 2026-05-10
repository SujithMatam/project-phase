
### Install requirements: 
pip install pandas numpy matplotlib seaborn scipy tabulate<br>
python calculate_metrics.py<br>
python figure2_generation.py<br>
python analysis_subgroups.py<br>
python analysis.py<br>


python -c "import matplotlib; import os; <br>
print('Matplotlib location:', os.path.dirname(matplotlib.__file__)); <br>
print('Config directory:', matplotlib.get_configdir())



### MARKDOWN TABLE FOR REPORT:
| Metric              | AI Group (Mean ± SD)   | Doctor Group (Mean ± SD)   | P-value   |
|:--------------------|:-----------------------|:---------------------------|:----------|
| Satisfaction        | 98.01 ± 2.05           | 93.43 ± 3.87               | <0.001    |
| Expectation         | 95.94 ± 2.62           | 91.51 ± 4.34               | <0.001    |
| Knowledge_score     | 50.21 ± 6.58           | 47.89 ± 5.78               | 0.0230    |
| GAD7 (Month 6)      | 8.85 ± 2.20            | 10.35 ± 1.54               | 0.0252    |
| Function (Month 6)  | 73.05 ± 5.07           | 69.56 ± 3.87               | 0.0293    |
| PCS (Month 6)       | 62.63 ± 3.80           | 60.91 ± 3.19               | 0.1622    |
| MCS (Month 6)       | 63.17 ± 4.92           | 62.21 ± 3.07               | 0.4872    |
| Response Time (min) | 0.45 ± 0.19            | 358.71 ± 34.97             | <0.001    |
| Accuracy (%)        | 93.86 ± 1.02           | 98.14 ± 0.45               | <0.001    |

## 📊 Result Visualizations

### Figure 2: Longitudinal Outcomes (Total Cohort)
![Longitudinal Outcomes](figure2_longitudinal_outcomes.png)

### Figure 3: Subjective Evaluation and Question Distribution
![Analysis Results](orthopedic_analysis_results.png)

### Figure 4: Subgroup Analysis - Sports Medicine
![Sports Medicine](figure4_sports_medicine.png)

### Figure 5: Subgroup Analysis - Joint Replacement
![Joint Replacement](figure5_joint_replacement.png)

### Figure 6: Subgroup Analysis - Age Brackets (<45 vs ≥45)
![Age Analysis](figure6_age_subgroups.png)


# Unified Orthopedic Research Analysis

This folder contains a unified, consolidated version of the orthopedic postoperative care analysis. It is designed to match the workflow and data structure of a professional clinical trial research paper.

## 🚀 One-Script Execution
All analyses, data generation, and plotting are handled by a single master script:
```bash
python master_analysis.py
```

## 📂 Key Files
1.  **[master_analysis.py](master_analysis.py)**: The unified analysis engine.
2.  **[orthopedic_master_dataset.csv](orthopedic_master_dataset.csv)**: The master dataset containing all patients (N=300).
3.  **[master_metrics_summary.csv](master_metrics_summary.csv)**: Statistical results (Means & P-values).

## 📊 Result Previews
- **Figure 2**: Longitudinal recovery trajectories.
- **Figure 3**: Dynamic question distributions (AI vs Doctor).
- **Figure 4/5**: Surgery-specific analysis (Sports & Joint).
- **Figure 6**: Age-based recovery trajectories.

## 📋 Comprehensive Metrics Table
These results are calculated from the Master Dataset (AI vs. Doctor):

| Metric | AI Group (Mean) | Doctor Group (Mean) | P-value |
| :--- | :--- | :--- | :--- |
| **Satisfaction** | 97.39 | 93.40 | **<0.001** |
| **Expectation** | 95.58 | 91.31 | **<0.001** |
| **Knowledge Score** | 50.64 | 47.69 | **<0.001** |
| **GAD7 (Month 6)** | 7.83 | 10.73 | **<0.001** |
| **Function (Month 6)** | 74.78 | 71.59 | **0.0033** |
| **PCS (Month 6)** | 63.88 | 61.82 | **0.0276** |
| **MCS (Month 6)** | 61.27 | 61.83 | 0.5372 |
| **Response Time (min)** | 0.49 | 356.20 | **<0.001** |
| **Accuracy (%)** | 93.81 | 98.13 | **<0.001** |
