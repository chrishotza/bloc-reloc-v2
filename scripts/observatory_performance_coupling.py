#!/usr/bin/env python3
"""
================================================================================
BLOC-RELOC-V2: PERFORMANCE-DYNAMICS COUPLING AUDIT
================================================================================
Cross-audits dynamic regimes with final performance optimization metrics.
Answers: Do longer relaxation regimes and power-law candidates produce 
better quality solutions or merely extended exploration?

Execution:
  python3 scripts/observatory_performance_coupling.py

Author: Bloc-Reloc Laboratory
================================================================================
"""

import sys
import numpy as np
import pandas as pd
from pathlib import Path

# ------------------------------------------------------------------------------
# 1. PATH RESOLUTION & VALIDATION
# ------------------------------------------------------------------------------
SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parent.parent

OBSERVATORY_DIR = REPO_ROOT / 'results' / 'observatory'

INPUT_DYNAMIC_SUMMARY = OBSERVATORY_DIR / 'dynamic_regime_summary.csv'
INPUT_OBS_SUMMARY = OBSERVATORY_DIR / 'observatory_summary.csv'

OUTPUT_CSV = OBSERVATORY_DIR / 'performance_dynamics_coupling.csv'

REQUIRED_INPUTS = {
    'dynamic_regime_summary.csv': INPUT_DYNAMIC_SUMMARY,
    'observatory_summary.csv': INPUT_OBS_SUMMARY
}

CONFIGS = [
    'baseline',
    'affinity',
    'periodic',
    'reactive',
    'affinity_periodic',
    'affinity_reactive'
]

# ==============================================================================
# MAIN EXECUTOR & COUPLING ANALYSIS
# ==============================================================================

def main():
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

    OBSERVATORY_DIR.mkdir(parents=True, exist_ok=True)

    df_dyn = pd.read_csv(INPUT_DYNAMIC_SUMMARY)
    df_obs = pd.read_csv(INPUT_OBS_SUMMARY)

    # Calculate global optimization performance metrics per configuration
    perf_records = []
    for config in CONFIGS:
        c_obs = df_obs[df_obs['configuration'] == config]
        if c_obs.empty:
            continue

        mean_initial = float(c_obs['initial_edge_cut'].mean())
        mean_final = float(c_obs['final_edge_cut'].mean())
        
        # Improvement: Absolute & Percentage
        mean_abs_improvement = mean_initial - mean_final
        mean_pct_improvement = (mean_abs_improvement / mean_initial * 100.0) if mean_initial > 0 else 0.0

        # Solution Stability: Std Dev across graph instances
        std_final = float(c_obs['final_edge_cut'].std()) if len(c_obs) > 1 else 0.0

        perf_records.append({
            'configuration': config,
            'mean_initial_edge_cut': round(mean_initial, 4),
            'mean_final_edge_cut': round(mean_final, 4),
            'mean_abs_improvement': round(mean_abs_improvement, 4),
            'mean_pct_improvement': round(mean_pct_improvement, 4),
            'std_final_edge_cut': round(std_final, 4)
        })

    df_perf = pd.DataFrame(perf_records)

    # Merge performance with dynamic regime summary
    df_coupled = pd.merge(df_dyn, df_perf, on='configuration', how='inner')

    # Reorder columns logically: Configuration -> Performance -> Dynamics -> Avalanches -> Regime
    target_columns = [
        'configuration',
        'mean_initial_edge_cut',
        'mean_final_edge_cut',
        'mean_abs_improvement',
        'mean_pct_improvement',
        'std_final_edge_cut',
        'time_to_survival_50',
        'time_to_survival_10',
        'extinction_time',
        'survival_t5',
        'survival_t10',
        'survival_t15',
        'total_avalanches',
        'mean_delta',
        'median_delta',
        'max_delta',
        'best_relaxation_model',
        'relaxation_regime'
    ]

    # Include any extra columns dynamically if present
    final_cols = [c for c in target_columns if c in df_coupled.columns] + \
                 [c for c in df_coupled.columns if c not in target_columns]

    df_coupled = df_coupled[final_cols]
    df_coupled.to_csv(OUTPUT_CSV, index=False)

    print("================================================")
    print("PERFORMANCE-DYNAMICS COUPLING AUDIT COMPLETE")
    print("================================================")
    print(f"Filas generadas: {len(df_coupled)}")
    print(f"Ruta CSV:        {OUTPUT_CSV}")
    print(f"Configuraciones: {', '.join(df_coupled['configuration'].tolist())}")
    print("================================================\n")

if __name__ == '__main__':
    main()
