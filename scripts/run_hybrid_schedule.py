#!/usr/bin/env python3

import pickle
import time
import pandas as pd

from src.bloc_reloc_v2.core import BlocRelocV2

GRAPH="data/graphs/barabasi_albert_0.pkl"

PERIODS=[
    None,
    10,
    5,
    3,
    2,
    1
]

rows=[]

with open(GRAPH,"rb") as f:
    G=pickle.load(f)

for period in PERIODS:

    print()
    print("="*60)
    print("Period:",period)
    print("="*60)

    t0=time.time()

    r=BlocRelocV2(
        G,
        k=4,
        seed=42,
        variant="baseline"
    ).refine(
        iterations=50,
        hybrid_period=period,
        hybrid_samples=1200
    )

    runtime=time.time()-t0

    trace=r["trace"]

    rows.append({
        "period":"baseline" if period is None else period,
        "edge_cut":r["edge_cut"],
        "weighted_cost":r["weighted_cost"],
        "runtime":runtime,
        "accepted_total":sum(x["accepted"] for x in trace),
        "rejected_total":sum(x["rejected"] for x in trace),
        "iterations_to_plateau":next(
            (
                i
                for i in range(1,len(trace))
                if trace[i]["weighted_cost"]==trace[-1]["weighted_cost"]
            ),
            len(trace)
        )
    })

    print("Edge cut :",r["edge_cut"])
    print("Weighted :",round(r["weighted_cost"],4))
    print("Runtime  :",round(runtime,3),"s")

df=pd.DataFrame(rows)

print()
print("="*80)
print(df.to_string(index=False))
print("="*80)

df.to_csv(
    "results/hybrid_schedule_results.csv",
    index=False
)

print()
print("Saved -> results/hybrid_schedule_results.csv")
