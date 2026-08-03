#!/usr/bin/env python3
"""
================================================================================
BLOC-RELOC-V2: DYNAMICS OBSERVATORY
================================================================================
Self-contained, fully reproducible empirical analysis pipeline for 
optimization trajectories.

Execution:
  python3 scripts/dynamics_observatory.py

Author: Bloc-Reloc Laboratory
================================================================================
"""

import os
import sys
import datetime
import warnings
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Universal plot styling
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['figure.dpi'] = 300

warnings.filterwarnings('ignore')

# ------------------------------------------------------------------------------
# 1. DYNAMIC REPOSITORY ROOT & PATH RESOLUTION
# ------------------------------------------------------------------------------
SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parent.parent

INPUT_DYNAMICS = REPO_ROOT / 'results' / 'search_dynamics.csv'
OUTPUT_DIR = REPO_ROOT / 'results' / 'observatory'

REQUIRED_COLUMNS = [
    'graph',
    'configuration',
    'iteration',
    'edge_cut',
    'accepted',
    'rejected',
    'acceptance_ratio',
    'runtime'
]

CONFIGS = [
    'baseline',
    'affinity',
    'periodic',
    'reactive',
    'affinity_periodic',
    'affinity_reactive'
]

STALL_WINDOW = 5  # Configurable stall window for true plateau detection

# ==============================================================================
# FALLBACK / NATIVE SCIENTIFIC UTILITIES
# ==============================================================================

def curve_fit_fallback(func, xdata, ydata, p0):
    try:
        from scipy.optimize import curve_fit
        popt, _ = curve_fit(func, xdata, ydata, p0=p0, maxfev=10000)
        return popt
    except ImportError:
        def loss(params):
            return np.sum((ydata - func(xdata, *params)) ** 2)
        
        res_params = np.array(p0, dtype=float)
        alpha, gamma, rho = 1.0, 2.0, 0.5
        n = len(p0)
        simplex = [res_params]
        for i in range(n):
            point = np.array(res_params, copy=True)
            point[i] += 0.05 if point[i] != 0 else 0.00025
            simplex.append(point)
            
        for _ in range(1500):
            simplex.sort(key=loss)
            centroid = np.mean(simplex[:-1], axis=0)
            
            # Reflection
            reflected = centroid + alpha * (centroid - simplex[-1])
            if loss(simplex[0]) <= loss(reflected) < loss(simplex[-2]):
                simplex[-1] = reflected
                continue
            # Expansion
            if loss(reflected) < loss(simplex[0]):
                expanded = centroid + gamma * (reflected - centroid)
                simplex[-1] = expanded if loss(expanded) < loss(reflected) else reflected
                continue
            # Contraction
            contracted = centroid + rho * (simplex[-1] - centroid)
            if loss(contracted) < loss(simplex[-1]):
                simplex[-1] = contracted
                continue
            
            # Shrink
            for i in range(1, len(simplex)):
                simplex[i] = simplex[0] + 0.5 * (simplex[i] - simplex[0])
                
        return simplex[0]

# Mathematical Models for Relaxation
def model_exponential(t, a, b, c):
    return a * np.exp(-b * t) + c

def model_stretched_exp(t, a, b, beta, c):
    return a * np.exp(- (b * t) ** beta) + c

def model_logarithmic(t, a, b, c):
    return -a * np.log(b * t + 1.0) + c

def model_power_law(t, a, b, c):
    return a * ((t + 1.0) ** (-b)) + c


# ==============================================================================
# PIPELINE MODULES
# ==============================================================================

