import os
import sys
import csv
import time
import pickle

sys.path.insert(0,os.path.abspath("."))

from src.bloc_reloc_v2.core import BlocRelocV2

GRAPH_DIR="data/graphs"
OUT="results/bloc_reloc_v2_results.csv"

rows=[]

for file in sorted(os.listdir(GRAPH_DIR)):

    if not file.endswith(".pkl"):
        continue

    with open(os.path.join(GRAPH_DIR,file),"rb") as f:
        G=pickle.load(f)

    for variant in [
        "baseline",
        "affinity_modified"
    ]:

        t=time.time()

        r=BlocRelocV2(
            G,
            k=4,
            seed=42,
            variant=variant
        ).refine(50)

        rows.append({
            "graph":file,
            "variant":variant,
            "edge_cut":r["edge_cut"],
            "runtime":time.time()-t,
            "nodes":G.number_of_nodes(),
            "edges":G.number_of_edges()
        })

        print(file,variant,r["edge_cut"])

os.makedirs("results",exist_ok=True)

with open(OUT,"w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)

print("\nSaved:",OUT)
