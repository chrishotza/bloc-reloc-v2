#!/bin/bash
set -e

python3 <<'PY'
from pathlib import Path

p=Path("src/topology_profiler/profiler.py")
txt=p.read_text()

txt=txt.replace("""
        try:
            algebraic=nx.algebraic_connectivity(G)
        except Exception:
            algebraic=float("nan")
""","""
        algebraic=float("nan")
""")

txt=txt.replace("""
        try:
            spectral=max(nx.adjacency_spectrum(G)).real
        except Exception:
            spectral=float("nan")
""","""
        spectral=float("nan")
""")

p.write_text(txt)

print("FAST PATCH APPLIED")
PY

echo
grep -n "algebraic\|spectral" src/topology_profiler/profiler.py
