#!/usr/bin/env python3

import random
import pickle
import time
import pandas as pd

from src.bloc_reloc_v2.core import BlocRelocV2

GRAPH="data/graphs/barabasi_albert_0.pkl"

with open(GRAPH,"rb") as f:
    G=pickle.load(f)

solver=BlocRelocV2(
    G,
    k=4,
    seed=42,
    variant="baseline"
)

part=solver.initialize_partition()

counts={}
for b in part.values():
    counts[b]=counts.get(b,0)+1

target=solver.weighted_cut(part)

N=G.number_of_nodes()

samples_list=[
    100,
    300,
    600,
    1200,
    2400,
    4800,
    9600,
    "exhaustive"
]

rows=[]

for samples in samples_list:

    p=part.copy()
    c=counts.copy()
    best=target

    accepted=0
    rejected=0

    t0=time.time()

    if samples=="exhaustive":

        nodes=list(G.nodes())

        for i in range(len(nodes)):

            u=nodes[i]

            for j in range(i+1,len(nodes)):

                v=nodes[j]

                if p[u]==p[v]:
                    continue

                bu=p[u]
                bv=p[v]

                p[u]=bv
                p[v]=bu

                cost=solver.weighted_cut(p)

                if cost<best:
                    best=cost
                    accepted+=1
                else:
                    p[u]=bu
                    p[v]=bv
                    rejected+=1

    else:

        nodes=list(G.nodes())

        for _ in range(samples):

            u,v=random.sample(nodes,2)

            if p[u]==p[v]:
                continue

            bu=p[u]
            bv=p[v]

            p[u]=bv
            p[v]=bu

            cost=solver.weighted_cut(p)

            if cost<best:
                best=cost
                accepted+=1
            else:
                p[u]=bu
                p[v]=bv
                rejected+=1

    runtime=time.time()-t0

    edge_cut=solver.edge_cut(p)

    rows.append({
        "samples":samples,
        "edge_cut":edge_cut,
        "weighted_cost":best,
        "accepted":accepted,
        "rejected":rejected,
        "runtime":runtime,
        "improvement_per_second":(
            (target-best)/runtime if runtime>0 else 0
        )
    })

df=pd.DataFrame(rows)

print()
print("="*80)
print(df.to_string(index=False))
print("="*80)

df.to_csv(
    "results/sample_two_swap_scaling.csv",
    index=False
)

print()
print("Saved -> results/sample_two_swap_scaling.csv")
