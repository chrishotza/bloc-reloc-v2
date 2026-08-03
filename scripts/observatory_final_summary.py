#!/usr/bin/env python3
"""
================================================================================
BLOC-RELOC-V2: FINAL DYNAMIC REGIME SUMMARY (AUDIT TABLE GENERATOR)
================================================================================
Self-contained script that reads existing Dynamics Observatory outputs and 
compiles a unified audit table summarizing survival, avalanche dynamics, 
and relaxation regimes per configuration.

Execution:
  python3 scripts/observatory_final_summary.py

Author: Bloc-Reloc Laboratory
================================================================================
"""

import sys
import numpy as np
import pandas as pd
from pathlib import Path

# ------------------------------------------------------------------------------
# 1. REPOSITORY ROOT & PATH RESOLUTION
# ------------------------------------------------------------------------------
SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parent.parent

OUTPUT_DIR = REPO_ROOT / 'results' / 'observatory'

INPUT_SURVIVAL = OUTPUT_DIR / 'survival_analysis.csv'
INPUT_AVALANCHE = OUTPUT_DIR / 'avalanche_statistics.csv'
INPUT_REGIME = OUTPUT_DIR / 'relaxation_regime.csv'
INPUT_OBS_SUMMARY = OUTPUT_DIR / 'observatory_summary.csv'

OUTPUT_CSV = OUTPUT_DIR / 'dynamic_regime_summary.csv'

REQUIRED_INPUTS = {
    'survival_analysis.csv': INPUT_SURVIVAL,
    'avalanche_statistics.csv': INPUT_AVALANCHE,
    'relaxation_regime.csv': INPUT_REGIME,
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
# MAIN EXECUTOR & AUDIT GENERATION
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
    df_surv = pd.read_csv(INPUT_SURVIVAL)
    df_aval = pd.read_csv(INPUT_AVALANCHE)
    df_regime = pd.read_csv(INPUT_REGIME)

    summary_records = []

    for config in CONFIGS:
        c_surv = df_surv[df_surv['configuration'] == config].sort_values('iteration')
        c_aval = df_aval[df_aval['configuration'] == config]
        c_regime = df_regime[df_regime['configuration'] == config]

        if c_surv.empty:
            continue

        # --- Survival metrics ---
        # survival_t5, t10, t15
        s_t5_row = c_surv[c_surv['iteration'] == 5]
        survival_t5 = float(s_t5_row['survival_probability'].values[0]) if not s_t5_row.empty else np.nan

        s_t10_row = c_surv[c_surv['iteration'] == 10]
        survival_t10 = float(s_t10_row['survival_probability'].values[0]) if not s_t10_row.empty else np.nan

        s_t15_row = c_surv[c_surv['iteration'] == 15]
        survival_t15 = float(s_t15_row['survival_probability'].values[0]) if not s_t15_row.empty else np.nan

        # time_to_survival_50: first iteration where survival_probability <= 0.5
        s_50_row = c_surv[c_surv['survival_probability'] <= 0.5]
        time_to_survival_50 = int(s_50_row['iteration'].iloc[0]) if not s_50_row.empty else np.nan

        # time_to_survival_10: first iteration where survival_probability <= 0.1
        s_10_row = c_surv[c_surv['survival_probability'] <= 0.1]
        time_to_survival_10 = int(s_10_row['iteration'].iloc[0]) if not s_10_row.empty else np.nan

        # extinction_time: last iteration with survival_probability > 0
        s_ext_row = c_surv[c_surv['survival_probability'] > 0]
        extinction_time = int(s_ext_row['iteration'].iloc[-1]) if not s_ext_row.empty else np.nan

        # --- Avalanche metrics ---
        if not c_aval.empty:
            total_avalanches = int(c_aval['count'].values[0])
            mean_delta = float(c_aval['mean'].values[0])
            median_delta = float(c_aval['median'].values[0])
            max_delta = float(c_aval['max'].values[0])
        else:
            total_avalanches = np.nan
            mean_delta = np.nan
            median_delta = np.nan
            max_delta = np.nan

        # --- Relaxation regime metrics ---
        if not c_regime.empty:
            best_relaxation_model = str(c_regime['best_model_aic'].values[0])
            relaxation_regime = str(c_regime['relaxation_regime'].values[0])
        else:
            best_relaxation_model = np.nan
            relaxation_regime = np.nan

        summary_records.append({
            'configuration': config,
            'survival_t5': round(survival_t5, 6) if not np.isnan(survival_t5) else np.nan,
            'survival_t10': round(survival_t10, 6) if not np.isnan(survival_t10) else np.nan,
            'survival_t15': round(survival_t15, 6) if not np.isnan(survival_t15) else np.nan,
            'time_to_survival_50': time_to_survival_50,
            'time_to_survival_10': time_to_survival_10,
            'extinction_time': extinction_time,
            'total_avalanches': total_avalanches,
            'mean_delta': round(mean_delta, 4) if not np.isnan(mean_delta) else np.nan,
            'median_delta': round(median_delta, 4) if not np.isnan(median_delta) else np.nan,
            'max_delta': round(max_delta, 4) if not np.isnan(max_delta) else np.nan,
            'best_relaxation_model': best_relaxation_model,
            'relaxation_regime': relaxation_regime
        })

    out_df = pd.DataFrame(summary_records)
    out_df.to_csv(OUTPUT_CSV, index=False)

    print("================================================")
    print("FINAL DYNAMIC REGIME SUMMARY COMPLETE")
    print("================================================")
    print(f"Filas generadas: {len(out_df)}")
    print(f"Ruta CSV:        {OUTPUT_CSV}")
    print(f"Configuraciones: {', '.join(out_df['configuration'].tolist())}")
    print("================================================\n")

if __name__ == '__main__':
    main()
