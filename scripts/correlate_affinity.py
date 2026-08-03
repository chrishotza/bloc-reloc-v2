#!/usr/bin/env python3

import pandas as pd

exp = pd.read_csv("results/affinity_ablation.csv")

pivot = exp.pivot(
    index="graph",
    columns="variant",
    values="edge_cut"
)

pivot["improvement_%"] = (
    100.0 *
    (pivot["baseline"] - pivot["affinity_modified"])
    / pivot["baseline"]
)

topo = pd.read_csv("results/topology_metrics.csv")

df = topo.merge(
    pivot["improvement_%"],
    left_on="graph",
    right_index=True
)

print("\n==============================")
print("CORRELATIONS")
print("==============================")

for col in [
    "hub_ratio",
    "degree_std",
    "max_degree",
    "avg_degree"
]:
    r = df[col].corr(df["improvement_%"])
    print(f"{col:15s}: {r: .4f}")

print("\n==============================")
print("BY FAMILY")
print("==============================")

print(
    df.groupby("family")["improvement_%"]
      .mean()
      .round(3)
)

