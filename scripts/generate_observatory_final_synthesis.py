#!/usr/bin/env python3
"""
================================================================================
BLOC-RELOC-V2: DYNAMICS OBSERVATORY FINAL SYNTHESIS GENERATOR
================================================================================
Self-contained script that reads existing Dynamics Observatory reports, audits,
fingerprints, and correlations to assemble a comprehensive master synthesis document.

Execution:
  python3 scripts/generate_observatory_final_synthesis.py

Author: Bloc-Reloc Laboratory
================================================================================
"""

import sys
import datetime
import numpy as np
import pandas as pd
from pathlib import Path

# ------------------------------------------------------------------------------
# 1. PATH RESOLUTION & INPUT VALIDATION
# ------------------------------------------------------------------------------
SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parent.parent

OBSERVATORY_DIR = REPO_ROOT / 'results' / 'observatory'
EXEC_REPORT_DIR = OBSERVATORY_DIR / 'executive_report'
MECH_AUDIT_DIR = OBSERVATORY_DIR / 'mechanism_audit'
MECH_FP_DIR = OBSERVATORY_DIR / 'mechanism_fingerprint'
OUTPUT_DIR = OBSERVATORY_DIR / 'final_synthesis'

INPUT_EXEC_SUMMARY = EXEC_REPORT_DIR / 'EXECUTIVE_SUMMARY.md'
INPUT_PERF_RANK = EXEC_REPORT_DIR / 'performance_ranking.csv'
INPUT_DYN_RANK = EXEC_REPORT_DIR / 'dynamic_ranking.csv'
INPUT_MECH_PROFILE = MECH_AUDIT_DIR / 'mechanism_profile.csv'
INPUT_MECH_FP_CSV = MECH_FP_DIR / 'mechanism_fingerprint.csv'
INPUT_MECH_FP_MD = MECH_FP_DIR / 'MECHANISM_FINGERPRINT_REPORT.md'
INPUT_PERF_CORR = OBSERVATORY_DIR / 'performance_dynamics_correlations.csv'

REQUIRED_INPUTS = {
    'EXECUTIVE_SUMMARY.md': INPUT_EXEC_SUMMARY,
    'performance_ranking.csv': INPUT_PERF_RANK,
    'dynamic_ranking.csv': INPUT_DYN_RANK,
    'mechanism_profile.csv': INPUT_MECH_PROFILE,
    'mechanism_fingerprint.csv': INPUT_MECH_FP_CSV,
    'MECHANISM_FINGERPRINT_REPORT.md': INPUT_MECH_FP_MD,
    'performance_dynamics_correlations.csv': INPUT_PERF_CORR
}

OUT_SYNTHESIS_MD = OUTPUT_DIR / 'BLOC_RELOC_V2_FINAL_SYNTHESIS.md'
OUT_METADATA_TXT = OUTPUT_DIR / 'FINAL_SYNTHESIS_METADATA.txt'

SCRIPT_VERSION = "1.0.0"

