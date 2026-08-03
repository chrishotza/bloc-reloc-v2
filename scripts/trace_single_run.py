#!/usr/bin/env python3

import pickle
import pandas as pd

from src.bloc_reloc_v2.core import BlocRelocV2

with open("data/graphs/barabasi_albert_0.pkl","rb") as f:
    G=pickle.load(f)

rows=[]

for variant in ["baseline","affinity_modified"]:

    r=BlocRelocV2(
        G,
        k=4,
        seed=42,
        variant=variant
    ).refine(50)

    for x in r["trace"]:
        x["variant"]=variant
        rows.append(x)

df=pd.DataFrame(rows)

print()
print(df.head(20))

print()
print(df.groupby("variant")[["weighted_cost","edge_cut","accepted","rejected"]].tail(5))

df.to_csv(
    "results/refine_trace.csv",
    index=False
)

print()
print("Saved -> results/refine_trace.csv")
