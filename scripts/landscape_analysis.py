#!/usr/bin/env python3

import os
import pickle
import random
import pandas as pd

from src.bloc_reloc_v2.core import BlocRelocV2

random.seed(42)

rows=[]

for graph_file in sorted(os.listdir("data/graphs")):

    if not graph_file.endswith(".pkl"):
        continue

    with open(os.path.join("data/graphs",graph_file),"rb") as f:
        G=pickle.load(f)

    family=graph_file.rsplit("_",1)[0]

    for variant in ["baseline","affinity_modified"]:

        solver=BlocRelocV2(
            G,
            k=4,
            seed=42,
            variant=variant
        )

        part=solver.initialize_partition()

        gains=[]

        nodes=random.sample(
            list(G.nodes()),
            min(40,G.number_of_nodes())
        )

        for node in nodes:

            original=part[node]

            before=solver.weighted_cut(part)

            for b in range(solver.k):

                if b==original:
                    continue

                part[node]=b

                after=solver.weighted_cut(part)

                gains.append(before-after)

            part[node]=original

        improving=sum(g>0 for g in gains)
        worsening=sum(g<0 for g in gains)
        neutral=sum(g==0 for g in gains)

        rows.append({

            "graph":graph_file,
            "family":family,
            "variant":variant,

            "moves":len(gains),

            "improving":improving,
            "worsening":worsening,
            "neutral":neutral,

            "mean_gain":sum(gains)/len(gains),
            "median_gain":pd.Series(gains).median(),
            "std_gain":pd.Series(gains).std(),
            "best_gain":max(gains),
            "worst_gain":min(gains)
        })

        print(graph_file,variant,"OK")

df=pd.DataFrame(rows)

df.to_csv(
    "results/optimization_landscape.csv",
    index=False
)

print()
print("="*70)
print(df.groupby(["family","variant"]).mean(numeric_only=True).round(4))
print("="*70)

print()
print("Saved -> results/optimization_landscape.csv")
