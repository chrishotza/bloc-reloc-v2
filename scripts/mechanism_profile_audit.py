#!/usr/bin/env python3
"""
================================================================================
BLOC-RELOC-V2: DYNAMIC MECHANISM PROFILE AUDIT
================================================================================
Self-contained script that constructs an interpretative dynamic profile for
each BLOC-RELOC v2 configuration using existing Dynamics Observatory outputs.

Execution:
  python3 scripts/mechanism_profile_audit.py

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
# 1. PATH RESOLUTION & INPUT VALIDATION
# ------------------------------------------------------------------------------
SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parent.parent

OBSERVATORY_DIR = REPO_ROOT / 'results' / 'observatory'
OUTPUT_DIR = OBSERVATORY_DIR / 'mechanism_audit'

INPUT_DYN_REGIME = OBSERVATORY_DIR / 'dynamic_regime_summary.csv'
INPUT_PERF_AUDIT = OBSERVATORY_DIR / 'performance_dynamics_audit.csv'
INPUT_PERF_CORR = OBSERVATORY_DIR / 'performance_dynamics_correlations.csv'
INPUT_TOPO_CORR = OBSERVATORY_DIR / 'topology_dynamics_correlation.csv'

REQUIRED_INPUTS = {
    'dynamic_regime_summary.csv': INPUT_DYN_REGIME,
    'performance_dynamics_audit.csv': INPUT_PERF_AUDIT,
    'performance_dynamics_correlations.csv': INPUT_PERF_CORR,
    'topology_dynamics_correlation.csv': INPUT_TOPO_CORR
}

# Output targets
OUT_PROFILE_CSV = OUTPUT_DIR / 'mechanism_profile.csv'
OUT_TRADEOFF_CSV = OUTPUT_DIR / 'tradeoff_analysis.csv'
OUT_TOPO_LINKS_CSV = OUTPUT_DIR / 'topology_mechanism_links.csv'
OUT_MD_REPORT = OUTPUT_DIR / 'MECHANISM_AUDIT_REPORT.md'

FIG_TRADEOFF = OUTPUT_DIR / 'mechanism_tradeoff.png'
FIG_EXPL_QUAL = OUTPUT_DIR / 'exploration_vs_quality.png'

# ------------------------------------------------------------------------------
# HELPER: MIN-MAX NORMALIZER (PURE NUMPY)
# ------------------------------------------------------------------------------
def min_max_scale(series, invert=False):
    s = series.astype(float).values
    min_val, max_val = np.nanmin(s), np.nanmax(s)
    if max_val == min_val:
        scaled = np.ones_like(s) * 0.5
    else:
        scaled = (s - min_val) / (max_val - min_val)
    
    if invert:
        scaled = 1.0 - scaled
    return scaled


# ==============================================================================
# MAIN EXECUTOR & AUDIT GENERATION
# ==============================================================================

def main():
    # 1. Validate existence of required CSVs
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
    df_dyn = pd.read_csv(INPUT_DYN_REGIME)
    df_audit = pd.read_csv(INPUT_PERF_AUDIT)
    df_topo = pd.read_csv(INPUT_TOPO_CORR)

    # Merge audit and dyn summary safely avoiding suffix collisions
    df_merged = df_audit.merge(
        df_dyn, 
        on='configuration', 
        how='left',
        suffixes=('', '_dyn')
    )

    # Robust column fallback resolution
    def resolve_col(df, primary, fallback, default_val=np.nan):
        if primary in df.columns:
            return df[primary]
        elif fallback in df.columns:
            return df[fallback]
        else:
            return pd.Series([default_val] * len(df))

    df_merged['mean_final_edge_cut_clean'] = resolve_col(df_merged, 'mean_final_edge_cut', 'final_edge_cut')
    df_merged['relaxation_regime_clean'] = resolve_col(df_merged, 'relaxation_regime', 'relaxation_regime_dyn', 'Unknown')
    df_merged['best_relaxation_model_clean'] = resolve_col(df_merged, 'best_relaxation_model', 'best_relaxation_model_dyn', 'Unknown')

    # --------------------------------------------------------------------------
    # 3. COMPUTE TRADEOFF ANALYSIS & NORMALIZED SCORES
    # --------------------------------------------------------------------------
    df_trade = df_merged[['configuration']].copy()

    # Solution Quality Score: lower edge cut is better -> inverted scaling
    quality_score = min_max_scale(df_merged['mean_final_edge_cut_clean'], invert=True)

    # Dynamic Persistence Score: higher extinction_time
    persistence_score = min_max_scale(df_merged['extinction_time'], invert=False)

    # Exploration Score: higher total_avalanches & mean_active_iterations
    aval_scaled = min_max_scale(df_merged['total_avalanches'], invert=False)
    act_scaled = min_max_scale(df_merged['mean_active_iterations'], invert=False)
    exploration_score = (aval_scaled + act_scaled) / 2.0

    # Overall Balance Score
    overall_balance_score = (quality_score + persistence_score + exploration_score) / 3.0

    df_trade['solution_quality_score'] = np.round(quality_score, 4)
    df_trade['dynamic_persistence_score'] = np.round(persistence_score, 4)
    df_trade['exploration_score'] = np.round(exploration_score, 4)
    df_trade['overall_balance_score'] = np.round(overall_balance_score, 4)

    df_trade.to_csv(OUT_TRADEOFF_CSV, index=False)

    # --------------------------------------------------------------------------
    # 4. COMPUTE MECHANISM PROFILE & ASSIGN MECHANISM CLASS
    # --------------------------------------------------------------------------
    df_prof = df_merged[['configuration']].copy()

    # Ranks (1 = best)
    df_prof['quality_rank'] = df_merged['mean_final_edge_cut_clean'].rank(method='min', ascending=True).astype(int)
    df_prof['dynamic_persistence_rank'] = df_merged['extinction_time'].rank(method='min', ascending=False).astype(int)
    df_prof['exploration_rank'] = df_merged['total_avalanches'].rank(method='min', ascending=False).astype(int)

    # Key Metrics
    df_prof['final_edge_cut'] = np.round(df_merged['mean_final_edge_cut_clean'], 4)
    df_prof['extinction_time'] = df_merged['extinction_time']
    df_prof['total_avalanches'] = df_merged['total_avalanches'].astype(int)
    df_prof['mean_active_iterations'] = np.round(df_merged['mean_active_iterations'], 4)
    df_prof['mean_delta'] = np.round(df_merged['mean_delta'], 4)
    df_prof['relaxation_regime'] = df_merged['relaxation_regime_clean']

    # Rule-Based Mechanism Classification
    classes = []
    for idx, row in df_trade.iterrows():
        q_sc = row['solution_quality_score']
        p_sc = row['dynamic_persistence_score']
        e_sc = row['exploration_score']

        # RULE DEFINITIONS FOR MECHANISM CLASSES:
        #
        # 1) Explorer: High dynamic persistence, high extinction_time, high total_avalanches, and high mean_active_iterations.
        #    Interpretation: "Configuración con búsqueda prolongada y alta actividad dinámica."
        #
        # 2) Balanced: Good final quality, medium/high persistence, and significant exploration.
        #    Interpretation: "Configuración con compromiso entre calidad final y dinámica de búsqueda."
        #
        # 3) Premature-convergent: Low extinction_time, few avalanches, few active iterations, and early dynamic extinction.
        #    Interpretation: "Configuración que converge tempranamente sin evidencia suficiente de exploración prolongada."

        if q_sc >= 0.5 and p_sc >= 0.5:
            m_class = 'Balanced'
        elif e_sc >= 0.6 or p_sc >= 0.6:
            m_class = 'Explorer'
        else:
            m_class = 'Premature-convergent'
        classes.append(m_class)

    df_prof['mechanism_class'] = classes
    df_prof.to_csv(OUT_PROFILE_CSV, index=False)

    # --------------------------------------------------------------------------
    # 5. TOPOLOGY MECHANISM LINKS
    # --------------------------------------------------------------------------
    df_topo_work = df_topo.copy()
    if 'spearman_rho' in df_topo_work.columns:
        df_topo_work['abs_spearman'] = df_topo_work['spearman_rho'].abs()
    elif 'abs_spearman' not in df_topo_work.columns and 'pearson_r' in df_topo_work.columns:
        df_topo_work['abs_spearman'] = df_topo_work['pearson_r'].abs()
        df_topo_work['spearman_rho'] = df_topo_work['pearson_r']

    df_topo_work.sort_values(by='abs_spearman', ascending=False, inplace=True)
    top_30_topo = df_topo_work.head(30)
    top_30_topo.to_csv(OUT_TOPO_LINKS_CSV, index=False)

    # --------------------------------------------------------------------------
    # 6. GENERATE VISUALIZATIONS
    # --------------------------------------------------------------------------
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

    # Figure 1: Mechanism Tradeoff
    plt.figure(figsize=(8, 6))
    for _, row in df_trade.iterrows():
        plt.scatter(row['dynamic_persistence_score'], row['solution_quality_score'], s=140, label=row['configuration'])
        plt.annotate(row['configuration'], (row['dynamic_persistence_score'], row['solution_quality_score']),
                     textcoords="offset points", xytext=(0, 8), ha='center', fontsize=9, weight='bold')

    plt.xlabel('Dynamic Persistence Score (0-1, Higher = Longer Search)', fontsize=11, fontweight='bold')
    plt.ylabel('Solution Quality Score (0-1, Higher = Lower Cut)', fontsize=11, fontweight='bold')
    plt.title('Mechanism Tradeoff: Persistence vs Solution Quality', fontsize=13, fontweight='bold', pad=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(FIG_TRADEOFF, dpi=300)
    plt.close()

    # Figure 2: Exploration vs Final Edge Cut
    plt.figure(figsize=(8, 6))
    for _, row in df_prof.iterrows():
        tr_row = df_trade[df_trade['configuration'] == row['configuration']].iloc[0]
        plt.scatter(tr_row['exploration_score'], row['final_edge_cut'], s=140, color='darkorange', alpha=0.85)
        plt.annotate(row['configuration'], (tr_row['exploration_score'], row['final_edge_cut']),
                     textcoords="offset points", xytext=(0, 8), ha='center', fontsize=9, weight='bold')

    plt.xlabel('Exploration Score (0-1, Higher = More Avalanches/Activity)', fontsize=11, fontweight='bold')
    plt.ylabel('Final Edge Cut (Lower is Better)', fontsize=11, fontweight='bold')
    plt.title('Exploration Activity vs Final Partition Quality', fontsize=13, fontweight='bold', pad=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(FIG_EXPL_QUAL, dpi=300)
    plt.close()

    # --------------------------------------------------------------------------
    # 7. GENERATE MARKDOWN AUDIT REPORT
    # --------------------------------------------------------------------------
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    md_report = f"""# BLOC-RELOC V2 MECHANISM AUDIT REPORT

