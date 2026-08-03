#!/bin/bash
set -e

python3 <<'PY'
from pathlib import Path

p=Path("src/bloc_reloc_v2/core.py")

txt=p.read_text()

txt=txt.replace(
"""    def edge_cost(self,u,v):""",
"""    def decision_cost(self,u,v):"""
)

txt=txt.replace(
"self.edge_cost(",
"self.decision_cost("
)

txt=txt.replace(
"""    def edge_cut(self,p):

        c=0.0

        for u,v in self.graph.edges():
            if p[u]!=p[v]:
                c+=self.decision_cost(u,v)

        return c
""",
'''    def weighted_cut(self,p):

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
'''
)

txt=txt.replace(
"best=self.edge_cut(part)",
"best=self.weighted_cut(part)"
)

txt=txt.replace(
"c=self.edge_cut(part)",
"c=self.weighted_cut(part)"
)

txt=txt.replace(
'return {"partition":part,"edge_cut":best}',
'return {"partition":part,"edge_cut":self.edge_cut(part),"weighted_cost":best}'
)

p.write_text(txt)

print("PATCH OK")
PY

echo
echo "=================================="
grep -n "decision_cost\\|weighted_cut\\|edge_cut" src/bloc_reloc_v2/core.py
echo "=================================="
