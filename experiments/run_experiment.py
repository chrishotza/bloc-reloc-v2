import os
import pickle
import csv
import time


GRAPH_DIR = "data/graphs"
OUT = "results/baseline_results.csv"


def placeholder_solver(graph, variant):
    """
    Placeholder.
    Será reemplazado por BLOC-RELOC v2 real.
    """
    start = time.time()

    nodes = graph.number_of_nodes()
    edges = graph.number_of_edges()

    runtime = time.time() - start

    return {
        "edge_cut": -1,
        "balance": -1,
        "runtime": runtime,
        "nodes": nodes,
        "edges": edges,
        "variant": variant
    }


def main():

    os.makedirs("results", exist_ok=True)

    variants = [
        "baseline",
        "affinity_modified",
        "hub_aware",
        "bloc_reloc_v2_full"
    ]

    rows = []

    for file in sorted(os.listdir(GRAPH_DIR)):

        if not file.endswith(".pkl"):
            continue

        with open(
            os.path.join(GRAPH_DIR, file),
            "rb"
        ) as f:
            graph = pickle.load(f)

        for variant in variants:

            result = placeholder_solver(
                graph,
                variant
            )

            result["graph"] = file

            rows.append(result)

            print(
                file,
                variant
            )


    with open(
        OUT,
        "w",
        newline=""
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=rows[0].keys()
        )

        writer.writeheader()
        writer.writerows(rows)


    print("\nSaved:", OUT)


if __name__ == "__main__":
    main()
