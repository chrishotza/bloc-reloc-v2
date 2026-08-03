#!/usr/bin/env python3

import os
import csv
import pickle
import numpy as np

from src.bloc_reloc_v2.core import BlocRelocV2

GRAPH_DIR="data/graphs"

rows=[]

SEEDS=range(20)

for graph_file in sorted(os.listdir(GRAPH_DIR)):

    if not graph_file.endswith(".pkl"):
        continue

    with open(os.path.join(GRAPH_DIR,graph_file),"rb") as f:
        G=pickle.load(f)

    family=graph_file.rsplit("_",1)[0]

    for variant in ["baseline","affinity_modified"]:

        cuts=[]
        weighted=[]

        print(graph_file,variant)

        for seed in SEEDS:

            r=BlocRelocV2(
                G,
                k=4,
                seed=seed,
                variant=variant
            ).refine(50)

            cuts.append(r["edge_cut"])
            weighted.append(r["weighted_cost"])

        rows.append({

            "graph":graph_file,
            "family":family,
            "variant":variant,

            "mean_cut":np.mean(cuts),
            "std_cut":np.std(cuts),

            "best_cut":np.min(cuts),
            "worst_cut":np.max(cuts),

            "mean_weighted":np.mean(weighted),
            "std_weighted":np.std(weighted),

            "best_weighted":np.min(weighted),
            "worst_weighted":np.max(weighted)
        })

df_rows=rows

os.makedirs("results",exist_ok=True)

with open("results/stability_analysis.csv","w",newline="") as f:

    writer=csv.DictWriter(
        f,
        fieldnames=df_rows[0].keys()
    )

    writer.writeheader()
    writer.writerows(df_rows)

import pandas as pd

df=pd.DataFrame(df_rows)

print()
print("="*70)
print("STABILITY")
print("="*70)

print(
    df.groupby(["family","variant"])
      .mean(numeric_only=True)
      .round(3)
)

print()
print("Saved -> results/stability_analysis.csv")
