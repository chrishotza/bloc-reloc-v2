#!/usr/bin/env python3

import pandas as pd
import numpy as np

# ==========================================================
# LOAD
# ==========================================================

topo=pd.read_csv("results/topology_multivariate.csv")
dyn=pd.read_csv("results/search_dynamics.csv")

# ==========================================================
# REMOVE NON-PHYSICAL FEATURES
# ==========================================================

dropcols=[

    "PC1",
    "PC2",
    "cluster",
    "improvement",
    "improvement_%"

]

topo=topo.drop(
    columns=[c for c in dropcols if c in topo.columns]
)

# ==========================================================
# BEST POLICY (TARGET)
# ==========================================================

final=(

    dyn
    .sort_values("iteration")
    .groupby(["graph","configuration"])
    .tail(1)

)

best=(

    final
    .sort_values("edge_cut")
    .groupby("graph")
    .head(1)

)[["graph","configuration"]]

best.columns=["graph","best_policy"]

# ==========================================================
# BASELINE ONLY
# ==========================================================

baseline=dyn[
    dyn.configuration=="baseline"
].copy()

rows=[]

for graph,g in baseline.groupby("graph"):

    g=g.sort_values("iteration")

    early=g[g.iteration<=4].copy()

    x=early.iteration.values.astype(float)

    edge=early.edge_cut.values.astype(float)

    cost=early.weighted_cost.values.astype(float)

    slope_edge=np.polyfit(x,edge,1)[0]

    slope_cost=np.polyfit(x,cost,1)[0]

    plateau=int(
        g[g.edge_cut==g.edge_cut.iloc[-1]]
         .iteration.min()
    )

    rows.append({

        "graph":graph,

        "early_acceptance_mean":
            early.acceptance_ratio.mean(),

        "early_acceptance_std":
            early.acceptance_ratio.std(),

        "early_acceptance_max":
            early.acceptance_ratio.max(),

        "early_acceptance_min":
            early.acceptance_ratio.min(),

        "early_edgecut_slope":
            slope_edge,

        "early_cost_slope":
            slope_cost,

        "edgecut_after5":
            edge[-1],

        "cost_after5":
            cost[-1],

        "plateau_iteration":
            plateau,

        "runtime_baseline":
            g.runtime.iloc[-1]

    })

baseline_features=pd.DataFrame(rows)

# ==========================================================
# MERGE
# ==========================================================

dataset=(
    topo
    .merge(
        baseline_features,
        on="graph",
        how="inner"
    )
    .merge(
        best,
        on="graph",
        how="inner"
    )
)

dataset.to_csv(
    "results/regime_dataset_clean.csv",
    index=False
)

print("="*80)
print("CLEAN REGIME DATASET")
print("="*80)

print()

print("Rows :",len(dataset))
print("Cols :",len(dataset.columns))

print()

print(dataset.columns.tolist())

print()

print("="*80)
print("BEST POLICY")
print("="*80)

print(
    dataset.best_policy.value_counts()
)

print()

print("Saved -> results/regime_dataset_clean.csv")

