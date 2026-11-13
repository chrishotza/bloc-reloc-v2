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


    def test_invalid_partition_counts_are_rejected_before_initializing(self):
        graph = nx.cycle_graph(6)
        for k in (0, -1, 7, 1.5, True, False, "2"):
            with self.subTest(k=k), self.assertRaisesRegex(ValueError, "k must"):
                BlocRelocV2(graph, k=k)
        with self.assertRaisesRegex(ValueError, "k must"):
            BlocRelocV2(nx.Graph(), k=1)

    def test_invalid_refinement_parameters_fail_closed(self):
        runner = BlocRelocV2(nx.cycle_graph(8), k=2, seed=9)
        for kwargs in (
            {"iterations": -1}, {"iterations": True},
            {"hybrid_period": 0}, {"hybrid_period": False},
            {"hybrid_period": 1.5}, {"reactive_stall": 0},
            {"reactive_stall": True}, {"hybrid_samples": 0},
            {"hybrid_samples": -1},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                runner.refine(**kwargs)

    def test_single_node_hybrid_refinement_remains_safe(self):
        graph = nx.empty_graph(1)
        result = BlocRelocV2(graph, k=1, seed=1).refine(
            iterations=2, hybrid_period=1, hybrid_samples=3
        )
        self.assertEqual(result["edge_cut"], 0)
        self.assertEqual(len(result["trace"]), 2)

    def test_invalid_direct_swap_sample_count_rejected(self):
        from collections import Counter

        runner = BlocRelocV2(nx.cycle_graph(4), k=2)
        partition = runner.initialize_partition()
        for count in (-1, True, "3", 0.4):
            with self.subTest(count=count), self.assertRaises(ValueError):
                runner.two_swap_step(partition, Counter(partition.values()), 4, count)



if __name__ == "__main__":
    unittest.main()
