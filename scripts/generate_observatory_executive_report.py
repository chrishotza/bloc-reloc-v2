#!/usr/bin/env python3
"""
================================================================================
BLOC-RELOC-V2: DYNAMICS OBSERVATORY EXECUTIVE REPORT GENERATOR
================================================================================
Self-contained script that reads existing Dynamics Observatory audit results,
computes performance and dynamic rankings, extracts correlation highlights,
generates visualization plots, and outputs a comprehensive executive summary in
Markdown format.

Execution:
  python3 scripts/generate_observatory_executive_report.py

Author: Bloc-Reloc Laboratory
================================================================================
"""

import sys
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ------------------------------------------------------------------------------
# 1. REPOSITORY ROOT & PATH RESOLUTION
# ------------------------------------------------------------------------------
SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parent.parent

OBSERVATORY_DIR = REPO_ROOT / 'results' / 'observatory'
REPORT_DIR = OBSERVATORY_DIR / 'executive_report'

INPUT_DYN_REGIME = OBSERVATORY_DIR / 'dynamic_regime_summary.csv'
INPUT_PERF_AUDIT = OBSERVATORY_DIR / 'performance_dynamics_audit.csv'
INPUT_PERF_CORR = OBSERVATORY_DIR / 'performance_dynamics_correlations.csv'
INPUT_OBS_SUMMARY = OBSERVATORY_DIR / 'observatory_summary.csv'

REQUIRED_INPUTS = {
    'dynamic_regime_summary.csv': INPUT_DYN_REGIME,
    'performance_dynamics_audit.csv': INPUT_PERF_AUDIT,
    'performance_dynamics_correlations.csv': INPUT_PERF_CORR,
    'observatory_summary.csv': INPUT_OBS_SUMMARY
}

# Output targets
OUT_MD_REPORT = REPORT_DIR / 'EXECUTIVE_SUMMARY.md'
OUT_PERF_RANK = REPORT_DIR / 'performance_ranking.csv'
OUT_DYN_RANK = REPORT_DIR / 'dynamic_ranking.csv'
OUT_CORR_HIGHLIGHTS = REPORT_DIR / 'correlation_highlights.csv'

FIG_PERF_VS_SURV = REPORT_DIR / 'performance_vs_survival.png'
FIG_ACTIVITY_VS_QUAL = REPORT_DIR / 'dynamic_activity_vs_quality.png'

# ==============================================================================
# MAIN EXECUTOR & REPORT GENERATOR
# ==============================================================================

