#!/bin/bash
set -e

python3 <<'PY'
from pathlib import Path

p=Path("src/bloc_reloc_v2/core.py")
txt=p.read_text()

# --------------------------------------------------------
# 1) Cambiar firma de two_swap_step
# --------------------------------------------------------

txt=txt.replace(
"    def two_swap_step(self, part, counts, best):",
"    def two_swap_step(self, part, counts, best, max_samples=None):"
)

# --------------------------------------------------------
# 2) Reemplazar recorrido exhaustivo por versión muestreable
# --------------------------------------------------------

old="""        nodes=list(self.graph.nodes())
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
"""

new="""        nodes=list(self.graph.nodes())

        if max_samples is None:

            random.shuffle(nodes)

            pairs=[]

            for i in range(len(nodes)):
                for j in range(i+1,len(nodes)):
                    pairs.append((nodes[i],nodes[j]))

        else:

            pairs=[
                tuple(random.sample(nodes,2))
                for _ in range(max_samples)
            ]

        for u,v in pairs:

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
"""

if old not in txt:
    raise SystemExit("ERROR: two_swap body not found")

txt=txt.replace(old,new)

# --------------------------------------------------------
# 3) Cambiar firma refine
# --------------------------------------------------------

txt=txt.replace(
"    def refine(self,iterations=50):",
"    def refine(self,iterations=50,hybrid_period=None,hybrid_samples=1200):"
)

# --------------------------------------------------------
# 4) Insertar llamada híbrida
# --------------------------------------------------------

anchor="""            trace.append({
                "iteration":it,
                "weighted_cost":best,
                "edge_cut":self.edge_cut(part),
                "accepted":accepted,
                "rejected":rejected
            })
"""

insert="""            if (
                hybrid_period is not None
                and hybrid_period>0
                and (it+1)%hybrid_period==0
            ):

                part,counts,best,a2,r2=self.two_swap_step(
                    part,
                    counts,
                    best,
                    max_samples=hybrid_samples
                )

                accepted+=a2
                rejected+=r2

            trace.append({
                "iteration":it,
                "weighted_cost":best,
                "edge_cut":self.edge_cut(part),
                "accepted":accepted,
                "rejected":rejected
            })
"""

if anchor not in txt:
    raise SystemExit("ERROR: trace block not found")

txt=txt.replace(anchor,insert)

p.write_text(txt)

print("PATCH OK")
PY

echo
echo "========================================"
echo "VERIFY"
echo "========================================"

grep -n "hybrid_period\\|hybrid_samples\\|max_samples\\|two_swap_step" src/bloc_reloc_v2/core.py

echo
echo "Hybrid scheduler installed."
