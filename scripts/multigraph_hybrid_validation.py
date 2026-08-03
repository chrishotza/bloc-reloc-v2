#!/usr/bin/env python3

import os
import csv
import time
import pickle

from src.bloc_reloc_v2.core import BlocRelocV2

GRAPH_DIR="data/graphs"
OUT="results/multigraph_hybrid_validation.csv"

rows=[]

graphs=sorted(
    x for x in os.listdir(GRAPH_DIR)
    if x.endswith(".pkl")
)

for graph_file in graphs:

    family=graph_file.rsplit("_",1)[0]

    with open(os.path.join(GRAPH_DIR,graph_file),"rb") as f:
        G=pickle.load(f)

    print("\n"+graph_file)

    experiments=[

        {
            "name":"baseline",
            "kwargs":{}
        },

        {
            "name":"periodic_1",
            "kwargs":{
                "hybrid_period":1,
                "hybrid_samples":1200
            }
        },

        {
            "name":"reactive_100",
            "kwargs":{
                "reactive_stall":100,
                "hybrid_samples":1200
            }
        }

    ]

    for exp in experiments:

        t0=time.time()

        solver=BlocRelocV2(
            G,
            k=4,
            seed=42,
            variant="baseline"
        )

        r=solver.refine(
            iterations=50,
            **exp["kwargs"]
        )

        runtime=time.time()-t0

        trace=r["trace"]

        rows.append({

            "graph":graph_file,
            "family":family,
            "strategy":exp["name"],

            "edge_cut":r["edge_cut"],
            "weighted_cost":r["weighted_cost"],

            "runtime":runtime,

            "accepted_total":
                sum(x["accepted"] for x in trace),

            "rejected_total":
                sum(x["rejected"] for x in trace),

            "iterations":
                len(trace)

        })

        print(
            f"{exp['name']:14s}",
            f"cut={r['edge_cut']:4d}",
            f"time={runtime:7.3f}s"
        )

with open(OUT,"w",newline="") as f:

    writer=csv.DictWriter(
        f,
        fieldnames=rows[0].keys()
    )

    writer.writeheader()
    writer.writerows(rows)

print()
print("="*70)
print("CSV generado:",OUT)
print("="*70)