**Date of Execution:** {now_str}  
**Configurations Evaluated:** {len(df_prof)}  

---

## 1. Configuration Profiles Summary

The table below summarizes the interpretative mechanism profile, assigned class, and dynamic metrics across all evaluated BLOC-RELOC v2 configurations:

| Configuration | Class | Quality Rank | Persistence Rank | Exploration Rank | Final Edge Cut | Extinction Time | Total Avalanches | Relaxation Regime |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
"""
    for _, r in df_prof.iterrows():
        md_report += f"| **{r['configuration']}** | `{r['mechanism_class']}` | {r['quality_rank']} | {r['dynamic_persistence_rank']} | {r['exploration_rank']} | {r['final_edge_cut']:.4f} | {r['extinction_time']} | {r['total_avalanches']} | `{r['relaxation_regime']}` |\n"

    md_report += """
---

## 2. Dynamic Regimes Classification

The Dynamics Observatory classifies relaxation trajectories into empirical regimes based on goodness-of-fit model selection:
- **Stretched Exponential:** Characterizes systems undergoing non-exponential, multi-stage relaxation with memory effects or heterogeneous barriers.
- **Power-Law / Exponential Candidates:** Represents asymptotic decay or immediate collapse towards local basins without extended structural reconfiguration.

---

## 3. Exploration vs Premature Convergence Dynamics

