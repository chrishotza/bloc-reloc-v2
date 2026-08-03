#!/bin/bash
set -e

echo "========================================================"
echo " BLOC-RELOC v2 CORE AUDIT"
echo "========================================================"
echo

echo "[1] Métodos del core"
grep -n "^ *def " src/bloc_reloc_v2/core.py
echo

echo "[2] Dónde se calcula el costo"
grep -n "edge_cost\|edge_cut\|decision\|cost\|gain" src/bloc_reloc_v2/core.py
echo

echo "[3] Dónde decide mover nodos"
grep -n "best_cut\|best_block\|random.shuffle\|partition\[node\]\|for b in range" src/bloc_reloc_v2/core.py
echo

echo "[4] Runner"
grep -n "variant\|edge_cut\|runtime\|BlocRelocV2" experiments/run_experiment.py
echo

echo "[5] CSV generado"
if [ -f results/bloc_reloc_v2_results.csv ]; then
    head -5 results/bloc_reloc_v2_results.csv
else
    echo "No existe."
fi
echo

echo "[6] Estadísticas rápidas"
python3 - <<'PY'
import pandas as pd
from pathlib import Path

p=Path("results/bloc_reloc_v2_results.csv")
if not p.exists():
    print("CSV inexistente")
    raise SystemExit

df=pd.read_csv(p)

print(df.groupby("variant")["edge_cut"].describe())
PY

echo
echo "========================================================"
echo " AUDIT COMPLETO"
echo "========================================================"
