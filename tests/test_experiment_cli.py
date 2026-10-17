"""Regression checks for the minimal BLOC-RELOC experiment runner.

Use small, locally generated trusted fixtures; never load external pickles.
These tests verify output safety and basic CLI behavior, not research claims.
"""
from __future__ import annotations

import csv
from pathlib import Path
import pickle
import subprocess
import sys
import tempfile
import unittest

import networkx as nx


ROOT = Path(__file__).resolve().parents[1]


class MinimalExperimentCLITests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.graphs = self.base / "graphs"
        self.graphs.mkdir()
        self.output = self.base / "new-results.csv"
        self.graph_name = "locally-generated.pkl"
        with (self.graphs / self.graph_name).open("wb") as stream:
            pickle.dump(nx.cycle_graph(12), stream)

    def execute(self, *args):
        return subprocess.run(
            [
                sys.executable, "-m", "experiments.run_experiment",
                "--graph-dir", str(self.graphs),
                "--output", str(self.output),
                "--iterations", "3",
                "--seed", "7",
                *args,
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )

    def test_results_are_separate_and_have_both_variants(self):
        result = self.execute()
        self.assertEqual(result.returncode, 0, result.stderr)
        with self.output.open(newline="", encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(len(rows), 2)
        self.assertEqual(
            {r["variant"] for r in rows}, {"baseline", "affinity_modified"}
        )
        self.assertEqual({r["graph"] for r in rows}, {self.graph_name})
        self.assertEqual({r["nodes"] for r in rows}, {"12"})

    def test_existing_results_are_not_silently_overwritten(self):
        self.output.write_text("historical marker\n", encoding="utf-8")
        result = self.execute()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Refusing to overwrite", result.stderr + result.stdout)
        self.assertEqual(
            self.output.read_text(encoding="utf-8"), "historical marker\n"
        )

    def test_overwrite_requires_explicit_flag(self):
        self.output.write_text("old local result\n", encoding="utf-8")
        result = self.execute("--overwrite")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(
            self.output.read_text(encoding="utf-8").startswith(
                "graph,variant,edge_cut,runtime,nodes,edges\n"
            )
        )

    def test_missing_graph_directory_explains_next_step(self):
        missing = self.base / "does-not-exist"
        result = self.execute("--graph-dir", str(missing))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("run_generation", result.stderr + result.stdout)
        self.assertFalse(self.output.exists())

    def test_empty_graph_directory_explains_next_step(self):
        (self.graphs / self.graph_name).unlink()
        result = self.execute()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("No .pkl graphs", result.stderr + result.stdout)
        self.assertFalse(self.output.exists())

    def test_rejects_invalid_iterations(self):
        result = self.execute("--iterations", "0")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--iterations must be", result.stderr + result.stdout)
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
