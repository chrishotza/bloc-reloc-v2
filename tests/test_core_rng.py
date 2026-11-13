"""Isolation and determinism tests for the minimal BLOC-RELOC engine."""
import random
import unittest

import networkx as nx

from src.bloc_reloc_v2.core import BlocRelocV2


class LocalRandomnessTests(unittest.TestCase):
    def test_constructor_does_not_reset_process_random_state(self):
        random.seed(991)
        expected = [random.random() for _ in range(3)]
        random.seed(991)
        before = random.random()
        BlocRelocV2(nx.cycle_graph(12), k=3, seed=42)
        after = [random.random() for _ in range(2)]
        self.assertEqual([before, *after], expected)

    def test_refinement_does_not_consume_process_random_state(self):
        random.seed(725)
        expected = [random.random() for _ in range(3)]
        random.seed(725)
        first = random.random()
        BlocRelocV2(nx.cycle_graph(12), k=3, seed=42).refine(
            iterations=3, hybrid_period=1, hybrid_samples=6
        )
        following = [random.random() for _ in range(2)]
        self.assertEqual([first, *following], expected)

    def test_same_seed_replays_refinement_exactly(self):
        graph = nx.cycle_graph(12)
        a = BlocRelocV2(graph, k=3, seed=42).refine(
            iterations=4, hybrid_period=2, hybrid_samples=12
        )
        b = BlocRelocV2(graph, k=3, seed=42).refine(
            iterations=4, hybrid_period=2, hybrid_samples=12
        )
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
