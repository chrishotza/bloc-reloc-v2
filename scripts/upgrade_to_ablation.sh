#!/bin/bash
set -e

echo "==> Upgrading core..."

cat > src/bloc_reloc_v2/core.py <<'PY'
import math
import random

class BlocRelocV2:

    def __init__(self, graph, k=4, seed=42, variant="baseline"):
        self.graph=graph
        self.k=k
        self.seed=seed
        self.variant=variant
        random.seed(seed)
        self.degree=dict(graph.degree())

    def initialize_partition(self):
        return {n:i%self.k for i,n in enumerate(self.graph.nodes())}

    def edge_cost(self,u,v):
        if self.variant=="baseline":
            return 1.0

        if self.variant=="affinity_modified":
            return 1.0/math.sqrt(self.degree[u]*self.degree[v]+1.0)

        return 1.0

    def edge_cut(self,p):
        c=0.0
        for u,v in self.graph.edges():
            if p[u]!=p[v]:
                c+=self.edge_cost(u,v)
        return c

    def refine(self,iterations=50):

        part=self.initialize_partition()
        best=self.edge_cut(part)

        for _ in range(iterations):

            nodes=list(self.graph.nodes())
            random.shuffle(nodes)

            for node in nodes:

                old=part[node]
                best_block=old
                best_cut=best

                for b in range(self.k):

                    if b==old:
                        continue

                    part[node]=b

                    c=self.edge_cut(part)

                    if c<best_cut:
                        best_cut=c
                        best_block=b

                part[node]=best_block
                best=best_cut

        return {"partition":part,"edge_cut":best}
PY

echo "==> Upgrading runner..."

cat > experiments/run_experiment.py <<'PY'
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
PY

echo
echo "==> Running..."

export PYTHONPATH=$PWD

python3 experiments/run_experiment.py

echo
echo "DONE."
