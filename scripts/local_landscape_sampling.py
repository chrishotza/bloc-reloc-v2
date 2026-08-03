#!/usr/bin/env python3

import os
import pickle
import random
import pandas as pd

from src.bloc_reloc_v2.core import BlocRelocV2

random.seed(42)

rows=[]

for file in sorted(os.listdir("data/graphs")):

    if not file.endswith(".pkl"):
        continue

    with open(os.path.join("data/graphs",file),"rb") as f:
        G=pickle.load(f)

    family=file.rsplit("_",1)[0]

    for variant in ["baseline","affinity_modified"]:

        improve=0
        worsen=0

        gains=[]

        for seed in range(20):

            solver=BlocRelocV2(
                G,
                k=4,
                seed=seed,
                variant=variant
            )

            part=solver.initialize_partition()

            node=random.choice(list(G.nodes()))

            before=solver.weighted_cut(part)

            old=part[node]

            for b in range(solver.k):

                if b==old:
                    continue

                part[node]=b

                after=solver.weighted_cut(part)

                gain=before-after

                gains.append(gain)

                if gain>0:
                    improve+=1
                elif gain<0:
                    worsen+=1

            part[node]=old

        rows.append({
            "graph":file,
            "family":family,
            "variant":variant,
            "p_improve":improve/len(gains),
            "p_worsen":worsen/len(gains),
            "mean_gain":sum(gains)/len(gains),
            "std_gain":pd.Series(gains).std()
        })

        print(file,variant,"OK")

df=pd.DataFrame(rows)

print()
print("="*70)
print(df.groupby(["family","variant"]).mean(numeric_only=True).round(4))
print("="*70)

df.to_csv("results/local_landscape_sampling.csv",index=False)

print()
print("Saved -> results/local_landscape_sampling.csv")
