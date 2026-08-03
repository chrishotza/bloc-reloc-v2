#!/usr/bin/env python3

import pandas as pd
import numpy as np

# ==========================================================
# LOAD
# ==========================================================

topo=pd.read_csv("results/topology_multivariate.csv")

dyn=pd.read_csv("results/search_dynamics.csv")

land=pd.read_csv("results/landscape_index.csv")

# ==========================================================
# FINAL RESULT PER RUN
# ==========================================================

final=(
    dyn.sort_values("iteration")
       .groupby(["graph","configuration"])
       .tail(1)
       .copy()
)

# ==========================================================
# EARLY DYNAMICS
# ==========================================================

rows=[]

for (graph,cfg),g in dyn.groupby(["graph","configuration"]):

    g=g.sort_values("iteration").reset_index(drop=True)

    early=g[g.iteration<=4].copy()

    x=early.iteration.values.astype(float)

    edge=early.edge_cut.values.astype(float)

    cost=early.weighted_cost.values.astype(float)

    slope_edge=np.polyfit(x,edge,1)[0]

    slope_cost=np.polyfit(x,cost,1)[0]

    plateau=int(
        g[g.edge_cut==g.edge_cut.iloc[-1]]
        .iteration
        .min()
    )

    rows.append({

        "graph":graph,
        "configuration":cfg,

        "early_acceptance_mean":
            early.acceptance_ratio.mean(),

        "early_acceptance_std":
            early.acceptance_ratio.std(),

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

        "runtime":
            final[
                (final.graph==graph) &
                (final.configuration==cfg)
            ].runtime.iloc[0],

        "final_edge_cut":
            final[
                (final.graph==graph) &
                (final.configuration==cfg)
            ].edge_cut.iloc[0]

    })

early_df=pd.DataFrame(rows)

# ==========================================================
# LANDSCAPE (PIVOT)
# ==========================================================

land_pivot=(
    land.pivot_table(
        index=["graph","family"],
        columns="variant",
        values=[
            "p_improve",
            "p_worsen",
            "mean_gain",
            "std_gain",
            "smoothness",
            "success_ratio",
            "landscape_index"
        ]
    )
)

land_pivot.columns=[
    f"{a}_{b}"
    for a,b in land_pivot.columns
]

land_pivot=land_pivot.reset_index()

# ==========================================================
# TOPOLOGY
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
# MERGE
# ==========================================================

master=early_df.merge(
    topo,
    on="graph",
    how="left"
)

master=master.merge(
    land_pivot,
    on=["graph","family"],
    how="left"
)

# ==========================================================
# BEST POLICY LABEL
# ==========================================================

best=(
    master.sort_values("final_edge_cut")
          .groupby("graph")
          .head(1)
          [["graph","configuration"]]
)

best.columns=[
    "graph",
    "best_policy"
]

master=master.merge(
    best,
    on="graph"
)

# ==========================================================
# SAVE
# ==========================================================

master.to_csv(
    "results/regime_dataset.csv",
    index=False
)

print("="*80)
print("REGIME DATASET")
print("="*80)

print()

print("Rows :",len(master))
print("Cols :",len(master.columns))

print()

print(master.columns.tolist())

print()

print("="*80)
print("BEST POLICY")
print("="*80)

print(
    master.best_policy
          .value_counts()
)

print()

print("Saved -> results/regime_dataset.csv")

