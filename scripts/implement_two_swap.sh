#!/bin/bash
set -e

python3 <<'PY'
from pathlib import Path

p=Path("src/bloc_reloc_v2/core.py")
txt=p.read_text()

old="""    def two_swap_step(self, part, counts, best):
        \"""
        Placeholder para el operador 2-swap.

        Debe devolver:
            part, counts, best, accepted, rejected
        \"""
        return part, counts, best, 0, 0
"""

new="""    def two_swap_step(self, part, counts, best):

        accepted=0
        rejected=0

        nodes=list(self.graph.nodes())
        random.shuffle(nodes)

        for i in range(len(nodes)):

            u=nodes[i]

            for j in range(i+1,len(nodes)):

                v=nodes[j]

                if part[u]==part[v]:
                    continue

                bu=part[u]
                bv=part[v]

                part[u]=bv
                part[v]=bu

                c=self.weighted_cut(part)

                if c<best:
                    best=c
                    accepted+=1
                else:
                    part[u]=bu
                    part[v]=bv
                    rejected+=1

        return part,counts,best,accepted,rejected
"""

if old not in txt:
    raise SystemExit("STUB NOT FOUND")

txt=txt.replace(old,new)

p.write_text(txt)

print("2-SWAP IMPLEMENTED")
PY

echo
grep -n -A35 "def two_swap_step" src/bloc_reloc_v2/core.py
