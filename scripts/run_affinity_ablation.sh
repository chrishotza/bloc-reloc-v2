#!/bin/bash
set -e

export PYTHONPATH=$PWD

python3 <<'PY'
import os
import csv
import time
import pickle

from src.bloc_reloc_v2.core import BlocRelocV2

GRAPH_DIR="data/graphs"
OUT="results/affinity_ablation.csv"

os.makedirs("results",exist_ok=True)

rows=[]

variants=[
    "baseline",
    "affinity_modified"
]

for graph_file in sorted(os.listdir(GRAPH_DIR)):

    if not graph_file.endswith(".pkl"):
        continue

    with open(os.path.join(GRAPH_DIR,graph_file),"rb") as f:
        G=pickle.load(f)

    for variant in variants:

        t0=time.time()

        r=BlocRelocV2(
            G,
            k=4,
            seed=42,
            variant=variant
        ).refine(50)

        rows.append({
            "graph":graph_file,
            "variant":variant,
            "edge_cut":r["edge_cut"],
            "weighted_cost":r["weighted_cost"],
            "runtime":time.time()-t0
        })

        print(f"{graph_file:30s} {variant:20s} cut={r['edge_cut']:4d}")

with open(OUT,"w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)

print()
print("CSV generado:",OUT)
PY
