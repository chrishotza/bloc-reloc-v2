"""
Evaluation metrics.
"""


def edge_cut(graph, partition):
    cut = 0
    for u, v in graph.edges():
        if partition[u] != partition[v]:
            cut += 1
    return cut
