#!/usr/bin/env python3

import pickle
import time
import pandas as pd

from src.bloc_reloc_v2.core import BlocRelocV2

GRAPH="data/graphs/barabasi_albert_0.pkl"

STALLS=[
    None,
    1000,
    300,
    100,
    50,
    25,
    10
]

rows=[]

with open(GRAPH,"rb") as f:
    G=pickle.load(f)

for stall in STALLS:

    print()
    print("="*60)
    print("STALL:",stall)
    print("="*60)

    solver=BlocRelocV2(
        G,
        k=4,
        seed=42,
        variant="baseline"
    )

    t0=time.time()

    r=solver.refine(
        iterations=50,
        reactive_stall=stall,
        hybrid_samples=1200
    )

    runtime=time.time()-t0

    trace=r["trace"]

    rows.append({
        "stall_limit":"baseline" if stall is None else stall,
        "edge_cut":r["edge_cut"],
        "weighted_cost":r["weighted_cost"],
        "runtime":runtime,
        "accepted":sum(x["accepted"] for x in trace),
        "rejected":sum(x["rejected"] for x in trace),
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
    "results/reactive_scheduler_results.csv",
    index=False
)

print()
print("Saved -> results/reactive_scheduler_results.csv")
