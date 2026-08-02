import random
from collections import Counter


class BlocRelocV2:

    def __init__(self, graph, k=4, seed=42):
        self.graph = graph
        self.k = k
        self.seed = seed
        random.seed(seed)


    def initialize_partition(self):
        partition = {}

        for i, node in enumerate(self.graph.nodes()):
            partition[node] = i % self.k

        return partition


    def edge_cut(self, partition):

        cut = 0

        for u, v in self.graph.edges():
            if partition[u] != partition[v]:
                cut += 1

        return cut


    def balanced(self, partition):

        counts = Counter(partition.values())

        sizes = list(counts.values())

        target = len(partition) / self.k

        return all(
            abs(size - target) <= target * 0.25
            for size in sizes
        )


    def refine(self, iterations=10):

        partition = self.initialize_partition()

        best = self.edge_cut(partition)

        for _ in range(iterations):

            nodes = list(self.graph.nodes())
            random.shuffle(nodes)

            for node in nodes:

                current = partition[node]

                candidates = [
                    x for x in range(self.k)
                    if x != current
                ]

                target = random.choice(candidates)

                partition[node] = target

                new_cut = self.edge_cut(partition)

                if self.balanced(partition) and new_cut < best:
                    best = new_cut

                else:
                    partition[node] = current


        return {
            "partition": partition,
            "edge_cut": best
        }
