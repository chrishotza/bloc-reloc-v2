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