def module_1_relaxation(df):
    print(" -> Executing Module 1: Relaxation Fitting (Raw & Normalized with AIC/BIC)...")
    records = []
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    df = df.sort_values(['graph', 'configuration', 'iteration']).copy()
    
    # Robust normalization: explicit loop + pd.concat to preserve all columns
    group_list = []
    for (graph, config), g in df.groupby(['graph', 'configuration'], as_index=False):
        g = g.copy()
        initial = g['edge_cut'].iloc[0]
        final = g['edge_cut'].min()
        denom = initial - final
        if denom > 1e-6:
            g['edge_cut_norm'] = (g['edge_cut'] - final) / denom
        else:
            g['edge_cut_norm'] = 0.0
        group_list.append(g)

    df = pd.concat(group_list, ignore_index=True)

    for config in CONFIGS:
        cdf = df[df['configuration'] == config]
        if cdf.empty:
            continue

        traj_raw = cdf.groupby('iteration')['edge_cut'].mean().reset_index()
        traj_norm = cdf.groupby('iteration')['edge_cut_norm'].mean().reset_index()

        t = traj_raw['iteration'].values.astype(float)
        y_raw = traj_raw['edge_cut'].values.astype(float)
        y_norm = traj_norm['edge_cut_norm'].values.astype(float)
        N = len(t)

        ax1.plot(t, y_raw, label=config, linewidth=2, alpha=0.85)
        ax2.plot(t, y_norm, label=config, linewidth=2, alpha=0.85)

        targets = [('raw', y_raw), ('normalized', y_norm)]

        for target_type, y in targets:
            models = [
                ('exponential', model_exponential, [y[0] - y[-1], 0.1, y[-1]], 3),
                ('stretched_exp', model_stretched_exp, [y[0] - y[-1], 0.1, 0.5, y[-1]], 4),
                ('logarithmic', model_logarithmic, [y[0] - y[-1], 0.1, y[0]], 3),
                ('power_law', model_power_law, [y[0] - y[-1], 0.5, y[-1]], 3)
            ]

            for name, func, p0, k in models:
                warning_short = (name == 'power_law' and N <= 50)
                try:
                    popt = curve_fit_fallback(func, t, y, p0)
                    y_pred = func(t, *popt)
                    sse = np.sum((y - y_pred) ** 2)
                    rmse = np.sqrt(sse / N)
                    
                    sse_val = max(sse, 1e-12)
                    aic = N * np.log(sse_val / N) + 2 * k
                    bic = N * np.log(sse_val / N) + k * np.log(N)

                    records.append({
                        'configuration': config,
                        'target_type': target_type,
                        'model': name,
                        'parameters': ",".join([f"{p:.4f}" for p in popt]),
                        'sse': round(float(sse), 6),
                        'rmse': round(float(rmse), 6),
                        'aic': round(float(aic), 4),
                        'bic': round(float(bic), 4),
                        'warning_short_timeseries': warning_short
                    })
                except Exception:
                    records.append({
                        'configuration': config,
                        'target_type': target_type,
                        'model': name,
                        'parameters': 'FAILED',
                        'sse': np.nan,
                        'rmse': np.nan,
                        'aic': np.nan,
                        'bic': np.nan,
                        'warning_short_timeseries': warning_short
                    })

    ax1.set_title("Raw Average Edge-Cut Relaxation")
    ax1.set_xlabel("Iteration (t)")
    ax1.set_ylabel("Mean Edge Cut")
    ax1.legend(title="Configuration")

    ax2.set_title("Normalized Relaxation E(t) = (Cut(t) - Final)/(Initial - Final)")
    ax2.set_xlabel("Iteration (t)")
    ax2.set_ylabel("E(t) [Normalized Cut]")
    ax2.legend(title="Configuration")

    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / 'relaxation_fit.png')
    plt.close()

    res_df = pd.DataFrame(records)
    res_df.to_csv(OUTPUT_DIR / 'relaxation_models.csv', index=False)

    best_records = []
    for (config, target_type), group in res_df.groupby(['configuration', 'target_type']):
        valid_group = group.dropna(subset=['aic', 'bic'])
        if not valid_group.empty:
            best_aic_row = valid_group.loc[valid_group['aic'].idxmin()]
            best_bic_row = valid_group.loc[valid_group['bic'].idxmin()]
            best_records.append({
                'configuration': config,
                'target_type': target_type,
                'best_model_aic': best_aic_row['model'],
                'min_aic': best_aic_row['aic'],
                'best_model_bic': best_bic_row['model'],
                'min_bic': best_bic_row['bic'],
                'warning_short_timeseries': best_aic_row['warning_short_timeseries']
            })
    
    best_df = pd.DataFrame(best_records)
    best_df.to_csv(OUTPUT_DIR / 'best_relaxation_models.csv', index=False)

    return res_df, df


