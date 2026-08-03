#!/usr/bin/env python3

import pickle
import time

from src.bloc_reloc_v2.core import BlocRelocV2

with open("data/graphs/barabasi_albert_0.pkl","rb") as f:
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

best=solver.weighted_cut(part)

t=time.time()

part,counts,best,acc,rej=solver.two_swap_step(
    part,
    counts,
    best
)

print()
print("Elapsed :",round(time.time()-t,3),"s")
print("Accepted:",acc)
print("Rejected:",rej)
print("Cost    :",best)
