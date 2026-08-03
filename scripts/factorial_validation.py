#!/usr/bin/env python3

import os
import csv
import time
import pickle

from src.bloc_reloc_v2.core import BlocRelocV2

GRAPH_DIR="data/graphs"
OUT="results/factorial_validation.csv"

CONFIGS=[

    dict(
        name="baseline",
        variant="baseline",
        hybrid_period=None,
        reactive_stall=None
    ),

    dict(
        name="affinity",
        variant="affinity_modified",
        hybrid_period=None,
        reactive_stall=None
    ),

    dict(
        name="periodic",
        variant="baseline",
        hybrid_period=1,
        reactive_stall=None
    ),

    dict(
        name="reactive",
        variant="baseline",
        hybrid_period=None,
        reactive_stall=100
    ),

    dict(
        name="affinity_periodic",
        variant="affinity_modified",
        hybrid_period=1,
        reactive_stall=None
    ),

    dict(
        name="affinity_reactive",
        variant="affinity_modified",
        hybrid_period=None,
        reactive_stall=100
    ),

]

rows=[]

graphs=sorted(
    x for x in os.listdir(GRAPH_DIR)
    if x.endswith(".pkl")
)

for graph in graphs:

    family=graph.rsplit("_",1)[0]

    print()
    print("="*70)
    print(graph)
    print("="*70)

    with open(os.path.join(GRAPH_DIR,graph),"rb") as f:
        G=pickle.load(f)

    for cfg in CONFIGS:

        solver=BlocRelocV2(
            G,
            k=4,
            seed=42,
            variant=cfg["variant"]
        )

        t0=time.time()

        r=solver.refine(
            iterations=50,
            hybrid_period=cfg["hybrid_period"],
            reactive_stall=cfg["reactive_stall"],
            hybrid_samples=1200
        )

        runtime=time.time()-t0

        trace=r["trace"]

        plateau=49

        last=r["edge_cut"]

        for i,x in enumerate(trace):

            if x["edge_cut"]!=last:
                plateau=i

            last=x["edge_cut"]

        rows.append({

            "graph":graph,
            "family":family,

            "configuration":cfg["name"],

            "variant":cfg["variant"],

            "hybrid_period":cfg["hybrid_period"],

            "reactive_stall":cfg["reactive_stall"],

            "edge_cut":r["edge_cut"],

            "weighted_cost":r["weighted_cost"],

            "runtime":runtime,

            "accepted":
                sum(t["accepted"] for t in trace),

            "rejected":
                sum(t["rejected"] for t in trace),

            "iterations_to_plateau":plateau

        })

        print(
            f'{cfg["name"]:22s}',
            f'cut={r["edge_cut"]:4d}',
            f'time={runtime:7.3f}s'
        )

with open(OUT,"w",newline="") as f:

    writer=csv.DictWriter(
        f,
        fieldnames=rows[0].keys()
    )

    writer.writeheader()
    writer.writerows(rows)

print()
print("="*80)
print("Saved ->",OUT)
print("="*80)

