#!/usr/bin/env python3

import pandas as pd

df = pd.read_csv("results/affinity_ablation.csv")

pivot = df.pivot_table(
    index="graph",
    columns="variant",
    values="edge_cut"
)

pivot["improvement"] = pivot["baseline"] - pivot["affinity_modified"]
pivot["improvement_%"] = 100 * pivot["improvement"] / pivot["baseline"]

pivot["family"] = pivot.index.str.extract(r"^([a-z_]+)_\d+")

print("\n==============================")
print("GLOBAL")
print("==============================")

print(f"Graphs : {len(pivot)}")
print(f"Wins   : {(pivot.improvement>0).sum()}")
print(f"Losses : {(pivot.improvement<0).sum()}")
print(f"Draws  : {(pivot.improvement==0).sum()}")

print()
print("Mean improvement %")
print(round(pivot.improvement_.mean() if False else pivot["improvement_%"].mean(),3))

print()
print("==============================")
print("BY FAMILY")
print("==============================")

summary = (
    pivot
    .groupby("family")
    .agg(
        graphs=("family","count"),
        wins=("improvement",lambda x:(x>0).sum()),
        losses=("improvement",lambda x:(x<0).sum()),
        draws=("improvement",lambda x:(x==0).sum()),
        mean_improvement=("improvement_%","mean"),
        median_improvement=("improvement_%","median")
    )
)

print(summary.round(3))

print()
print("==============================")
print("BEST 15")
print("==============================")
print(
    pivot.sort_values("improvement_%",ascending=False)[
        ["improvement_%"]
    ].head(15)
)

print()
print("==============================")
print("WORST 15")
print("==============================")
print(
    pivot.sort_values("improvement_%")[
        ["improvement_%"]
    ].head(15)
)

