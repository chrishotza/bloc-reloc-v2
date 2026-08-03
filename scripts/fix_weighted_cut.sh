#!/bin/bash
set -e

python3 <<'PY'
from pathlib import Path

p=Path("src/bloc_reloc_v2/core.py")
txt=p.read_text()

old="""    def edge_cut(self,p):
        c=0.0
        for u,v in self.graph.edges():
            if p[u]!=p[v]:
                c+=self.decision_cost(u,v)
        return c
"""

new="""    def weighted_cut(self,p):
        c=0.0
        for u,v in self.graph.edges():
            if p[u]!=p[v]:
                c+=self.decision_cost(u,v)
        return c

    def edge_cut(self,p):
        cut=0
        for u,v in self.graph.edges():
            if p[u]!=p[v]:
                cut+=1
        return cut
"""

if old not in txt:
    raise SystemExit("NO MATCH FOUND")

txt=txt.replace(old,new)

p.write_text(txt)

print("OK")
PY

echo
echo "========== CHECK =========="
grep -n "weighted_cut\|edge_cut\|decision_cost" src/bloc_reloc_v2/core.py
echo "==========================="
