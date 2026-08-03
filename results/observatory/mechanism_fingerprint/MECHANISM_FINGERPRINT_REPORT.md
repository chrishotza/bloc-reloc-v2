# BLOC-RELOC V2 MECHANISM FINGERPRINT

**Date of Execution:** 2026-08-03 18:51:01  
**Evaluated Configurations:** 6  

---

## Configuration fingerprints

The table below summarizes the dynamic fingerprint metrics and descriptive behavioral vectors across all evaluated BLOC-RELOC v2 configurations:

| Configuration | Class | Quality | Persistence | Exploration | Balance | Convergence Speed | Dynamic Lifetime | Avalanches | Relaxation Regime | Mechanism Vector |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|:---|
| **baseline** | `Premature-convergent` | 0.0000 | 0.0244 | 0.0000 | 0.0081 | 0.25 | 8.0 | 448 | `stretched exponential dominated` | `QUALITY_LOW | PERSISTENCE_LOW | EXPLORATION_LOW | PREMATURE_CONVERGENT` |
| **affinity** | `Premature-convergent` | 0.3033 | 0.0000 | 0.0704 | 0.1246 | 0.25 | 7.0 | 543 | `stretched exponential dominated` | `QUALITY_LOW | PERSISTENCE_LOW | EXPLORATION_LOW | PREMATURE_CONVERGENT` |
| **periodic** | `Balanced` | 0.8529 | 1.0000 | 0.6687 | 0.8405 | 0.1 | 48.0 | 1329 | `stretched exponential dominated` | `QUALITY_HIGH | PERSISTENCE_HIGH | EXPLORATION_HIGH | BALANCED` |
| **reactive** | `Balanced` | 0.7919 | 1.0000 | 1.0000 | 0.9306 | 0.083333 | 48.0 | 1807 | `power-law candidate` | `QUALITY_HIGH | PERSISTENCE_HIGH | EXPLORATION_HIGH | BALANCED` |
| **affinity_periodic** | `Balanced` | 1.0000 | 0.7561 | 0.5866 | 0.7809 | 0.125 | 38.0 | 1266 | `power-law candidate` | `QUALITY_HIGH | PERSISTENCE_HIGH | EXPLORATION_MEDIUM | BALANCED` |
| **affinity_reactive** | `Balanced` | 0.8212 | 0.6341 | 0.8849 | 0.7801 | 0.083333 | 33.0 | 1675 | `power-law candidate` | `QUALITY_HIGH | PERSISTENCE_MEDIUM | EXPLORATION_HIGH | BALANCED` |

---

## Behavioral groups

### Balanced
- **Characteristics:** Demonstrates a robust trade-off between search persistence, dynamic activity, and optimal final cut quality.
- **Configurations:** 
  - `periodic`
  - `reactive`
  - `affinity_periodic`
  - `affinity_reactive`

### Premature-convergent
- **Characteristics:** Early dynamic collapse characterized by low extinction times, minimal avalanche activity, and rapid loss of reconfiguration capability.
- **Configurations:**
  - `baseline`
  - `affinity`

### Explorer
- **Characteristics:** Prolonged dynamic lifetime with high avalanche occurrence and extensive phase-space exploration.
- **Configurations:**
  - *None identified*

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
