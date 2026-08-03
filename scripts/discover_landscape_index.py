#!/usr/bin/env python3

import pandas as pd
import numpy as np

L=pd.read_csv("results/local_landscape_sampling.csv")
A=pd.read_csv("results/affinity_ablation.csv")

pivot=A.pivot(
    index="graph",
    columns="variant",
    values="edge_cut"
)

pivot["improvement_%"]=100*(
    pivot["baseline"]-pivot["affinity_modified"]
)/pivot["baseline"]

pivot=pivot.reset_index()

df=L.merge(pivot,on="graph")

df["smoothness"]=1/(1+df["std_gain"])

df["success_ratio"]=df["p_improve"]/(df["p_improve"]+df["p_worsen"]+1e-12)

df["landscape_index"]=(
    df["smoothness"]*
    df["success_ratio"]
)

print()
print("="*70)
print("CORRELATIONS")
print("="*70)

metrics=[
    "p_improve",
    "p_worsen",
    "mean_gain",
    "std_gain",
    "smoothness",
    "success_ratio",
    "landscape_index"
]

for m in metrics:

    b=df[df.variant=="baseline"][[m,"improvement_%"]].corr().iloc[0,1]
    a=df[df.variant=="affinity_modified"][[m,"improvement_%"]].corr().iloc[0,1]

    print(f"{m:20s} baseline={b:8.4f}   affinity={a:8.4f}")

print()
print("="*70)
print("TOP LANDSCAPE INDEX")
print("="*70)

print(
    df[df.variant=="affinity_modified"]
    [["graph","family","landscape_index","improvement_%"]]
    .sort_values("landscape_index",ascending=False)
    .head(20)
)

print()
print("="*70)
print("FAMILY MEANS")
print("="*70)

print(
    df.groupby(["family","variant"])[
        ["landscape_index","smoothness","success_ratio"]
    ].mean().round(4)
)

df.to_csv(
    "results/landscape_index.csv",
    index=False
)

print()
print("Saved -> results/landscape_index.csv")