def module_2_survival(df):
    print(f" -> Executing Module 2: Kaplan-Meier Survival Analysis (Stall Window = {STALL_WINDOW})...")
    
    events = []
    grouped = df.groupby(['graph', 'configuration'])

    for (graph, config), gdata in grouped:
        gdata = gdata.sort_values('iteration')
        cuts = gdata['edge_cut'].values
        iters = gdata['iteration'].values
        max_iter = iters[-1]

        event_time = max_iter
        
        for i in range(len(cuts) - STALL_WINDOW):
            current_val = cuts[i]
            future_vals = cuts[i + 1 : i + 1 + STALL_WINDOW]
            if np.all(future_vals >= current_val):
                event_time = iters[i]
                break

        events.append({
            'graph': graph,
            'configuration': config,
            'event_iteration': event_time
        })

    edf = pd.DataFrame(events)

    km_records = []
    fig, ax = plt.subplots(figsize=(10, 6))

    for config in CONFIGS:
        c_events = edf[edf['configuration'] == config]['event_iteration'].values
        if len(c_events) == 0:
            continue

        n_total = len(c_events)
        max_t = df['iteration'].max()

        survival_prob = 1.0
        t_space = np.arange(0, max_t + 1)
        s_at_t = []

        at_risk = n_total
        for t in t_space:
            d_t = np.sum(c_events == t)
            if at_risk > 0:
                survival_prob *= (1.0 - (d_t / at_risk))
                at_risk -= d_t
            s_at_t.append(survival_prob)

            km_records.append({
                'configuration': config,
                'iteration': int(t),
                'events_d_t': int(d_t),
                'at_risk': int(at_risk + d_t),
                'survival_probability': round(float(survival_prob), 6)
            })

        ax.step(t_space, s_at_t, where='post', label=config, linewidth=2)

    ax.set_title(f"Kaplan-Meier Survival Function: P(Active Search at Iteration t) [Stall Window = {STALL_WINDOW}]")
    ax.set_xlabel("Iteration (t)")
    ax.set_ylabel("S(t) [Probability of NOT having reached Plateau]")
    ax.set_ylim(-0.05, 1.05)
    ax.legend(title="Configuration", bbox_to_anchor=(1.02, 1), loc='upper left')
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / 'kaplan_meier.png')
    plt.close()

    km_df = pd.DataFrame(km_records)
    km_df.to_csv(OUTPUT_DIR / 'survival_analysis.csv', index=False)
    return edf, km_df


def module_3_hazard(km_df):
    print(" -> Executing Module 3: Discrete Hazard Rate Analysis...")
    hazard_records = []

    fig, ax = plt.subplots(figsize=(10, 6))

    for config in CONFIGS:
        cdf = km_df[km_df['configuration'] == config].sort_values('iteration')
        if cdf.empty:
            continue

        t_vals = cdf['iteration'].values
        d_t = cdf['events_d_t'].values
        n_t = cdf['at_risk'].values

        with np.errstate(divide='ignore', invalid='ignore'):
            h_t = np.where(n_t > 0, d_t / n_t, 0.0)

        for t, h in zip(t_vals, h_t):
            hazard_records.append({
                'configuration': config,
                'iteration': int(t),
                'hazard': round(float(h), 6)
            })

        ax.plot(t_vals, h_t, label=config, marker='o', markersize=3, linewidth=1.5, alpha=0.75)

    ax.set_title("Discrete Hazard Rate h(t): Instantaneous Probability of Entering Plateau")
    ax.set_xlabel("Iteration (t)")
    ax.set_ylabel("Hazard Rate h(t)")
    ax.legend(title="Configuration", bbox_to_anchor=(1.02, 1), loc='upper left')
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / 'hazard_rate.png')
    plt.close()

    hdf = pd.DataFrame(hazard_records)
    hdf.to_csv(OUTPUT_DIR / 'hazard_curve.csv', index=False)
    return hdf


def module_4_avalanche(df):
    print(" -> Executing Module 4: Avalanche Improvement Delta Analysis...")
    
    df = df.sort_values(['graph', 'configuration', 'iteration'])
    df['next_edge_cut'] = df.groupby(['graph', 'configuration'])['edge_cut'].shift(-1)
    df['delta'] = df['edge_cut'] - df['next_edge_cut']
    
    delta_df = df.dropna(subset=['delta']).copy()
    
    export_deltas = delta_df[['graph', 'configuration', 'iteration', 'delta']].copy()
    export_deltas.to_csv(OUTPUT_DIR / 'avalanche_distribution.csv', index=False)

    fig, ax = plt.subplots(figsize=(10, 6))

    for config in CONFIGS:
        c_deltas = delta_df[delta_df['configuration'] == config]['delta']
        pos_deltas = c_deltas[c_deltas > 0]
        if pos_deltas.empty:
            continue
            
        counts, bins = np.histogram(pos_deltas, bins=30)
        ax.plot(bins[:-1], counts, label=config, marker='s', markersize=4, linewidth=1.5)

    ax.set_yscale('log')
    ax.set_title("Avalanche Size Distribution (Positive Improvement Steps Δ > 0)")
    ax.set_xlabel("Improvement Magnitude Δ = EdgeCut(t) - EdgeCut(t+1)")
    ax.set_ylabel("Frequency (Log Scale)")
    ax.legend(title="Configuration", bbox_to_anchor=(1.02, 1), loc='upper left')
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / 'delta_distribution.png')
    plt.close()

    return delta_df


