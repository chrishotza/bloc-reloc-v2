#!/usr/bin/env python3

import pandas as pd

df=pd.read_csv("results/optimization_landscape.csv")

df["p_improve"]=df["improving"]/df["moves"]
df["p_worsen"]=df["worsening"]/df["moves"]
df["landscape_bias"]=df["p_improve"]-df["p_worsen"]

print()
print("="*70)
print("LANDSCAPE STATISTICS")
print("="*70)

summary=(
    df.groupby(["family","variant"])
      .agg(
          p_improve=("p_improve","mean"),
          p_worsen=("p_worsen","mean"),
          landscape_bias=("landscape_bias","mean"),
          mean_gain=("mean_gain","mean"),
          std_gain=("std_gain","mean"),
          best_gain=("best_gain","mean"),
          worst_gain=("worst_gain","mean")
      )
      .round(4)
)

print(summary)

print()
print("="*70)
print("AFFINITY DELTA")
print("="*70)

base=df[df.variant=="baseline"].set_index("graph")
aff=df[df.variant=="affinity_modified"].set_index("graph")

cmp=pd.DataFrame(index=base.index)

cmp["family"]=base["family"]

cmp["delta_p_improve"]=(aff["p_improve"]-base["p_improve"])*100

cmp["delta_bias"]=aff["landscape_bias"]-base["landscape_bias"]

cmp["delta_mean_gain"]=aff["mean_gain"]-base["mean_gain"]

print(
    cmp.groupby("family")
       .mean(numeric_only=True)
       .round(4)
)

cmp.to_csv(
    "results/landscape_delta.csv"
)

print()
print("Saved -> results/landscape_delta.csv")