# ==============================================================================
# MAIN EXECUTOR
# ==============================================================================
def main():
    # 1. Validate required inputs
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

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 2. Read inputs
    df_perf_rank = pd.read_csv(INPUT_PERF_RANK)
    df_dyn_rank = pd.read_csv(INPUT_DYN_RANK)
    df_mech_profile = pd.read_csv(INPUT_MECH_PROFILE)
    df_mech_fp = pd.read_csv(INPUT_MECH_FP_CSV)
    df_perf_corr = pd.read_csv(INPUT_PERF_CORR)

    num_configurations = len(df_mech_fp['configuration'].unique())

    # --------------------------------------------------------------------------
    # 3. BUILD MARKDOWN FINAL SYNTHESIS
    # --------------------------------------------------------------------------
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    md_synthesis = f"""# BLOC-RELOC v2 DYNAMICS OBSERVATORY
# FINAL SYNTHESIS

**Generated:** {now_str}  
**Document Version:** {SCRIPT_VERSION}  

---

## 1. Experimental scope

- **Configurations Analyzed:** {num_configurations}
- **Data Scope:** This final synthesis is compiled strictly using previously computed artifact outputs from the Dynamics Observatory (including executive reports, mechanism profiles, dynamic rankings, and correlation matrices). No new experimental runs, algorithm modifications, parameter adjustments, or metric recalculations were performed.

---

## 2. Performance landscape

Ordered by partition quality (`mean_final_edge_cut` ascending):

| configuration | quality_rank | mean_final_edge_cut |
|:---|:---:|:---:|
"""
    # Sort by rank or cut ascending
    if 'rank' in df_perf_rank.columns:
        df_perf_sorted = df_perf_rank.sort_values(by='rank', ascending=True)
    else:
        df_perf_sorted = df_perf_rank.sort_values(by='mean_final_edge_cut', ascending=True)

    for idx, r in df_perf_sorted.iterrows():
        rank_val = r['rank'] if 'rank' in r else (idx + 1)
        md_synthesis += f"| **{r['configuration']}** | {int(rank_val)} | {r['mean_final_edge_cut']:.4f} |\n"

    md_synthesis += """
---

## 3. Dynamic behavior landscape

Summary of persistence and search activity metrics across configurations:

| configuration | dynamic_rank | time_to_survival_50 | extinction_time | total_avalanches |
|:---|:---:|:---:|:---:|:---:|
"""
    if 'rank_dynamic' in df_dyn_rank.columns:
        df_dyn_sorted = df_dyn_rank.sort_values(by='rank_dynamic', ascending=True)
    else:
        df_dyn_sorted = df_dyn_rank.sort_values(by=['time_to_survival_50', 'extinction_time'], ascending=[False, False])

    for idx, r in df_dyn_sorted.iterrows():
        dyn_rank = r['rank_dynamic'] if 'rank_dynamic' in r else (idx + 1)
        md_synthesis += f"| **{r['configuration']}** | {int(dyn_rank)} | {r['time_to_survival_50']} | {r['extinction_time']} | {int(r['total_avalanches'])} |\n"

    md_synthesis += """
---

## 4. Mechanism fingerprints

Compact behavioral fingerprint representation and vector classification:

| configuration | mechanism_class | quality_score | persistence_score | exploration_score | balance_score | mechanism_vector |
|:---|:---:|:---:|:---:|:---:|:---:|:---|
"""
    for _, r in df_mech_fp.iterrows():
        md_synthesis += f"| **{r['configuration']}** | `{r['mechanism_class']}` | {r['quality_score']:.4f} | {r['persistence_score']:.4f} | {r['exploration_score']:.4f} | {r['balance_score']:.4f} | `{r['mechanism_vector']}` |\n"

    md_synthesis += """
---

## 5. Emergent behavioral regimes

Behavioral groups categorized strictly by observed quantitative metrics:

### Premature-convergent
"""
    prem_df = df_mech_fp[df_mech_fp['mechanism_class'] == 'Premature-convergent']
    if not prem_df.empty:
        for _, r in prem_df.iterrows():
            md_synthesis += f"- **{r['configuration']}**:\n"
            md_synthesis += f"  - Persistence: Low (persistence_score: {r['persistence_score']:.4f}, dynamic_lifetime: {r['dynamic_lifetime']})\n"
            md_synthesis += f"  - Dynamic Activity: Low (avalanche_activity: {r['avalanche_activity']}, exploration_score: {r['exploration_score']:.4f})\n"
            md_synthesis += f"  - Final Quality: quality_score {r['quality_score']:.4f}\n"
    else:
        md_synthesis += "- No configurations assigned to this regime.\n"

    md_synthesis += """
### Balanced
"""
    bal_df = df_mech_fp[df_mech_fp['mechanism_class'] == 'Balanced']
    if not bal_df.empty:
        for _, r in bal_df.iterrows():
            md_synthesis += f"- **{r['configuration']}**:\n"
            md_synthesis += f"  - Persistence: Moderate/High (persistence_score: {r['persistence_score']:.4f}, dynamic_lifetime: {r['dynamic_lifetime']})\n"
            md_synthesis += f"  - Dynamic Activity: Sustained (avalanche_activity: {r['avalanche_activity']}, exploration_score: {r['exploration_score']:.4f})\n"
            md_synthesis += f"  - Final Quality: High (quality_score {r['quality_score']:.4f})\n"
    else:
        md_synthesis += "- No configurations assigned to this regime.\n"

    md_synthesis += """
---

## 6. Main trade-offs observed

The empirical data highlights key behavioral patterns across the benchmarked configurations:

- **Quality vs Exploration:** An empirical pattern indicates that elevated phase-space exploration does not unilaterally correspond to improved final partition quality. An observed association suggests that targeted local reconfigurations can achieve high quality without excessive total avalanches.
- **Persistence vs Convergence:** An empirical pattern shows that extended dynamic lifetime (higher extinction time) prevents premature search termination. Configurations exhibiting early dynamic extinction demonstrate a strong observed association with premature convergence to sub-optimal local basins.
- **Avalanche Activity vs Final Solution Quality:** An empirical pattern reveals that higher avalanche frequency reflects sustained search mobility, but the structural effectiveness of moves dictates whether activity translates into lower final edge cut values.

---

## 7. Top empirical observations

Top 10 absolute correlations extracted between dynamic variables and optimization performance:

| dynamic_variable | performance_variable | pearson_r | spearman_rho |
|:---|:---|:---:|:---:|
"""
    df_corr_work = df_perf_corr.copy()
    if 'spearman_rho' in df_corr_work.columns:
        df_corr_work['abs_spearman'] = df_corr_work['spearman_rho'].abs()
    else:
        df_corr_work['abs_spearman'] = df_corr_work['pearson_r'].abs()
        df_corr_work['spearman_rho'] = df_corr_work['pearson_r']

    if 'pearson_r' in df_corr_work.columns:
        df_corr_work['abs_pearson'] = df_corr_work['pearson_r'].abs()
    else:
        df_corr_work['abs_pearson'] = df_corr_work['abs_spearman']

    df_corr_sorted = df_corr_work.sort_values(by=['abs_spearman', 'abs_pearson'], ascending=[False, False]).head(10)

    for _, r in df_corr_sorted.iterrows():
        p_val = f"{r['pearson_r']:.4f}" if 'pearson_r' in r and pd.notna(r['pearson_r']) else "N/A"
        s_val = f"{r['spearman_rho']:.4f}" if 'spearman_rho' in r and pd.notna(r['spearman_rho']) else "N/A"
        md_synthesis += f"| `{r['dynamic_variable']}` | `{r['performance_variable']}` | {p_val} | {s_val} |\n"

    md_synthesis += """
---

## 8. Limitations

- Analysis limited to 6 tested configurations.
- Correlations are exploratory and do not establish causality.
- Mechanism classes are descriptive labels derived from normalized metrics.
- Results summarize observed behavior within the benchmark suite.

================================================================================
*BLOC-RELOC v2 Final Synthesis Document*
"""

    with open(OUT_SYNTHESIS_MD, 'w', encoding='utf-8') as f:
        f.write(md_synthesis)

    # --------------------------------------------------------------------------
    # 4. BUILD METADATA FILE
    # --------------------------------------------------------------------------
    metadata_content = f"""BLOC-RELOC V2 FINAL SYNTHESIS METADATA
================================================
Timestamp: {now_str}
Script Version: {SCRIPT_VERSION}
Number of Configurations: {num_configurations}

Input Files Used:
- {INPUT_EXEC_SUMMARY.relative_to(REPO_ROOT)}
- {INPUT_PERF_RANK.relative_to(REPO_ROOT)}
- {INPUT_DYN_RANK.relative_to(REPO_ROOT)}
- {INPUT_MECH_PROFILE.relative_to(REPO_ROOT)}
- {INPUT_MECH_FP_CSV.relative_to(REPO_ROOT)}
- {INPUT_MECH_FP_MD.relative_to(REPO_ROOT)}
- {INPUT_PERF_CORR.relative_to(REPO_ROOT)}
================================================
"""

    with open(OUT_METADATA_TXT, 'w', encoding='utf-8') as f:
        f.write(metadata_content)

    # --------------------------------------------------------------------------
    # 5. TERMINAL OUTPUT
    # --------------------------------------------------------------------------
    print("================================================")
    print("FINAL SYNTHESIS COMPLETE")
    print("================================================")
    print("\nSTATUS: SUCCESS\n")
    print("Generated:")
    print("  - BLOC_RELOC_V2_FINAL_SYNTHESIS.md")
    print("  - FINAL_SYNTHESIS_METADATA.txt")
    print("================================================\n")

if __name__ == '__main__':
    main()
