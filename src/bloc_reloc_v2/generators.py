"""
Synthetic graph generators for BLOC-RELOC v2 experiments.
"""

import networkx as nx


def random_regular(n=300, d=10, seed=0):
    return nx.random_regular_graph(d, n, seed=seed)


def watts_strogatz(n=300, k=10, p=0.1, seed=0):
    return nx.watts_strogatz_graph(n, k, p, seed=seed)


def barabasi_albert(n=300, m=5, seed=0):
    return nx.barabasi_albert_graph(n, m, seed=seed)


def planted_partition(n=300, seed=0):
    if type(n) is not int or n < 3:
        raise ValueError("n must be an integer >= 3")
    sizes = [n // 3, n // 3, n - 2 * (n // 3)]
    if len(set(sizes)) == 1:
        # Preserve the historical generator and RNG exactly for n divisible
        # by three (including the original n=300 experimental fixtures).
        return nx.planted_partition_graph(
            len(sizes), sizes[0], 0.05, 0.005, seed=seed
        )
    # planted_partition_graph uses a uniform community size. For other n,
    # random_partition_graph retains the requested total and 3 communities.
    return nx.random_partition_graph(sizes, 0.05, 0.005, seed=seed)


GENERATORS = {
    "random_regular": random_regular,
    "watts_strogatz": watts_strogatz,
    "barabasi_albert": barabasi_albert,
    "planted_partition": planted_partition,
}
