#!/usr/bin/env python3

import os
import csv
import time
import pickle

from src.bloc_reloc_v2.core import BlocRelocV2

GRAPH_DIR="data/graphs"
OUT="results/search_dynamics.csv"

CONFIGS=[

    ("baseline","baseline",None,None),

    ("affinity","affinity_modified",None,None),

    ("periodic","baseline",1,None),

    ("reactive","baseline",None,100),

    ("affinity_periodic","affinity_modified",1,None),

    ("affinity_reactive","affinity_modified",None,100)

]

FIELDNAMES=[

    "graph",
    "family",
    "configuration",

    "iteration",

    "weighted_cost",

    "edge_cut",

    "accepted",

    "rejected",

    "acceptance_ratio",

    "runtime"

]

done=set()

if os.path.exists(OUT):

    with open(OUT) as f:

        r=csv.DictReader(f)

        for row in r:

            done.add(

                (

                    row["graph"],

                    row["configuration"],

                    int(row["iteration"])

                )

            )

need_header=not os.path.exists(OUT)

fout=open(OUT,"a",newline="")

writer=csv.DictWriter(

    fout,

    fieldnames=FIELDNAMES

)

if need_header:

    writer.writeheader()

graphs=sorted(

    g for g in os.listdir(GRAPH_DIR)

    if g.endswith(".pkl")

)

total_written=0

for graph in graphs:

    family=graph.rsplit("_",1)[0]

    with open(

        os.path.join(GRAPH_DIR,graph),

        "rb"

    ) as f:

        G=pickle.load(f)

    print()

    print("="*70)

    print(graph)

    print("="*70)

    for name,variant,period,stall in CONFIGS:

        key=(graph,name,49)

        if key in done:

            print(f"{name:20s} SKIP")

            continue

        print(f"{name:20s} RUN")

        solver=BlocRelocV2(

            G,

            k=4,

            seed=42,

            variant=variant

        )

        t0=time.time()

        result=solver.refine(

            iterations=50,

            hybrid_period=period,

            reactive_stall=stall,

            hybrid_samples=1200

        )

        runtime=time.time()-t0

        for tr in result["trace"]:

            acc=tr["accepted"]

            rej=tr["rejected"]

            total=acc+rej

            ratio=0.0

            if total>0:

                ratio=acc/total

            writer.writerow({

                "graph":graph,

                "family":family,

                "configuration":name,

                "iteration":tr["iteration"],

                "weighted_cost":tr["weighted_cost"],

                "edge_cut":tr["edge_cut"],

                "accepted":acc,

                "rejected":rej,

                "acceptance_ratio":ratio,

                "runtime":runtime

            })

            fout.flush()

            os.fsync(fout.fileno())

            total_written+=1

        print(

            f"done",

            f"cut={result['edge_cut']}",

            f"time={runtime:.2f}s"

        )

fout.close()

print()

print("="*70)

print("SEARCH DYNAMICS COMPLETED")

print("Rows written :",total_written)

print("Output       :",OUT)

print("="*70)

