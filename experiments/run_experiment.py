import os
import sys
import pickle
import csv
import time

sys.path.insert(0, os.path.abspath("."))

from src.bloc_reloc_v2.core import BlocRelocV2


GRAPH_DIR = "data/graphs"
OUT = "results/bloc_reloc_v2_results.csv"


def main():

    os.makedirs("results", exist_ok=True)

    rows = []

    for file in sorted(os.listdir(GRAPH_DIR)):

        if not file.endswith(".pkl"):
            continue

        with open(os.path.join(GRAPH_DIR, file), "rb") as f:
            graph = pickle.load(f)

        start = time.time()

        solver = BlocRelocV2(
            graph,
            k=4,
            seed=42
        )

        result = solver.refine(iterations=50)

        runtime = time.time() - start

        rows.append({
            "graph": file,
            "variant": "bloc_reloc_v2_baseline",
            "edge_cut": result["edge_cut"],
            "runtime": runtime,
            "nodes": graph.number_of_nodes(),
            "edges": graph.number_of_edges()
        })

        print(f"{file}: cut={result['edge_cut']} time={runtime:.4f}s")


    with open(OUT, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


    print("Saved:", OUT)


if __name__ == "__main__":
    main()
