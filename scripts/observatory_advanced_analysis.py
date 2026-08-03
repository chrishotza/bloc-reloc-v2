#!/usr/bin/env python3
"""
================================================================================
BLOC-RELOC-V2: OBSERVATORY ADVANCED ANALYSIS (FINAL REPRODUCIBLE ARTIFACT)
================================================================================
Empirical dynamics structural analysis pipeline.
Reads outputs from Dynamics Observatory v1 and topology features to analyze:
  1. Relaxation Regime Classification
  2. Avalanche Statistics & Tail Models
  3. Universal Relaxation Collapse
  4. Topology Dynamics Coupling

Execution:
  python3 scripts/observatory_advanced_analysis.py

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

INPUT_SEARCH_DYNAMICS = REPO_ROOT / 'results' / 'search_dynamics.csv'
INPUT_RELAXATION_MODELS = REPO_ROOT / 'results' / 'observatory' / 'relaxation_models.csv'
INPUT_BEST_RELAXATION = REPO_ROOT / 'results' / 'observatory' / 'best_relaxation_models.csv'
INPUT_AVALANCHE_DIST = REPO_ROOT / 'results' / 'observatory' / 'avalanche_distribution.csv'
INPUT_TOPOLOGY = REPO_ROOT / 'results' / 'topology_multivariate.csv'

OUTPUT_DIR = REPO_ROOT / 'results' / 'observatory'

REQUIRED_INPUTS = {
    'search_dynamics.csv': INPUT_SEARCH_DYNAMICS,
    'relaxation_models.csv': INPUT_RELAXATION_MODELS,
    'best_relaxation_models.csv': INPUT_BEST_RELAXATION,
    'avalanche_distribution.csv': INPUT_AVALANCHE_DIST,
    'topology_multivariate.csv': INPUT_TOPOLOGY
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
# FALLBACK FITTERS & MATHEMATICAL TAIL MODELS
# ==============================================================================

def curve_fit_fallback(func, xdata, ydata, p0):
    """
    Nelder-Mead Simplex optimization fallback if scipy is unavailable.
    """
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

def tail_exp_model(x, a, lambda_val):
    return a * np.exp(-lambda_val * x)

def tail_power_model(x, a, alpha):
    return a * (x ** (-alpha))


# ==============================================================================
# PIPELINE MODULES
# ==============================================================================

def module_1_relaxation_classification():
    print(" -> Executing Module 1: Relaxation Regime Classification...")
    best_rel = pd.read_csv(INPUT_BEST_RELAXATION)
    
    # Filter normalized target fits
    norm_best = best_rel[best_rel['target_type'] == 'normalized'].copy() if 'target_type' in best_rel.columns else best_rel.copy()
    
    regime_records = []
    for config in CONFIGS:
        row = norm_best[norm_best['configuration'] == config]
        if row.empty:
            continue
        
        best_aic_model = str(row['best_model_aic'].values[0])
        best_bic_model = str(row['best_model_bic'].values[0])
        
        # Categorize regime string based on empirical IC winners
        if best_aic_model == 'exponential':
            regime = 'exponential dominated'
        elif best_aic_model == 'stretched_exp':
            regime = 'stretched exponential dominated'
        elif best_aic_model == 'logarithmic':
            regime = 'logarithmic dominated'
        elif best_aic_model == 'power_law':
            regime = 'power-law candidate'
        else:
            regime = 'unclassified'
            
        regime_records.append({
            'configuration': config,
            'best_model_aic': best_aic_model,
            'best_model_bic': best_bic_model,
            'relaxation_regime': regime
        })
        
    regime_df = pd.DataFrame(regime_records)
    out_path = OUTPUT_DIR / 'relaxation_regime.csv'
    regime_df.to_csv(out_path, index=False)
    print(f"    Saved: {out_path.name}")
    return regime_df


def module_2_avalanche_statistics():
    print(" -> Executing Module 2: Avalanche Statistics & Tail Fitting...")
    aval_df = pd.read_csv(INPUT_AVALANCHE_DIST)
    
    # Strictly Δ > 0
    pos_aval = aval_df[aval_df['delta'] > 0].copy()
    
    stats_records = []
    tail_records = []
    
    for config in CONFIGS:
        c_deltas = pos_aval[pos_aval['configuration'] == config]['delta'].values
        if len(c_deltas) == 0:
            continue
            
        n_events = len(c_deltas)
        mean_val = np.mean(c_deltas)
        median_val = np.median(c_deltas)
        max_val = np.max(c_deltas)
        
        p50 = np.percentile(c_deltas, 50)
        p75 = np.percentile(c_deltas, 75)
        p90 = np.percentile(c_deltas, 90)
        p95 = np.percentile(c_deltas, 95)
        p99 = np.percentile(c_deltas, 99)
        
        stats_records.append({
            'configuration': config,
            'count': n_events,
            'mean': round(float(mean_val), 4),
            'median': round(float(median_val), 4),
            'max': round(float(max_val), 4),
            'p50': round(float(p50), 4),
            'p75': round(float(p75), 4),
            'p90': round(float(p90), 4),
            'p95': round(float(p95), 4),
            'p99': round(float(p99), 4)
        })
        
        # Construct empirical CCDF
        sorted_x = np.sort(c_deltas)
        ccdf = 1.0 - (np.arange(1, n_events + 1) / n_events)
        
        valid_mask = (ccdf > 0) & (sorted_x > 0)
        x_fit = sorted_x[valid_mask]
        y_fit = ccdf[valid_mask]
        N_fit = len(x_fit)
        
        # Exponential Tail
        try:
            popt_exp = curve_fit_fallback(tail_exp_model, x_fit, y_fit, p0=[1.0, 0.1])
            y_pred_exp = tail_exp_model(x_fit, *popt_exp)
            sse_exp = np.sum((y_fit - y_pred_exp) ** 2)
            rmse_exp = np.sqrt(sse_exp / N_fit)
            k_exp = 2
            sse_val_exp = max(sse_exp, 1e-12)
            aic_exp = N_fit * np.log(sse_val_exp / N_fit) + 2 * k_exp
            bic_exp = N_fit * np.log(sse_val_exp / N_fit) + k_exp * np.log(N_fit)
            
            tail_records.append({
                'configuration': config,
                'model': 'exponential_tail',
                'parameters': f"a={popt_exp[0]:.4f}, lambda={popt_exp[1]:.4f}",
                'rmse': round(float(rmse_exp), 6),
                'aic': round(float(aic_exp), 4),
                'bic': round(float(bic_exp), 4)
            })
        except Exception:
            tail_records.append({
                'configuration': config, 'model': 'exponential_tail',
                'parameters': 'FAILED', 'rmse': np.nan, 'aic': np.nan, 'bic': np.nan
            })
            
        # Power Law Tail
        try:
            popt_pw = curve_fit_fallback(tail_power_model, x_fit, y_fit, p0=[1.0, 1.0])
            y_pred_pw = tail_power_model(x_fit, *popt_pw)
            sse_pw = np.sum((y_fit - y_pred_pw) ** 2)
            rmse_pw = np.sqrt(sse_pw / N_fit)
            k_pw = 2
            sse_val_pw = max(sse_pw, 1e-12)
            aic_pw = N_fit * np.log(sse_val_pw / N_fit) + 2 * k_pw
            bic_pw = N_fit * np.log(sse_val_pw / N_fit) + k_pw * np.log(N_fit)
            
            tail_records.append({
                'configuration': config,
                'model': 'power_law_tail',
                'parameters': f"a={popt_pw[0]:.4f}, alpha={popt_pw[1]:.4f}",
                'rmse': round(float(rmse_pw), 6),
                'aic': round(float(aic_pw), 4),
                'bic': round(float(bic_pw), 4)
            })
        except Exception:
            tail_records.append({
                'configuration': config, 'model': 'power_law_tail',
                'parameters': 'FAILED', 'rmse': np.nan, 'aic': np.nan, 'bic': np.nan
            })

    stats_df = pd.DataFrame(stats_records)
    out_stats = OUTPUT_DIR / 'avalanche_statistics.csv'
    stats_df.to_csv(out_stats, index=False)
    print(f"    Saved: {out_stats.name}")
    
    tail_df = pd.DataFrame(tail_records)
    out_tail = OUTPUT_DIR / 'avalanche_tail_models.csv'
    tail_df.to_csv(out_tail, index=False)
    print(f"    Saved: {out_tail.name}")
    
    return stats_df, tail_df


def module_3_universal_relaxation_collapse():
    print(" -> Executing Module 3: Universal Relaxation Collapse...")
    raw_df = pd.read_csv(INPUT_SEARCH_DYNAMICS)
    
    raw_df = raw_df.sort_values(['graph', 'configuration', 'iteration']).copy()
    
    # Calculate E(t) = (cut(t) - final) / (initial - final) without problematic apply
    group_list = []
    for (graph, config), g in raw_df.groupby(['graph', 'configuration'], as_index=False):
        g = g.copy()
        initial = g['edge_cut'].iloc[0]
        final = g['edge_cut'].min()
        denom = initial - final
        if denom > 1e-6:
            g['edge_cut_norm'] = (g['edge_cut'] - final) / denom
        else:
            g['edge_cut_norm'] = 0.0
        group_list.append(g)
        
    df_norm = pd.concat(group_list, ignore_index=True)
    
    # Aggregate configuration + iteration
    master_records = []
    fig, ax = plt.subplots(figsize=(10, 6))
    
    for config in CONFIGS:
        cdf = df_norm[df_norm['configuration'] == config]
        if cdf.empty:
            continue
            
        stats = cdf.groupby('iteration')['edge_cut_norm'].agg(['mean', 'std']).reset_index()
        stats['configuration'] = config
        
        master_records.append(stats[['configuration', 'iteration', 'mean', 'std']])
        
        t = stats['iteration'].values
        m = stats['mean'].values
        s = stats['std'].values
        
        ax.plot(t, m, label=config, linewidth=2, alpha=0.9)
        ax.fill_between(t, np.clip(m - s, 0, None), m + s, alpha=0.12)
        
    master_df = pd.concat(master_records, ignore_index=True)
    out_master = OUTPUT_DIR / 'master_relaxation_curves.csv'
    master_df.to_csv(out_master, index=False)
    print(f"    Saved: {out_master.name}")
    
    ax.set_title("Universal Relaxation Collapse E(t) = [Cut(t) - Final] / [Initial - Final]")
    ax.set_xlabel("Iteration (t)")
    ax.set_ylabel("Normalized Edge Cut E(t) (Mean ± Std)")
    ax.set_ylim(-0.05, 1.05)
    ax.legend(title="Configuration", bbox_to_anchor=(1.02, 1), loc='upper left')
    plt.tight_layout()
    
    out_fig = OUTPUT_DIR / 'master_relaxation_collapse.png'
    fig.savefig(out_fig)
    plt.close()
    print(f"    Saved: {out_fig.name}")
    
    return master_df, df_norm


def module_4_topology_coupling(df_norm):
    print(" -> Executing Module 4: Topology Coupling Analysis...")
    topo_df = pd.read_csv(INPUT_TOPOLOGY)
    aval_df = pd.read_csv(INPUT_AVALANCHE_DIST)
    
    df_sorted = df_norm.sort_values(['graph', 'configuration', 'iteration'])
    
    # 1. initial_slope
    slopes = []
    for (graph, config), g in df_sorted.groupby(['graph', 'configuration']):
        if len(g) >= 2:
            y0 = g['edge_cut_norm'].iloc[0]
            y1 = g['edge_cut_norm'].iloc[1]
            slopes.append({'graph': graph, 'configuration': config, 'initial_slope': y1 - y0})
    slope_df = pd.DataFrame(slopes)
    
    # 2. plateau_iteration (stall window = 5)
    stall_window = 5
    plateaus = []
    for (graph, config), g in df_sorted.groupby(['graph', 'configuration']):
        cuts = g['edge_cut'].values
        iters = g['iteration'].values
        plat_t = iters[-1]
        for i in range(len(cuts) - stall_window):
            if np.all(cuts[i + 1 : i + 1 + stall_window] >= cuts[i]):
                plat_t = iters[i]
                break
        plateaus.append({'graph': graph, 'configuration': config, 'plateau_iteration': plat_t})
    plateau_df = pd.DataFrame(plateaus)
    
    # 3. mean_acceptance
    acc_df = df_norm.groupby(['graph', 'configuration'])['acceptance_ratio'].mean().reset_index()
    acc_df.rename(columns={'acceptance_ratio': 'mean_acceptance'}, inplace=True)
    
    # 4. avalanche_mean
    pos_aval = aval_df[aval_df['delta'] > 0]
    aval_mean_df = pos_aval.groupby(['graph', 'configuration'])['delta'].mean().reset_index()
    aval_mean_df.rename(columns={'delta': 'avalanche_mean'}, inplace=True)
    
    # 5. relaxation_time: iteration where E(t) <= 1/e
    tau_target = 1.0 / np.e
    taus = []
    for (graph, config), g in df_sorted.groupby(['graph', 'configuration']):
        iters = g['iteration'].values
        e_vals = g['edge_cut_norm'].values
        tau_val = iters[-1]
        for t, e in zip(iters, e_vals):
            if e <= tau_target:
                tau_val = t
                break
        taus.append({'graph': graph, 'configuration': config, 'relaxation_time': tau_val})
    tau_df = pd.DataFrame(taus)
    
    # Merge all dynamic metrics per graph & config
    dyn = slope_df.merge(plateau_df, on=['graph', 'configuration'], how='outer')
    dyn = dyn.merge(acc_df, on=['graph', 'configuration'], how='outer')
    dyn = dyn.merge(aval_mean_df, on=['graph', 'configuration'], how='outer')
    dyn = dyn.merge(tau_df, on=['graph', 'configuration'], how='outer')
    dyn['avalanche_mean'] = dyn['avalanche_mean'].fillna(0.0)
    
    merged = dyn.merge(topo_df, on='graph', how='inner')
    
    dynamic_vars = ['initial_slope', 'plateau_iteration', 'mean_acceptance', 'avalanche_mean', 'relaxation_time']
    topo_vars = [c for c in topo_df.columns if c != 'graph' and pd.api.types.is_numeric_dtype(topo_df[c])]
    
    corr_records = []
    for config in CONFIGS:
        c_data = merged[merged['configuration'] == config]
        if c_data.empty:
            continue
            
        for d_var in dynamic_vars:
            for t_var in topo_vars:
                d_s = c_data[d_var].astype(float)
                t_s = c_data[t_var].astype(float)
                
                if d_s.std() == 0 or t_s.std() == 0:
                    r_p, r_s = np.nan, np.nan
                else:
                    r_p = d_s.corr(t_s, method='pearson')
                    r_s = d_s.corr(t_s, method='spearman')
                    
                corr_records.append({
                    'configuration': config,
                    'dynamic_variable': d_var,
                    'topology_feature': t_var,
                    'pearson_r': round(float(r_p), 6) if not np.isnan(r_p) else np.nan,
                    'spearman_rho': round(float(r_s), 6) if not np.isnan(r_s) else np.nan
                })
                
    corr_df = pd.DataFrame(corr_records)
    out_corr = OUTPUT_DIR / 'topology_dynamics_correlation.csv'
    corr_df.to_csv(out_corr, index=False)
    print(f"    Saved: {out_corr.name}")
    return corr_df


# ==============================================================================
# MAIN EXECUTOR & STRICT VALIDATION
# ==============================================================================

def main():
    print("================================================================================")
    print("STARTING OBSERVATORY ADVANCED ANALYSIS PIPELINE")
    print("================================================================================")
    print(f" -> Resolved Repository Root: {REPO_ROOT}")
    
    # Validation step: Check missing files
    missing = []
    for name, path in REQUIRED_INPUTS.items():
        if not path.exists():
            missing.append(f"{name} (expected at {path})")
            
    if missing:
        print("\n[FATAL ERROR] MISSING REQUIRED INPUT FILE(S):")
        for m in missing:
            print(f"  - {m}")
        print("\nPipeline execution halted.")
        sys.exit(1)
        
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    regime_df = module_1_relaxation_classification()
    stats_df, tail_df = module_2_avalanche_statistics()
    master_df, df_norm = module_3_universal_relaxation_collapse()
    corr_df = module_4_topology_coupling(df_norm)
    
    print("\n================================================")
    print("OBSERVATORY ADVANCED COMPLETE")
    print("================================================")
    print("Generated Artifacts in results/observatory/:")
    print("  - relaxation_regime.csv")
    print("  - avalanche_statistics.csv")
    print("  - avalanche_tail_models.csv")
    print("  - master_relaxation_curves.csv")
    print("  - topology_dynamics_correlation.csv")
    print("  - master_relaxation_collapse.png")
    print("================================================\n")

if __name__ == '__main__':
    main()
