#!/usr/bin/env python3
"""
================================================================================
BLOC-RELOC-V2: PERFORMANCE DYNAMICS AUDIT & CORRELATION ANALYSIS
================================================================================
Self-contained script that cross-analyzes dynamic regimes (survival, avalanches,
relaxation) with optimization performance (final edge cut, delta improvements,
runtime) across all configurations.

Execution:
  python3 scripts/observatory_performance_dynamics_audit.py

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

INPUT_DYNAMIC_REGIME = OUTPUT_DIR / 'dynamic_regime_summary.csv'
INPUT_OBS_SUMMARY = OUTPUT_DIR / 'observatory_summary.csv'

OUTPUT_AUDIT_CSV = OUTPUT_DIR / 'performance_dynamics_audit.csv'
OUTPUT_CORR_CSV = OUTPUT_DIR / 'performance_dynamics_correlations.csv'

REQUIRED_INPUTS = {
    'dynamic_regime_summary.csv': INPUT_DYNAMIC_REGIME,
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
# FALLBACK CORRELATION CALCULATOR (PURE NUMPY / PANDAS)
# ==============================================================================

def compute_pearson(x, y):
    valid = ~(np.isnan(x) | np.isnan(y))
    xv, yv = x[valid], y[valid]
    if len(xv) < 2 or np.std(xv) == 0 or np.std(yv) == 0:
        return np.nan
    return float(np.corrcoef(xv, yv)[0, 1])

def compute_spearman(x, y):
    valid = ~(np.isnan(x) | np.isnan(y))
    xv, yv = x[valid], y[valid]
    if len(xv) < 2:
        return np.nan
    rank_x = pd.Series(xv).rank().values
    rank_y = pd.Series(yv).rank().values
    if np.std(rank_x) == 0 or np.std(rank_y) == 0:
        return np.nan
    return float(np.corrcoef(rank_x, rank_y)[0, 1])


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
    df_dyn = pd.read_csv(INPUT_DYNAMIC_REGIME)
    df_obs = pd.read_csv(INPUT_OBS_SUMMARY)

    # Merge inputs on configuration
    merged = df_dyn.merge(df_obs, on='configuration', how='inner')

    audit_records = []

    for config in CONFIGS:
        row = merged[merged['configuration'] == config]
        if row.empty:
            continue

        r = row.iloc[0]

        # Extract primary metrics
        mean_final_edge_cut = float(r['mean_final_edge_cut']) if 'mean_final_edge_cut' in r else np.nan
        std_final_edge_cut = float(r['std_final_edge_cut']) if 'std_final_edge_cut' in r else np.nan
        mean_runtime_sec = float(r['mean_runtime_sec']) if 'mean_runtime_sec' in r else np.nan

        time_to_survival_50 = float(r['time_to_survival_50']) if 'time_to_survival_50' in r else np.nan
        time_to_survival_10 = float(r['time_to_survival_10']) if 'time_to_survival_10' in r else np.nan
        extinction_time = float(r['extinction_time']) if 'extinction_time' in r else np.nan
        mean_active_iterations = float(r['mean_active_iterations']) if 'mean_active_iterations' in r else np.nan
        total_avalanches = float(r['total_avalanches']) if 'total_avalanches' in r else np.nan
        mean_delta = float(r['mean_delta']) if 'mean_delta' in r else np.nan
        median_delta = float(r['median_delta']) if 'median_delta' in r else np.nan
        relaxation_regime = str(r['relaxation_regime']) if 'relaxation_regime' in r else np.nan

        mean_delta_improvement = float(r['mean_delta_improvement']) if 'mean_delta_improvement' in r else np.nan
        max_delta_improvement = float(r['max_delta_improvement']) if 'max_delta_improvement' in r else np.nan

        # Derived metrics
        exploration_duration = mean_active_iterations
        exploration_survival_index = (time_to_survival_50 / extinction_time) if (extinction_time > 0 and not np.isnan(extinction_time)) else np.nan
        avalanche_frequency = (total_avalanches / extinction_time) if (extinction_time > 0 and not np.isnan(extinction_time)) else np.nan

        if not np.isnan(mean_runtime_sec) and mean_runtime_sec > 0 and not np.isnan(mean_delta_improvement):
            dynamic_efficiency = mean_delta_improvement / mean_runtime_sec
        else:
            dynamic_efficiency = np.nan

        audit_records.append({
            'configuration': config,
            'mean_final_edge_cut': round(mean_final_edge_cut, 4) if not np.isnan(mean_final_edge_cut) else np.nan,
            'std_final_edge_cut': round(std_final_edge_cut, 4) if not np.isnan(std_final_edge_cut) else np.nan,
            'mean_runtime_sec': round(mean_runtime_sec, 6) if not np.isnan(mean_runtime_sec) else np.nan,
            'time_to_survival_50': time_to_survival_50,
            'time_to_survival_10': time_to_survival_10,
            'extinction_time': extinction_time,
            'mean_active_iterations': round(mean_active_iterations, 4) if not np.isnan(mean_active_iterations) else np.nan,
            'total_avalanches': total_avalanches,
            'mean_delta': round(mean_delta, 4) if not np.isnan(mean_delta) else np.nan,
            'median_delta': round(median_delta, 4) if not np.isnan(median_delta) else np.nan,
            'relaxation_regime': relaxation_regime,
            'exploration_duration': round(exploration_duration, 4) if not np.isnan(exploration_duration) else np.nan,
            'exploration_survival_index': round(exploration_survival_index, 6) if not np.isnan(exploration_survival_index) else np.nan,
            'avalanche_frequency': round(avalanche_frequency, 6) if not np.isnan(avalanche_frequency) else np.nan,
            'dynamic_efficiency': round(dynamic_efficiency, 6) if not np.isnan(dynamic_efficiency) else np.nan,
            'mean_delta_improvement': round(mean_delta_improvement, 4) if not np.isnan(mean_delta_improvement) else np.nan,
            'max_delta_improvement': round(max_delta_improvement, 4) if not np.isnan(max_delta_improvement) else np.nan
        })

    audit_df = pd.DataFrame(audit_records)
    audit_df.to_csv(OUTPUT_AUDIT_CSV, index=False)

    # 3. Compute Correlations
    dynamic_vars = [
        'time_to_survival_50',
        'time_to_survival_10',
        'extinction_time',
        'total_avalanches',
        'mean_delta',
        'mean_active_iterations'
    ]

    performance_vars = [
        'mean_final_edge_cut',
        'mean_delta_improvement',
        'max_delta_improvement'
    ]

    corr_records = []

    for d_var in dynamic_vars:
        for p_var in performance_vars:
            if d_var in audit_df.columns and p_var in audit_df.columns:
                x = audit_df[d_var].values.astype(float)
                y = audit_df[p_var].values.astype(float)

                r_p = compute_pearson(x, y)
                r_s = compute_spearman(x, y)

                corr_records.append({
                    'dynamic_variable': d_var,
                    'performance_variable': p_var,
                    'pearson_r': round(r_p, 6) if not np.isnan(r_p) else np.nan,
                    'spearman_rho': round(r_s, 6) if not np.isnan(r_s) else np.nan
                })

    corr_df = pd.DataFrame(corr_records)
    corr_df.to_csv(OUTPUT_CORR_CSV, index=False)

    # Final stdout
    print("================================================")
    print("PERFORMANCE DYNAMICS AUDIT COMPLETE")
    print("================================================")
    print("\nSTATUS: SUCCESS\n")
    print("Generated:")
    print("  - performance_dynamics_audit.csv")
    print("  - performance_dynamics_correlations.csv")
    print("================================================\n")

if __name__ == '__main__':
    main()
