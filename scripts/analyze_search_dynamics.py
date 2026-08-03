#!/usr/bin/env python3

import pandas as pd

FILE="results/search_dynamics.csv"

df=pd.read_csv(FILE)

print("="*90)
print("SEARCH DYNAMICS ANALYSIS")
print("="*90)

print()
print("Rows:",len(df))
print("Graphs:",df.graph.nunique())
print("Families:",df.family.nunique())
print("Configurations:",df.configuration.unique())

# -------------------------------------------------

final=(
    df.sort_values("iteration")
      .groupby(["graph","configuration"])
      .tail(1)
)

print()
print("="*90)
print("FINAL EDGE CUT (GLOBAL)")
print("="*90)

print(
    final.groupby("configuration")
         .agg(
             mean_cut=("edge_cut","mean"),
             median_cut=("edge_cut","median"),
             std=("edge_cut","std"),
             runtime=("runtime","mean")
         )
         .sort_values("mean_cut")
         .round(3)
)

# -------------------------------------------------

print()
print("="*90)
print("FINAL EDGE CUT BY FAMILY")
print("="*90)

for fam in sorted(final.family.unique()):

    print()
    print(fam)

    print(
        final[final.family==fam]
        .groupby("configuration")
        .agg(
            mean_cut=("edge_cut","mean"),
            median=("edge_cut","median"),
            runtime=("runtime","mean")
        )
        .sort_values("mean_cut")
        .round(3)
    )

# -------------------------------------------------

print()
print("="*90)
print("MEAN ACCEPTANCE RATIO")
print("="*90)

acc=(
    df.groupby(["configuration","iteration"])
      .acceptance_ratio
      .mean()
      .reset_index()
)

print(
    acc.groupby("configuration")
       .acceptance_ratio
       .agg(["mean","max","min"])
       .round(4)
)

# -------------------------------------------------

print()
print("="*90)
print("AVERAGE EDGE CUT CURVE")
print("="*90)

curve=(
    df.groupby(["configuration","iteration"])
      .edge_cut
      .mean()
      .reset_index()
)

for cfg in curve.configuration.unique():

    print()
    print(cfg)

    print(
        curve[curve.configuration==cfg]
        .head(10)
        .to_string(index=False)
    )

    print("...")

    print(
        curve[curve.configuration==cfg]
        .tail(10)
        .to_string(index=False)
    )

# -------------------------------------------------

print()
print("="*90)
print("PLATEAU ESTIMATION")
print("="*90)

rows=[]

for (graph,cfg),g in df.groupby(["graph","configuration"]):

    g=g.sort_values("iteration")

    last=g.edge_cut.iloc[-1]

    plateau=g[g.edge_cut==last].iteration.min()

    rows.append({
        "graph":graph,
        "configuration":cfg,
        "plateau":plateau
    })

plateau=pd.DataFrame(rows)

print(
    plateau.groupby("configuration")
           .plateau
           .agg(["mean","median","min","max"])
           .round(2)
)

print()
print("="*90)
print("DONE")
print("="*90)