def module_5_summary(df, edf, delta_df):
    print(" -> Executing Module 5: Observatory Executive Summary...")
    summary_records = []

    for config in CONFIGS:
        cdf = df[df['configuration'] == config]
        if cdf.empty:
            continue

        cedf = edf[edf['configuration'] == config]
        cddf = delta_df[delta_df['configuration'] == config]

        final_cuts = cdf.groupby('graph')['edge_cut'].last()
        runtimes = cdf.groupby('graph')['runtime'].max()
        plateaus = cedf['event_iteration']
        active_iters = cedf['event_iteration']
        acceptances = cdf.groupby('graph')['acceptance_ratio'].mean()

        pos_deltas = cddf[cddf['delta'] > 0]['delta']

        summary_records.append({
            'configuration': config,
            'mean_final_edge_cut': round(float(final_cuts.mean()), 4),
            'std_final_edge_cut': round(float(final_cuts.std()), 4),
            'mean_runtime_sec': round(float(runtimes.mean()), 4),
            'mean_plateau_iteration': round(float(plateaus.mean()), 4),
            'mean_active_iterations': round(float(active_iters.mean()), 4),
            'mean_acceptance_ratio': round(float(acceptances.mean()), 6),
            'mean_delta_improvement': round(float(pos_deltas.mean()), 4) if not pos_deltas.empty else 0.0,
            'max_delta_improvement': round(float(pos_deltas.max()), 4) if not pos_deltas.empty else 0.0,
            'total_positive_avalanches': int((cddf['delta'] > 0).sum())
        })

    sdf = pd.DataFrame(summary_records)
    sdf.to_csv(OUTPUT_DIR / 'observatory_summary.csv', index=False)
    return sdf


# ==============================================================================
# MAIN EXECUTOR & LAB TRACEABILITY
# ==============================================================================

def main():
    print("================================================================================")
    print("STARTING DYNAMICS OBSERVATORY PIPELINE (REPRODUCIBLE RUN)")
    print("================================================================================")
    print(f" -> Resolved Repository Root: {REPO_ROOT}")

    if not INPUT_DYNAMICS.exists():
        print(f"\n[FATAL ERROR]: Missing input file.")
        print(f"Expected at: {INPUT_DYNAMICS}")
        print("Please ensure search_dynamics.csv exists before running the observatory.")
        sys.exit(1)

    print(f" -> Loading trajectory data from: {INPUT_DYNAMICS}")
    df = pd.read_csv(INPUT_DYNAMICS)

    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        print(f"\n[FATAL ERROR]: Missing required schema columns in search_dynamics.csv.")
        print(f"Missing columns: {missing_cols}")
        print(f"Required columns: {REQUIRED_COLUMNS}")
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    rows_count = len(df)
    unique_graphs = df['graph'].nunique()
    detected_configs = list(df['configuration'].unique())

    metadata_path = OUTPUT_DIR / 'run_metadata.txt'
    with open(metadata_path, 'w') as f:
        f.write("BLOC-RELOC-V2 DYNAMICS OBSERVATORY RUN METADATA\n")
        f.write("==================================================================\n")
        f.write(f"Execution Date/Time : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
        f.write(f"Python Version      : {sys.version.split()[0]}\n")
        f.write(f"Pandas Version      : {pd.__version__}\n")
        f.write(f"Numpy Version       : {np.__version__}\n")
        f.write(f"Input Path          : {INPUT_DYNAMICS}\n")
        f.write(f"Output Path         : {OUTPUT_DIR}\n")
        f.write("------------------------------------------------------------------\n")
        f.write(f"Rows Processed      : {rows_count}\n")
        f.write(f"Graphs Count        : {unique_graphs}\n")
        f.write(f"Detected Configs    : {', '.join(detected_configs)}\n")
        f.write("==================================================================\n")

    rel_df, df_norm = module_1_relaxation(df)
    edf, km_df = module_2_survival(df_norm)
    hdf = module_3_hazard(km_df)
    delta_df = module_4_avalanche(df_norm)
    sdf = module_5_summary(df_norm, edf, delta_df)

    print("\n================================================================================")
    print("OBSERVATORY COMPLETE")
    print("================================================================================")
    print(f"rows processed: {rows_count}")
    print(f"graphs:         {unique_graphs}")
    print(f"configs:        {len(detected_configs)} ({', '.join(detected_configs)})")
    print(f"outputs:        {OUTPUT_DIR}/")
    print("====================================================================\n")

if __name__ == '__main__':
    main()
