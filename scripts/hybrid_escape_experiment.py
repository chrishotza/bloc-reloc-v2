#!/usr/bin/env python3

import pickle
import random
import time
import pandas as pd

from src.bloc_reloc_v2.core import BlocRelocV2

GRAPH="data/graphs/barabasi_albert_0.pkl"

SAMPLES=1200

with open(GRAPH,"rb") as f:
    G=pickle.load(f)

solver=BlocRelocV2(
    G,
    k=4,
    seed=42,
    variant="baseline"
)

##########################################################
# FASE 1
##########################################################

r=solver.refine(50)

part=r["partition"].copy()

best=solver.weighted_cut(part)

print()
print("="*70)
print("AFTER 1-SWAP")
print("="*70)
print("edge cut      :",r["edge_cut"])
print("weighted cost :",best)

##########################################################
# FASE 2
##########################################################

nodes=list(G.nodes())

accepted=0
rejected=0

trace=[]

t0=time.time()

for step in range(SAMPLES):

    u,v=random.sample(nodes,2)

    if part[u]==part[v]:
        continue

    bu=part[u]
    bv=part[v]

    part[u]=bv
    part[v]=bu

    cost=solver.weighted_cut(part)

    if cost<best:

        best=cost
        accepted+=1

    else:

        part[u]=bu
        part[v]=bv
        rejected+=1

    trace.append({
        "sample":step,
        "weighted_cost":best,
        "edge_cut":solver.edge_cut(part),
        "accepted":accepted,
        "rejected":rejected
    })

runtime=time.time()-t0

##########################################################

df=pd.DataFrame(trace)

print()
print("="*70)
print("AFTER SAMPLED 2-SWAP")
print("="*70)

print("edge cut      :",solver.edge_cut(part))
print("weighted cost :",best)
print("accepted      :",accepted)
print("rejected      :",rejected)
print("runtime       :",round(runtime,3),"s")

print()

print(df.tail(20).to_string(index=False))

df.to_csv(
    "results/hybrid_escape_trace.csv",
    index=False
)

print()
print("Saved -> results/hybrid_escape_trace.csv")
