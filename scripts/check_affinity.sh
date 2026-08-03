#!/bin/bash
set -e

export PYTHONPATH=$PWD

python3 <<'PY'
from src.bloc_reloc_v2.core import BlocRelocV2
import networkx as nx
from collections import Counter

G=nx.barabasi_albert_graph(300,5,seed=42)

for variant in ["baseline","affinity_modified"]:

    r=BlocRelocV2(
        G,
        k=4,
        seed=42,
        variant=variant
    ).refine(50)

    print()
    print("="*60)
    print(variant)
    print("="*60)
    print("Edge cut      :",r["edge_cut"])
    print("Weighted cost :",round(r["weighted_cost"],4))
    print("Blocks        :",Counter(r["partition"].values()))
PY
