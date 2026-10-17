# AGENTS.md — BLOC-RELOC v2

This is a research workspace with **archived evidence and actively runnable minimal experiments**. Navigate both layers without conflating them. Human contributors and AI agents should follow the same contract.

## Read in this order

1. [README.md](README.md) — overview, navigation and distinction between historical and current protocols.
2. [reproducibility/README.md](reproducibility/README.md) — smoke-test commands, expected outputs and safety.
3. [src/bloc_reloc_v2/core.py](src/bloc_reloc_v2/core.py) — current minimal graph refinement implementation.
4. [experiments/run_generation.py](experiments/run_generation.py) and [experiments/run_experiment.py](experiments/run_experiment.py) — supported CLI entrypoints.
5. [reproducibility/EXPERIMENT_PLAN.md](reproducibility/EXPERIMENT_PLAN.md) — prospective research plan, **not** proof that all tests ran.
6. [results/observatory/final_synthesis/BLOC_RELOC_V2_FINAL_SYNTHESIS.md](results/observatory/final_synthesis/BLOC_RELOC_V2_FINAL_SYNTHESIS.md) — **historical** aggregated observations; not a fresh independent rerun.

## Safe 4-graph smoke check

```bash
python -m pip install networkx
python -m experiments.run_generation --seeds 1 --nodes 24 --output-dir data/graphs-smoke
python -m experiments.run_experiment --graph-dir data/graphs-smoke --iterations 3 --output results/local/smoke.csv
python -m unittest discover -s tests -v
```

The smoke experiment produces **4 graph fixtures and 8 CSV rows**: two variants (`baseline`, `affinity_modified`) × four graph families. The full generator defaults are **30 seeds × four families × 300 nodes**; the runner defaults to **50 iterations**. They are substantially more expensive.

A repeated smoke run refuses to overwrite existing graph pickles or CSVs. Choose another local output directory/filename, or explicitly pass `--overwrite` only for outputs you intend to replace.

## Non-negotiable evidence boundaries

- The checked-in `results/` tree contains **historical research artifacts**, not necessarily results recreated by the current CLI.
- Fresh runs belong in ignored `results/local/`; **never overwrite** `results/bloc_reloc_v2_results.csv` or other archived evidence without an explicit request, a provenance trail and review.
- Treat the six-configuration Dynamics Observatory synthesis as **recorded observational evidence**. It does **not** establish causality, universal superiority, complete external-solver validation, or the reproducibility of every configuration using the two-variant runner.
- Keep exploratory results, prospective plans and validated reproducibility **clearly labelled and separate**.
- The manuscript directory is an outline; do not claim the paper is published without a resolvable identifier.
- Loading Python `pickle` may execute code. Only read fixtures generated locally or originating from a trusted source; never automatically download and unpickle external files.
- Do not modify benchmark CSVs, binary figures, historical reports or the underlying algorithm to improve presentation alone.

## Contribution and verification

- Prefer small, reversible changes with one clear purpose and no claims beyond their evidence.
- For changes to the minimal runner, generators or graph implementation, run `python -m unittest discover -s tests -v` and check the [Minimal reproducibility safety workflow](.github/workflows/minimal-repro.yml).
- When reporting new performance, specify graph family, seed, size, variants, iteration count, runtime environment, metrics and exact generated artifact paths.
- If an experiment is only a smoke test, **call it a smoke test**.

## Related work

- [ATOF — current Python-facing optimization framework](https://github.com/chrishotza/Adaptiv-Topologica-Optimization-Framework)
- [Historical adaptive topology research](https://github.com/chrishotza/adaptive-topological-optimization)
