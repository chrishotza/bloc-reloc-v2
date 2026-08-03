#!/usr/bin/env python3

import os
import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt

RESULTS="results"
INPUT=os.path.join(RESULTS,"search_dynamics.csv")

OUT_RELAX=os.path.join(RESULTS,"relaxation_curves.csv")
OUT_ACC=os.path.join(RESULTS,"acceptance_curves.csv")
OUT_DELTA=os.path.join(RESULTS,"delta_distribution.csv")

FIG1=os.path.join(RESULTS,"figure_relaxation.png")
FIG2=os.path.join(RESULTS,"figure_acceptance.png")
FIG3=os.path.join(RESULTS,"figure_delta_histograms.png")

if not os.path.exists(INPUT):
    raise FileNotFoundError(INPUT)

df=pd.read_csv(INPUT)

df=df.sort_values(
    ["configuration","graph","iteration"]
).reset_index(drop=True)

# ============================================================
# ACCEPTANCE RATIO
# ============================================================

total=df.accepted+df.rejected

df["acceptance_ratio"]=np.divide(
    df.accepted,
    total,
    out=np.zeros(len(df)),
    where=total>0
)

# ============================================================
# RELAXATION CURVES
# ============================================================

relax=(
    df
    .groupby(["configuration","iteration"])
    .agg(
        edge_cut_mean=("edge_cut","mean"),
        edge_cut_std=("edge_cut","std")
    )
    .reset_index()
)

relax.to_csv(
    OUT_RELAX,
    index=False
)

# ============================================================
# ACCEPTANCE CURVES
# ============================================================

acc=(
    df
    .groupby(["configuration","iteration"])
    .agg(
        acceptance_mean=("acceptance_ratio","mean"),
        acceptance_std=("acceptance_ratio","std")
    )
    .reset_index()
)

acc.to_csv(
    OUT_ACC,
    index=False
)

# ============================================================
# ENERGY DELTA
# ============================================================

rows=[]

for (graph,cfg),g in df.groupby(
    ["graph","configuration"]
):

    g=g.sort_values("iteration")

    edge=g.edge_cut.values.astype(float)

    delta=edge[:-1]-edge[1:]

    for d in delta:

        rows.append({

            "graph":graph,

            "configuration":cfg,

            "delta":d

        })

delta=pd.DataFrame(rows)

delta.to_csv(
    OUT_DELTA,
    index=False
)

# ============================================================
# FIGURE 1
# ============================================================

plt.figure(figsize=(10,6))

for cfg,g in relax.groupby("configuration"):

    plt.plot(
        g.iteration,
        g.edge_cut_mean,
        label=cfg,
        linewidth=2
    )

plt.xlabel("Iteration")
plt.ylabel("Mean Edge Cut")
plt.title("Average Relaxation Curves")
plt.grid(alpha=.3)
plt.legend()
plt.tight_layout()
plt.savefig(FIG1,dpi=300)
plt.close()

# ============================================================
# FIGURE 2
# ============================================================

plt.figure(figsize=(10,6))

for cfg,g in acc.groupby("configuration"):

    plt.plot(
        g.iteration,
        g.acceptance_mean,
        label=cfg,
        linewidth=2
    )

plt.xlabel("Iteration")
plt.ylabel("Acceptance Ratio")
plt.title("Acceptance Dynamics")
plt.grid(alpha=.3)
plt.legend()
plt.tight_layout()
plt.savefig(FIG2,dpi=300)
plt.close()

# ============================================================
# FIGURE 3
# ============================================================

configs=sorted(delta.configuration.unique())

n=len(configs)

cols=2
rows=int(np.ceil(n/cols))

plt.figure(figsize=(10,rows*3))

for i,cfg in enumerate(configs,1):

    plt.subplot(rows,cols,i)

    x=delta[
        delta.configuration==cfg
    ].delta

    plt.hist(
        x,
        bins=20
    )

    plt.title(cfg)

    plt.xlabel("Δ Edge Cut")

    plt.ylabel("Frequency")

plt.tight_layout()

plt.savefig(
    FIG3,
    dpi=300
)

plt.close()

# ============================================================
# SUMMARY
# ============================================================

print("="*90)
print("SEARCH MECHANISM FIGURES")
print("="*90)

print()
print("Input")
print(INPUT)

print()
print("Generated CSV")
print(OUT_RELAX)
print(OUT_ACC)
print(OUT_DELTA)

print()
print("Generated Figures")
print(FIG1)
print(FIG2)
print(FIG3)

print()
print("="*90)
print("DONE")
print("="*90)
