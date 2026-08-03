# BLOC-RELOC V2 DYNAMICS OBSERVATORY
## EXECUTIVE SUMMARY REPORT

**Date of Execution:** 2026-08-03 18:25:04  
**Configurations Analyzed:** 6  

---

### 1. Performance Ranking (Solution Quality)
Ranked by `mean_final_edge_cut` (lower values indicate superior partition quality):

| Rank | Configuration | Mean Final Edge Cut | Std Edge Cut | Runtime (s) |
|:---:|:---|:---:|:---:|:---:|
| 1 | **affinity_periodic** | 528.6583 | 220.8860 | 30.7621 |
| 2 | **periodic** | 536.6833 | 212.5125 | 24.1236 |
| 3 | **affinity_reactive** | 538.4083 | 214.3031 | 26.9390 |
| 4 | **reactive** | 540.0083 | 210.7996 | 21.7825 |
| 5 | **affinity** | 566.6583 | 208.8261 | 10.0781 |
| 6 | **baseline** | 583.2000 | 206.7719 | 7.7585 |

---

### 2. Dynamic Survival Ranking
Ranked by search persistence (`time_to_survival_50` and `extinction_time`):

| Dynamic Rank | Configuration | Time to Survival 50% | Extinction Time | Survival t=5 | Survival t=10 | Survival t=15 |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| 1 | **reactive** | 12 | 48 | 0.9250 | 0.6167 | 0.4417 |
| 2 | **affinity_reactive** | 12 | 33 | 0.8917 | 0.5500 | 0.3833 |
| 3 | **periodic** | 10 | 48 | 0.7167 | 0.4583 | 0.2500 |
| 4 | **affinity_periodic** | 8 | 38 | 0.6750 | 0.3917 | 0.2333 |
| 5 | **baseline** | 4 | 8 | 0.1000 | 0.0000 | 0.0000 |
| 6 | **affinity** | 4 | 7 | 0.2333 | 0.0000 | 0.0000 |

---

### 3. Dynamic Search Activity Ranking
Ranked by total avalanche dynamics and exploration active iterations:

| Configuration | Total Avalanches | Mean Active Iterations | Mean Delta | Median Delta |
|:---|:---:|:---:|:---:|:---:|
| **reactive** | 1807 | 15.26 | 12.1555 | 3.0000 |
| **affinity_reactive** | 1675 | 13.72 | 13.0991 | 3.0000 |
| **periodic** | 1329 | 11.68 | 11.3424 | 2.0000 |
| **affinity_periodic** | 1266 | 10.32 | 12.7488 | 3.0000 |
| **affinity** | 543 | 4.55 | 33.9926 | 13.0000 |
| **baseline** | 448 | 3.73 | 37.4598 | 16.0000 |

---

### 4. Relaxation Regime Classification
Summary of dynamic model fitting per configuration:

| Configuration | Best Relaxation Model | Relaxation Regime |
|:---|:---|:---|
| **baseline** | stretched_exp | `stretched exponential dominated` |
| **affinity** | stretched_exp | `stretched exponential dominated` |
| **periodic** | stretched_exp | `stretched exponential dominated` |
| **reactive** | power_law | `power-law candidate` |
| **affinity_periodic** | power_law | `power-law candidate` |
| **affinity_reactive** | power_law | `power-law candidate` |

---

### 5. Key Correlation Highlights
Top correlation pairs extracted between dynamic variables and optimization performance:

| Dynamic Variable | Performance Variable | Pearson r | Spearman rho |
|:---|:---|:---:|:---:|
| `mean_delta` | `mean_delta_improvement` | 1.0000 | 1.0000 |
| `time_to_survival_10` | `mean_delta_improvement` | -0.9762 | -0.7143 |
| `mean_delta` | `mean_final_edge_cut` | 0.9665 | 0.7143 |
| `extinction_time` | `mean_delta_improvement` | -0.9571 | -0.9276 |
| `mean_active_iterations` | `mean_delta_improvement` | -0.9318 | -0.7143 |
| `total_avalanches` | `mean_delta_improvement` | -0.9273 | -0.7143 |
| `time_to_survival_10` | `mean_final_edge_cut` | -0.9099 | -0.4286 |
| `time_to_survival_50` | `mean_delta_improvement` | -0.9083 | -0.6473 |
| `extinction_time` | `mean_final_edge_cut` | -0.8813 | -0.6088 |
| `total_avalanches` | `mean_final_edge_cut` | -0.8452 | -0.4286 |

---

### 6. Generated Visual Artifacts
- **Performance vs Survival:** `results/observatory/executive_report/performance_vs_survival.png`
- **Activity vs Quality:** `results/observatory/executive_report/dynamic_activity_vs_quality.png`

================================================================================
*Report generated automatically by `generate_observatory_executive_report.py`*
