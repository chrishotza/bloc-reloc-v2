#!/bin/bash
set -e

python3 <<'PY'
from pathlib import Path
import re

p=Path("src/bloc_reloc_v2/core.py")
txt=p.read_text()

# ------------------------------------------------------------
# ampliar firma refine
# ------------------------------------------------------------

txt=re.sub(
r'def refine\(self,iterations=50,hybrid_period=None,hybrid_samples=1200\):',
'def refine(self,iterations=50,hybrid_period=None,hybrid_samples=1200,reactive_stall=None):',
txt
)

# ------------------------------------------------------------
# insertar variables antes del bucle principal
# ------------------------------------------------------------

anchor="""        best=self.weighted_cut(part)

        trace=[]
"""

replace="""        best=self.weighted_cut(part)

        trace=[]

        stall_counter=0
"""

txt=txt.replace(anchor,replace)

# ------------------------------------------------------------
# actualizar contador de estancamiento
# ------------------------------------------------------------

anchor="""                part[node]=best_block
                best=best_cut
"""

replace="""                part[node]=best_block

                if best_cut<best:
                    stall_counter=0
                else:
                    stall_counter+=1

                best=best_cut
"""

txt=txt.replace(anchor,replace)

# ------------------------------------------------------------
# insertar política reactiva
# ------------------------------------------------------------

anchor="""            if (
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
"""

replace="""            if (
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

                stall_counter=0

            elif (
                reactive_stall is not None
                and stall_counter>=reactive_stall
            ):

                part,counts,best,a2,r2=self.two_swap_step(
                    part,
                    counts,
                    best,
                    max_samples=hybrid_samples
                )

                accepted+=a2
                rejected+=r2

                stall_counter=0
"""

txt=txt.replace(anchor,replace)

p.write_text(txt)

print("PATCH OK")
PY

echo
grep -n "reactive_stall\\|stall_counter" src/bloc_reloc_v2/core.py