Normalized Tradeoff Analysis across configurations (scores scaled strictly [0, 1] relative to the 6 tested configurations):

| Configuration | Quality Score | Persistence Score | Exploration Score | Overall Balance Score |
|:---|:---:|:---:|:---:|:---:|
"""
    for _, r in df_trade.iterrows():
        md_report += f"| **{r['configuration']}** | {r['solution_quality_score']:.4f} | {r['dynamic_persistence_score']:.4f} | {r['exploration_score']:.4f} | {r['overall_balance_score']:.4f} |\n"

    md_report += """
---

## 4. Topology-Dynamics Coupling Highlights

Top absolute correlations between structural graph topology features and dynamic search activity:

| Dynamic Variable | Topology Feature | Pearson r | Spearman rho | |Spearman| |
|:---|:---|:---:|:---:|:---:|
"""
    for _, r in top_30_topo.head(10).iterrows():
        d_var = r['dynamic_variable'] if 'dynamic_variable' in r else 'N/A'
        t_feat = r['topology_feature'] if 'topology_feature' in r else 'N/A'
        p_r = f"{r['pearson_r']:.4f}" if 'pearson_r' in r and pd.notna(r['pearson_r']) else 'N/A'
        s_rho = f"{r['spearman_rho']:.4f}" if 'spearman_rho' in r and pd.notna(r['spearman_rho']) else 'N/A'
        abs_s = f"{r['abs_spearman']:.4f}" if 'abs_spearman' in r and pd.notna(r['abs_spearman']) else 'N/A'
        md_report += f"| `{d_var}` | `{t_feat}` | {p_r} | {s_rho} | {abs_s} |\n"

    md_report += """
---

## 5. Methodological Limitations

- **Sample Size Constraints:** Analysis is strictly bounded to the 6 evaluated algorithmic configurations within the benchmark suite.
- **Exploratory Correlation Scope:** High statistical correlation between dynamic persistence and solution quality reflects empirical co-occurrence rather than direct mechanistic causation.
- **No Causal Inference:** Results serve for auditing behavioral regimes and guiding heuristic design; causal validation requires controlled ablation interventions.

================================================================================
*Report generated automatically by `mechanism_profile_audit.py`*
"""

    with open(OUT_MD_REPORT, 'w', encoding='utf-8') as f:
        f.write(md_report)

    # --------------------------------------------------------------------------
    # 8. TERMINAL COMPLETION OUTPUT
    # --------------------------------------------------------------------------
    print("================================================")
    print("MECHANISM AUDIT UPDATED")
    print("================================================")
    print("\nSTATUS: SUCCESS\n")
    print("Updated:")
    print("  - mechanism_profile.csv")
    print("  - MECHANISM_AUDIT_REPORT.md")
    print("================================================\n")

if __name__ == '__main__':
    main()
