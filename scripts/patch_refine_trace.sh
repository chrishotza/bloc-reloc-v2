#!/bin/bash
set -e

python3 <<'PY'
from pathlib import Path

p=Path("src/bloc_reloc_v2/core.py")
txt=p.read_text()

old='''        part=self.initialize_partition()
        best=self.weighted_cut(part)
'''

new='''        part=self.initialize_partition()
        best=self.weighted_cut(part)

        trace=[]
'''

txt=txt.replace(old,new)

old='''        for _ in range(iterations):
'''

new='''        for it in range(iterations):

            accepted=0
            rejected=0
'''

txt=txt.replace(old,new)

old='''                    if c<best_cut:
                        best_cut=c
                        best_block=b
'''

new='''                    if c<best_cut:
                        best_cut=c
                        best_block=b
                        accepted+=1
                    else:
                        rejected+=1
'''

txt=txt.replace(old,new)

old='''                part[node]=best_block
                best=best_cut

        return {"partition":part,"edge_cut":self.edge_cut(part),"weighted_cost":best}
'''

new='''                part[node]=best_block
                best=best_cut

            trace.append({
                "iteration":it,
                "weighted_cost":best,
                "edge_cut":self.edge_cut(part),
                "accepted":accepted,
                "rejected":rejected
            })

        return {
            "partition":part,
            "edge_cut":self.edge_cut(part),
            "weighted_cost":best,
            "trace":trace
        }
'''

txt=txt.replace(old,new)

p.write_text(txt)

print("PATCH OK")
PY
