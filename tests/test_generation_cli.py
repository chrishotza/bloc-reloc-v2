"""Fast local-fixture generator contract checks (synthetic graphs only)."""
from pathlib import Path
import pickle
import subprocess
import sys
import tempfile
import unittest

import networkx as nx


ROOT = Path(__file__).resolve().parents[1]


class GeneratorCLITests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.output = Path(tmp.name) / "generated"

    def run_generator(self, *args):
        return subprocess.run(
            [
                sys.executable, "-m", "experiments.run_generation",
                "--output-dir", str(self.output),
                "--nodes", "24",
                "--seeds", "1",
                *args,
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )

    def test_small_smoke_creates_four_valid_local_graphs(self):
        result = self.run_generator()
        self.assertEqual(result.returncode, 0, result.stderr)
        files = sorted(self.output.glob("*.pkl"))
        self.assertEqual(len(files), 4)
        for path in files:
            with self.subTest(graph=path.name):
                # The pickle was just written by the local trusted generator.
                with path.open("rb") as stream:
                    graph = pickle.load(stream)
                self.assertIsInstance(graph, nx.Graph)
                self.assertEqual(graph.number_of_nodes(), 24)

    def test_nonmultiple_of_three_keeps_all_requested_nodes(self):
        from src.bloc_reloc_v2.generators import planted_partition
        for count in (13, 25, 26, 301):
            with self.subTest(nodes=count):
                graph = planted_partition(n=count, seed=9)
                self.assertEqual(graph.number_of_nodes(), count)
                self.assertEqual(sum(map(len, graph.graph["partition"])), count)
                self.assertEqual([len(group) for group in graph.graph["partition"]],
                                 [count // 3, count // 3, count - 2 * (count // 3)])
                self.assertEqual(
                    sorted(graph.edges()), sorted(planted_partition(n=count, seed=9).edges())
                )

    def test_divisible_by_three_uses_historical_networkx_generator(self):
        from src.bloc_reloc_v2.generators import planted_partition
        for n in (24, 300):
            with self.subTest(n=n):
                self.assertEqual(
                    sorted(planted_partition(n, seed=4).edges()),
                    sorted(nx.planted_partition_graph(3, n // 3, 0.05, 0.005,
                                                      seed=4).edges())
                )

    def test_generator_rejects_invalid_node_counts(self):
        from src.bloc_reloc_v2.generators import planted_partition
        for bad in (0, -1, True, 2, 3.1, "25"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                planted_partition(n=bad, seed=3)

    def test_cli_nondivisible_graph_size_is_preserved_for_each_family(self):
        result = self.run_generator("--nodes", "25")
        self.assertEqual(result.returncode, 0, result.stderr)
        for path in self.output.glob("*.pkl"):
            with path.open("rb") as stream:
                graph = pickle.load(stream)  # Locally generated trusted fixtures.
            self.assertEqual(graph.number_of_nodes(), 25, path.name)

    def test_repeated_generation_requires_explicit_overwrite(self):
        self.assertEqual(self.run_generator().returncode, 0)
        repeat = self.run_generator()
        self.assertNotEqual(repeat.returncode, 0)
        self.assertIn("Refusing to overwrite", repeat.stderr + repeat.stdout)
        overwritten = self.run_generator("--overwrite")
        self.assertEqual(overwritten.returncode, 0, overwritten.stderr)
        self.assertEqual(len(list(self.output.glob("*.pkl"))), 4)

    def test_invalid_nodes_are_rejected_before_writing(self):
        result = self.run_generator("--nodes", "10")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--nodes must be", result.stderr + result.stdout)
        self.assertFalse(self.output.exists())

    def test_invalid_seed_count_is_rejected(self):
        result = self.run_generator("--seeds", "0")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--seeds must be", result.stderr + result.stdout)


if __name__ == "__main__":
    unittest.main()
