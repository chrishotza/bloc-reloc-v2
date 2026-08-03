#!/bin/bash
set -e

python3 <<'PY'
from pathlib import Path

p=Path("src/bloc_reloc_v2/core.py")
txt=p.read_text()

# agregar import Counter
if "from collections import Counter" not in txt:
    txt=txt.replace(
        "import random",
        "import random\nfrom collections import Counter"
    )

# insertar cálculo de tamaños al inicio de refine
txt=txt.replace(
"""        part=self.initialize_partition()
        best=self.weighted_cut(part)
""",
"""        part=self.initialize_partition()
        counts=Counter(part.values())

        target=len(part)/self.k
        tolerance=max(1,int(target*0.05))

        best=self.weighted_cut(part)
"""
)

# reemplazar movimiento
old="""                    part[node]=b

                    c=self.weighted_cut(part)

                    if c<best_cut:
                        best_cut=c
                        best_block=b
"""

new="""                    if counts[b]+1 <= target+tolerance and counts[old]-1 >= target-tolerance:

                        part[node]=b

                        c=self.weighted_cut(part)

                        if c<best_cut:
                            best_cut=c
                            best_block=b

                        part[node]=old
"""

txt=txt.replace(old,new)

# actualizar contador cuando el movimiento es aceptado
txt=txt.replace(
"""                part[node]=best_block
                best=best_cut
""",
"""                if best_block!=old:
                    counts[old]-=1
                    counts[best_block]+=1

                part[node]=best_block
                best=best_cut
"""
)

p.write_text(txt)

print("PATCH BALANCE OK")
PY

python3 - <<'PY'
from src.bloc_reloc_v2.core import BlocRelocV2
import networkx as nx
from collections import Counter

G=nx.barabasi_albert_graph(300,5,seed=42)

r=BlocRelocV2(G,k=4,seed=42).refine(50)

print()
print("Edge cut:",r["edge_cut"])
print("Distribution:",Counter(r["partition"].values()))
PY

