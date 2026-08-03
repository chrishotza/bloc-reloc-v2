# BLOC-RELOC V2 MECHANISM AUDIT REPORT

**Date of Execution:** 2026-08-03 18:48:04  
**Configurations Evaluated:** 6  

---

## 1. Configuration Profiles Summary

The table below summarizes the interpretative mechanism profile, assigned class, and dynamic metrics across all evaluated BLOC-RELOC v2 configurations:

| Configuration | Class | Quality Rank | Persistence Rank | Exploration Rank | Final Edge Cut | Extinction Time | Total Avalanches | Relaxation Regime |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| **baseline** | `Premature-convergent` | 6 | 5 | 6 | 583.2000 | 8.0 | 448 | `stretched exponential dominated` |
| **affinity** | `Premature-convergent` | 5 | 6 | 5 | 566.6583 | 7.0 | 543 | `stretched exponential dominated` |
| **periodic** | `Balanced` | 2 | 1 | 3 | 536.6833 | 48.0 | 1329 | `stretched exponential dominated` |
| **reactive** | `Balanced` | 4 | 1 | 1 | 540.0083 | 48.0 | 1807 | `power-law candidate` |
| **affinity_periodic** | `Balanced` | 1 | 3 | 4 | 528.6583 | 38.0 | 1266 | `power-law candidate` |
| **affinity_reactive** | `Balanced` | 3 | 4 | 2 | 538.4083 | 33.0 | 1675 | `power-law candidate` |

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
| **baseline** | 0.0000 | 0.0244 | 0.0000 | 0.0081 |
| **affinity** | 0.3033 | 0.0000 | 0.0704 | 0.1246 |
| **periodic** | 0.8529 | 1.0000 | 0.6687 | 0.8405 |
| **reactive** | 0.7919 | 1.0000 | 1.0000 | 0.9306 |
| **affinity_periodic** | 1.0000 | 0.7561 | 0.5866 | 0.7809 |
| **affinity_reactive** | 0.8212 | 0.6341 | 0.8849 | 0.7801 |

---

## 4. Topology-Dynamics Coupling Highlights

Top absolute correlations between structural graph topology features and dynamic search activity:

| Dynamic Variable | Topology Feature | Pearson r | Spearman rho | |Spearman| |
|:---|:---|:---:|:---:|:---:|
| `mean_acceptance` | `transitivity` | 0.7421 | 0.8223 | 0.8223 |
| `mean_acceptance` | `clustering` | 0.7505 | 0.8174 | 0.8174 |
| `mean_acceptance` | `transitivity` | 0.5884 | 0.7520 | 0.7520 |
| `mean_acceptance` | `clustering` | 0.5974 | 0.7374 | 0.7374 |
| `avalanche_mean` | `PC1` | 0.6563 | 0.7186 | 0.7186 |
| `mean_acceptance` | `transitivity` | 0.5923 | 0.7062 | 0.7062 |
| `mean_acceptance` | `clustering` | 0.5989 | 0.7023 | 0.7023 |
| `avalanche_mean` | `modularity` | 0.6736 | 0.6938 | 0.6938 |
| `initial_slope` | `density` | -0.5584 | -0.6744 | 0.6744 |
| `initial_slope` | `avg_degree` | -0.5584 | -0.6744 | 0.6744 |

---

## 5. Methodological Limitations

- **Sample Size Constraints:** Analysis is strictly bounded to the 6 evaluated algorithmic configurations within the benchmark suite.
- **Exploratory Correlation Scope:** High statistical correlation between dynamic persistence and solution quality reflects empirical co-occurrence rather than direct mechanistic causation.
- **No Causal Inference:** Results serve for auditing behavioral regimes and guiding heuristic design; causal validation requires controlled ablation interventions.

================================================================================
*Report generated automatically by `mechanism_profile_audit.py`*
