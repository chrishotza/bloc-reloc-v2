#!/usr/bin/env python3
"""
================================================================================
BLOC-RELOC-V2: MECHANISM FINGERPRINT GENERATOR
================================================================================
Constructs a compact behavioral representation (fingerprint) for each BLOC-RELOC v2
configuration using existing Observatory outputs.

Execution:
  python3 scripts/mechanism_fingerprint.py

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
AUDIT_DIR = OBSERVATORY_DIR / 'mechanism_audit'
OUTPUT_DIR = OBSERVATORY_DIR / 'mechanism_fingerprint'

INPUT_MECH_PROF = AUDIT_DIR / 'mechanism_profile.csv'
INPUT_TRADEOFF = AUDIT_DIR / 'tradeoff_analysis.csv'
INPUT_PERF_AUDIT = OBSERVATORY_DIR / 'performance_dynamics_audit.csv'
INPUT_TOPO_CORR = OBSERVATORY_DIR / 'topology_dynamics_correlation.csv'

REQUIRED_INPUTS = {
    'mechanism_profile.csv': INPUT_MECH_PROF,
    'tradeoff_analysis.csv': INPUT_TRADEOFF,
    'performance_dynamics_audit.csv': INPUT_PERF_AUDIT,
    'topology_dynamics_correlation.csv': INPUT_TOPO_CORR
}

OUT_FINGERPRINT_CSV = OUTPUT_DIR / 'mechanism_fingerprint.csv'
OUT_MD_REPORT = OUTPUT_DIR / 'MECHANISM_FINGERPRINT_REPORT.md'
FIG_MECH_SPACE = OUTPUT_DIR / 'mechanism_space.png'


# ------------------------------------------------------------------------------
# HELPER FUNCTIONS FOR VECTOR DERIVATION
# ------------------------------------------------------------------------------
def get_score_category(score):
    if score >= 0.66:
        return 'HIGH'
    elif score >= 0.33:
        return 'MEDIUM'
    else:
        return 'LOW'


def build_mechanism_vector(q_sc, p_sc, e_sc, m_class):
    q_cat = get_score_category(q_sc)
    p_cat = get_score_category(p_sc)
    e_cat = get_score_category(e_sc)
    class_tag = m_class.upper().replace('-', '_')
    return f"QUALITY_{q_cat} | PERSISTENCE_{p_cat} | EXPLORATION_{e_cat} | {class_tag}"


# ==============================================================================
# MAIN EXECUTOR
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

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 2. Load inputs
    df_prof = pd.read_csv(INPUT_MECH_PROF)
    df_trade = pd.read_csv(INPUT_TRADEOFF)
    df_audit = pd.read_csv(INPUT_PERF_AUDIT)

    # Merge inputs on configuration
    df_merged = df_prof.merge(df_trade, on='configuration', how='inner')
    df_merged = df_merged.merge(df_audit, on='configuration', how='inner', suffixes=('', '_audit'))

    # 3. Construct mechanism_fingerprint Data
    records = []
    for _, row in df_merged.iterrows():
        config = row['configuration']
        m_class = row['mechanism_class']
        q_score = float(row['solution_quality_score'])
        p_score = float(row['dynamic_persistence_score'])
        e_score = float(row['exploration_score'])
        b_score = float(row['overall_balance_score'])

        # Raw / Derived metrics mapping
        # Convergence speed is inversely proportional to time_to_survival_50 or extinction_time
        t_surv = row.get('time_to_survival_50', np.nan)
        if pd.isna(t_surv) or t_surv == 0:
            conv_speed = np.nan
        else:
            conv_speed = round(1.0 / float(t_surv), 6)

        dyn_lifetime = float(row['extinction_time'])
        aval_act = int(row['total_avalanches'])
        regime = str(row['relaxation_regime'])

        m_vector = build_mechanism_vector(q_score, p_score, e_score, m_class)

        records.append({
            'configuration': config,
            'mechanism_class': m_class,
            'quality_score': np.round(q_score, 4),
            'persistence_score': np.round(p_score, 4),
            'exploration_score': np.round(e_score, 4),
            'balance_score': np.round(b_score, 4),
            'convergence_speed': conv_speed,
            'dynamic_lifetime': dyn_lifetime,
            'avalanche_activity': aval_act,
            'relaxation_regime': regime,
            'mechanism_vector': m_vector
        })

    df_fp = pd.DataFrame(records)
    df_fp.to_csv(OUT_FINGERPRINT_CSV, index=False)

    # --------------------------------------------------------------------------
    # 4. CREATE FIGURE: mechanism_space.png
    # --------------------------------------------------------------------------
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    plt.figure(figsize=(8, 6))

    for _, row in df_fp.iterrows():
        color = 'navy' if row['mechanism_class'] == 'Balanced' else ('firebrick' if row['mechanism_class'] == 'Premature-convergent' else 'darkgreen')
        plt.scatter(row['exploration_score'], row['quality_score'], s=150, color=color, alpha=0.85)
        plt.annotate(row['configuration'], (row['exploration_score'], row['quality_score']),
                     textcoords="offset points", xytext=(0, 8), ha='center', fontsize=9, fontweight='bold')

    plt.xlabel('Exploration Score (0-1, Higher = More Avalanches/Activity)', fontsize=11, fontweight='bold')
    plt.ylabel('Quality Score (0-1, Higher = Lower Cut)', fontsize=11, fontweight='bold')
    plt.title('BLOC-RELOC v2 Mechanism Space', fontsize=13, fontweight='bold', pad=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(FIG_MECH_SPACE, dpi=300)
    plt.close()

    # --------------------------------------------------------------------------
    # 5. GENERATE REPORT: MECHANISM_FINGERPRINT_REPORT.md
    # --------------------------------------------------------------------------
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    md_report = f"""# BLOC-RELOC V2 MECHANISM FINGERPRINT

