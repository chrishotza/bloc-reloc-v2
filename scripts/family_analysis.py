#!/usr/bin/env python3

import pandas as pd

df = pd.read_csv("results/affinity_ablation.csv")

pivot = df.pivot(
    index="graph",
    columns="variant",
    values="edge_cut"
)

pivot["family"] = (
    pivot.index.to_series()
    .str.replace(r"_[0-9]+\.pkl$", "", regex=True)
)

pivot["improvement"] = pivot["baseline"] - pivot["affinity_modified"]
pivot["improvement_%"] = 100.0 * pivot["improvement"] / pivot["baseline"]

print("\n======================================================")
print("PER-FAMILY ANALYSIS")
print("======================================================")

for family in sorted(pivot.family.unique()):

    d = pivot[pivot.family == family]

    wins = (d.improvement > 0).sum()
    losses = (d.improvement < 0).sum()
    draws = (d.improvement == 0).sum()

    print()
    print(f"### {family}")
    print(f"Graphs : {len(d)}")
    print(f"Wins   : {wins}")
    print(f"Losses : {losses}")
    print(f"Draws  : {draws}")
    print(f"Mean % : {d.improvement_.mean() if False else d['improvement_%'].mean():.3f}")
    print(f"Median : {d['improvement_%'].median():.3f}")
    print(f"Best   : {d['improvement_%'].max():.3f}")
    print(f"Worst  : {d['improvement_%'].min():.3f}")

