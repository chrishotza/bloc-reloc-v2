#!/usr/bin/env python3

import numpy as np
import pandas as pd

# ==========================================================
# LOAD
# ==========================================================

dyn=pd.read_csv("results/search_dynamics.csv")
topo=pd.read_csv("results/topology_multivariate.csv")

dyn=dyn.sort_values(
    ["graph","configuration","iteration"]
)

# ==========================================================
# MECHANISM FEATURES
# ==========================================================

rows=[]

for (graph,cfg),g in dyn.groupby(["graph","configuration"]):

    g=g.sort_values("iteration").reset_index(drop=True)

    edge=g.edge_cut.values.astype(float)
    acc=g.accepted.values.astype(float)
    rej=g.rejected.values.astype(float)

    total=acc+rej

    ratio=np.divide(
        acc,
        total,
        out=np.zeros_like(acc),
        where=total>0
    )

    # ---------------------------------------------
    # plateau
    # ---------------------------------------------

    final=edge[-1]

    plateau=int(
        np.where(edge==final)[0][0]
    )

    # ---------------------------------------------
    # improvement
    # ---------------------------------------------

    improvement=edge[0]-edge[-1]

    # ---------------------------------------------
    # active iterations
    # ---------------------------------------------

    active=int(
        np.sum(np.diff(edge)!=0)
    )

    # ---------------------------------------------
    # first slope
    # ---------------------------------------------

    if len(edge)>=5:

        slope=np.polyfit(
            np.arange(5),
            edge[:5],
            1
        )[0]

    else:

        slope=np.nan

    # ---------------------------------------------
    # acceptance
    # ---------------------------------------------

    mean_acc=ratio.mean()

    max_acc=ratio.max()

    last_nonzero=np.where(acc>0)[0]

    if len(last_nonzero):

        last_accept=int(last_nonzero[-1])

    else:

        last_accept=-1

    rows.append({

        "graph":graph,
        "configuration":cfg,

        "plateau_iteration":plateau,

        "active_iterations":active,

        "last_accept_iteration":last_accept,

        "initial_slope":slope,

        "initial_edgecut":edge[0],
        "final_edgecut":edge[-1],

        "total_improvement":improvement,

        "acceptance_mean":mean_acc,
        "acceptance_max":max_acc,

        "accepted_total":acc.sum(),
        "rejected_total":rej.sum(),

        "runtime":g.runtime.iloc[0]

    })

mech=pd.DataFrame(rows)

# ==========================================================
# MERGE TOPOLOGY
# ==========================================================

dropcols=[

    "PC1",
    "PC2",
    "cluster",
    "improvement",
    "improvement_%"

]

topo=topo.drop(
    columns=[c for c in dropcols if c in topo.columns],
    errors="ignore"
)

full=mech.merge(
    topo,
    on="graph",
    how="left"
)

# ==========================================================
# FAMILY SUMMARY
# ==========================================================

print("="*90)
print("MECHANISM SUMMARY")
print("="*90)

summary=(

    full
    .groupby(["family","configuration"])
    .agg(

        plateau=("plateau_iteration","mean"),

        active=("active_iterations","mean"),

        improvement=("total_improvement","mean"),

        acceptance=("acceptance_mean","mean"),

        runtime=("runtime","mean")

    )

)

print(summary.round(3))

# ==========================================================
# CORRELATIONS
# ==========================================================

print()
print("="*90)
print("CORRELATIONS WITH IMPROVEMENT")
print("="*90)

numeric=full.select_dtypes(include=np.number)

corr=numeric.corr()["total_improvement"]

corr=corr.drop("total_improvement")

corr=corr.reindex(

    corr.abs().sort_values(
        ascending=False
    ).index

)

print(corr.head(30).round(4))

# ==========================================================
# SAVE
# ==========================================================

full.to_csv(
    "results/mechanism_dataset.csv",
    index=False
)

corr.to_csv(
    "results/mechanism_correlations.csv",
    header=["correlation"]
)

summary.to_csv(
    "results/mechanism_family_summary.csv"
)

print()
print("="*90)
print("FILES GENERATED")
print("="*90)
print("results/mechanism_dataset.csv")
print("results/mechanism_correlations.csv")
print("results/mechanism_family_summary.csv")