def main():
    # 1. Validate inputs
    missing = []
    for name, path in REQUIRED_INPUTS.items():
        if not path.exists():
            missing.append(f"{name} (expected at {path})")

    if missing:
        print("\n[FATAL ERROR] MISSING REQUIRED INPUT FILE(S):")
        for m in missing:
            print(f"  - {m}")
        print("\nExecution halted.")
        sys.exit(1)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    # 2. Read inputs
    df_dyn = pd.read_csv(INPUT_DYN_REGIME)
    df_audit = pd.read_csv(INPUT_PERF_AUDIT)
    df_corr = pd.read_csv(INPUT_PERF_CORR)
    df_obs = pd.read_csv(INPUT_OBS_SUMMARY)

    # Merge df_audit with df_dyn fallback to ensure all metrics exist safely
    df_audit_merged = df_audit.merge(
        df_dyn[['configuration', 'mean_delta', 'median_delta']], 
        on='configuration', 
        how='left', 
        suffixes=('', '_dyn')
    )
    if 'mean_delta' not in df_audit_merged.columns and 'mean_delta_dyn' in df_audit_merged.columns:
        df_audit_merged['mean_delta'] = df_audit_merged['mean_delta_dyn']
    if 'median_delta' not in df_audit_merged.columns and 'median_delta_dyn' in df_audit_merged.columns:
        df_audit_merged['median_delta'] = df_audit_merged['median_delta_dyn']

    # --------------------------------------------------------------------------
    # 3. Generate Rankings & Extracted Tables
    # --------------------------------------------------------------------------

    # --- Performance Ranking ---
    df_perf_rank = df_audit_merged[['configuration', 'mean_final_edge_cut']].copy()
    df_perf_rank.sort_values(by='mean_final_edge_cut', ascending=True, inplace=True)
    df_perf_rank['rank'] = range(1, len(df_perf_rank) + 1)
    df_perf_rank.to_csv(OUT_PERF_RANK, index=False)

    # --- Dynamic Ranking ---
    df_dyn_rank = df_dyn[['configuration', 'time_to_survival_50', 'extinction_time', 'total_avalanches']].copy()
    df_dyn_rank.sort_values(by=['time_to_survival_50', 'extinction_time', 'total_avalanches'], ascending=[False, False, False], inplace=True)
    df_dyn_rank['rank_dynamic'] = range(1, len(df_dyn_rank) + 1)
    df_dyn_rank.to_csv(OUT_DYN_RANK, index=False)

    # --- Correlation Highlights (Top 20 absolute correlations) ---
    df_corr_work = df_corr.copy()
    df_corr_work['abs_pearson'] = df_corr_work['pearson_r'].abs()
    df_corr_work['abs_spearman'] = df_corr_work['spearman_rho'].abs()
    df_corr_work.sort_values(by=['abs_pearson', 'abs_spearman'], ascending=[False, False], inplace=True)
    
    top_20_corr = df_corr_work.head(20).drop(columns=['abs_pearson', 'abs_spearman'])
    top_20_corr.to_csv(OUT_CORR_HIGHLIGHTS, index=False)

    # --------------------------------------------------------------------------
    # 4. Generate Visualizations (Matplotlib)
    # --------------------------------------------------------------------------
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

    # Figure 1: Performance vs Survival
    plt.figure(figsize=(8, 6))
    for _, row in df_audit_merged.iterrows():
        plt.scatter(row['time_to_survival_50'], row['mean_final_edge_cut'], s=120, label=row['configuration'])
        plt.annotate(row['configuration'], (row['time_to_survival_50'], row['mean_final_edge_cut']),
                     textcoords="offset points", xytext=(0, 8), ha='center', fontsize=9, weight='bold')

    plt.xlabel('Time to Survival 50% (Iterations)', fontsize=11, fontweight='bold')
    plt.ylabel('Mean Final Edge Cut (Lower is Better)', fontsize=11, fontweight='bold')
    plt.title('Performance vs Search Survival Duration', fontsize=13, fontweight='bold', pad=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(FIG_PERF_VS_SURV, dpi=300)
    plt.close()

    # Figure 2: Dynamic Activity vs Quality
    plt.figure(figsize=(8, 6))
    for _, row in df_audit_merged.iterrows():
        plt.scatter(row['total_avalanches'], row['mean_final_edge_cut'], s=120, color='crimson', alpha=0.8)
        plt.annotate(row['configuration'], (row['total_avalanches'], row['mean_final_edge_cut']),
                     textcoords="offset points", xytext=(0, 8), ha='center', fontsize=9, weight='bold')

    plt.xlabel('Total Avalanches Count', fontsize=11, fontweight='bold')
    plt.ylabel('Mean Final Edge Cut (Lower is Better)', fontsize=11, fontweight='bold')
    plt.title('Dynamic Search Activity vs Final Solution Quality', fontsize=13, fontweight='bold', pad=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(FIG_ACTIVITY_VS_QUAL, dpi=300)
    plt.close()

    # --------------------------------------------------------------------------
    # 5. Build Markdown Executive Report
    # --------------------------------------------------------------------------
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    num_configs = len(df_audit_merged)

    # Activity ranking (by total_avalanches descending)
    df_act_rank = df_audit_merged[['configuration', 'total_avalanches', 'mean_active_iterations', 'mean_delta', 'median_delta']].sort_values(
        by='total_avalanches', ascending=False
    )

    # Regime breakdown
    regime_summary = df_dyn[['configuration', 'best_relaxation_model', 'relaxation_regime']].to_dict('records')

    md_content = f"""# BLOC-RELOC V2 DYNAMICS OBSERVATORY
## EXECUTIVE SUMMARY REPORT

**Date of Execution:** {now_str}  
**Configurations Analyzed:** {num_configs}  

---

### 1. Performance Ranking (Solution Quality)
Ranked by `mean_final_edge_cut` (lower values indicate superior partition quality):

| Rank | Configuration | Mean Final Edge Cut | Std Edge Cut | Runtime (s) |
|:---:|:---|:---:|:---:|:---:|
"""
    for _, r in df_perf_rank.iterrows():
        audit_r = df_audit_merged[df_audit_merged['configuration'] == r['configuration']].iloc[0]
        md_content += f"| {r['rank']} | **{r['configuration']}** | {audit_r['mean_final_edge_cut']:.4f} | {audit_r['std_final_edge_cut']:.4f} | {audit_r['mean_runtime_sec']:.4f} |\n"

    md_content += """
---

### 2. Dynamic Survival Ranking
Ranked by search persistence (`time_to_survival_50` and `extinction_time`):

| Dynamic Rank | Configuration | Time to Survival 50% | Extinction Time | Survival t=5 | Survival t=10 | Survival t=15 |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|
"""
    for _, r in df_dyn_rank.iterrows():
        dyn_r = df_dyn[df_dyn['configuration'] == r['configuration']].iloc[0]
        md_content += f"| {r['rank_dynamic']} | **{r['configuration']}** | {dyn_r['time_to_survival_50']} | {dyn_r['extinction_time']} | {dyn_r['survival_t5']:.4f} | {dyn_r['survival_t10']:.4f} | {dyn_r['survival_t15']:.4f} |\n"

    md_content += """
---

### 3. Dynamic Search Activity Ranking
Ranked by total avalanche dynamics and exploration active iterations:

| Configuration | Total Avalanches | Mean Active Iterations | Mean Delta | Median Delta |
|:---|:---:|:---:|:---:|:---:|
"""
    for _, r in df_act_rank.iterrows():
        m_delta = f"{r['mean_delta']:.4f}" if pd.notna(r['mean_delta']) else "N/A"
        med_delta = f"{r['median_delta']:.4f}" if pd.notna(r['median_delta']) else "N/A"
        md_content += f"| **{r['configuration']}** | {int(r['total_avalanches'])} | {r['mean_active_iterations']:.2f} | {m_delta} | {med_delta} |\n"

    md_content += """
---

### 4. Relaxation Regime Classification
Summary of dynamic model fitting per configuration:

| Configuration | Best Relaxation Model | Relaxation Regime |
|:---|:---|:---|
"""
    for item in regime_summary:
        md_content += f"| **{item['configuration']}** | {item['best_relaxation_model']} | `{item['relaxation_regime']}` |\n"

    md_content += """
---

### 5. Key Correlation Highlights
Top correlation pairs extracted between dynamic variables and optimization performance:

| Dynamic Variable | Performance Variable | Pearson r | Spearman rho |
|:---|:---|:---:|:---:|
"""
    for _, r in top_20_corr.head(10).iterrows():
        md_content += f"| `{r['dynamic_variable']}` | `{r['performance_variable']}` | {r['pearson_r']:.4f} | {r['spearman_rho']:.4f} |\n"

    md_content += """
---

### 6. Generated Visual Artifacts
- **Performance vs Survival:** `results/observatory/executive_report/performance_vs_survival.png`
- **Activity vs Quality:** `results/observatory/executive_report/dynamic_activity_vs_quality.png`

================================================================================
*Report generated automatically by `generate_observatory_executive_report.py`*
"""

    with open(OUT_MD_REPORT, 'w', encoding='utf-8') as f:
        f.write(md_content)

    print("================================================")
    print("OBSERVATORY EXECUTIVE REPORT COMPLETE")
    print("================================================")
    print("\nSTATUS: SUCCESS\n")
    print("Generated:")
    print("  - EXECUTIVE_SUMMARY.md")
    print("  - performance_ranking.csv")
    print("  - dynamic_ranking.csv")
    print("  - correlation_highlights.csv")
    print("  - figures")
    print("================================================\n")

if __name__ == '__main__':
    main()
