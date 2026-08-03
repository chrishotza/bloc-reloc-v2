#!/bin/bash
set -e

python3 <<'PY'
from pathlib import Path

p=Path("src/bloc_reloc_v2/core.py")
txt=p.read_text()

# agregar parámetro operator
old="""    def __init__(self, graph, k=4, seed=42, variant="baseline"):
"""

new="""    def __init__(self, graph, k=4, seed=42, variant="baseline", operator="1_swap"):
"""

if old in txt:
    txt=txt.replace(old,new,1)

old="""        self.variant=variant
"""

new="""        self.variant=variant
        self.operator=operator
"""

if old in txt:
    txt=txt.replace(old,new,1)

# insertar stub del nuevo operador
marker="""    def refine(self,iterations=50):
"""

stub='''
    def two_swap_step(self, part, counts, best):
        """
        Placeholder para el operador 2-swap.

        Debe devolver:
            part, counts, best, accepted, rejected
        """
        return part, counts, best, 0, 0

'''

if stub not in txt:
    txt=txt.replace(marker,stub+marker)

p.write_text(txt)

print("2-SWAP INFRASTRUCTURE READY")
PY

echo
grep -n "operator\\|two_swap_step" src/bloc_reloc_v2/core.py