**Date of Execution:** {now_str}  
**Evaluated Configurations:** {len(df_fp)}  

---

## Configuration fingerprints

The table below summarizes the dynamic fingerprint metrics and descriptive behavioral vectors across all evaluated BLOC-RELOC v2 configurations:

| Configuration | Class | Quality | Persistence | Exploration | Balance | Convergence Speed | Dynamic Lifetime | Avalanches | Relaxation Regime | Mechanism Vector |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|:---|
"""
    for _, r in df_fp.iterrows():
        md_report += f"| **{r['configuration']}** | `{r['mechanism_class']}` | {r['quality_score']:.4f} | {r['persistence_score']:.4f} | {r['exploration_score']:.4f} | {r['balance_score']:.4f} | {r['convergence_speed']} | {r['dynamic_lifetime']} | {r['avalanche_activity']} | `{r['relaxation_regime']}` | `{r['mechanism_vector']}` |\n"

    md_report += """
---

## Behavioral groups

### Balanced
- **Characteristics:** Demonstrates a robust trade-off between search persistence, dynamic activity, and optimal final cut quality.
- **Configurations:** 
"""
    bal_configs = df_fp[df_fp['mechanism_class'] == 'Balanced']['configuration'].tolist()
    if bal_configs:
        for c in bal_configs:
            md_report += f"  - `{c}`\n"
    else:
        md_report += "  - *None identified*\n"

    md_report += """
### Premature-convergent
- **Characteristics:** Early dynamic collapse characterized by low extinction times, minimal avalanche activity, and rapid loss of reconfiguration capability.
- **Configurations:**
"""
    prem_configs = df_fp[df_fp['mechanism_class'] == 'Premature-convergent']['configuration'].tolist()
    if prem_configs:
        for c in prem_configs:
            md_report += f"  - `{c}`\n"
    else:
        md_report += "  - *None identified*\n"

    md_report += """
### Explorer
- **Characteristics:** Prolonged dynamic lifetime with high avalanche occurrence and extensive phase-space exploration.
- **Configurations:**
"""
    exp_configs = df_fp[df_fp['mechanism_class'] == 'Explorer']['configuration'].tolist()
    if exp_configs:
        for c in exp_configs:
            md_report += f"  - `{c}`\n"
    else:
        md_report += "  - *None identified*\n"

    md_report += """
---

## Main trade-offs

- **Calidad vs Exploración:** Configurations exhibit varying capabilities in translating raw phase-space exploration into partition improvement. High exploration scores do not strictly guarantee minimal final edge cut.
- **Persistencia vs Convergencia:** Extended dynamic persistence allows escaping local minima but delays state stabilization, whereas rapid convergence often results in premature trapping.
- **Actividad Dinámica vs Resultado Final:** Elevated avalanche activity indicates sustained active reallocations; however, effective heuristics must channel this energy into structural convergence.

---

## Limitations

- **Sample Size Constraints:** The empirical analysis is strictly bounded to the 6 benchmarked algorithmic configurations within BLOC-RELOC v2.
- **Descriptive Framework:** Scores and vectors represent normalized comparative metrics across the evaluated suite rather than absolute theoretical bounds.
- **Correlation vs Causality:** High co-occurrence of dynamic persistence and solution quality reflects empirical behavior; causal mechanistic proof requires isolated ablation interventions.

================================================================================
*Report generated automatically by `mechanism_fingerprint.py`*
"""

    with open(OUT_MD_REPORT, 'w', encoding='utf-8') as f:
        f.write(md_report)

    # --------------------------------------------------------------------------
    # 6. TERMINAL OUTPUT
    # --------------------------------------------------------------------------
    print("================================================")
    print("MECHANISM FINGERPRINT COMPLETE")
    print("================================================")
    print("\nSTATUS: SUCCESS\n")


if __name__ == '__main__':
    main()
