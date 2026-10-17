"""Generate local, trusted synthetic graph fixtures for BLOC-RELOC v2.

Default behavior preserves the historical four-families x 30-seeds protocol.
For a quick check, pass --seeds 1 --nodes 24 --output-dir data/graphs-smoke.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import pickle

from src.bloc_reloc_v2.generators import GENERATORS


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Generate trusted local synthetic graphs; never import untrusted pickles."
    )
    parser.add_argument(
        "--output-dir", type=Path, default=Path("data/graphs"),
        help="where to store generated .pkl graphs (default: data/graphs)"
    )
    parser.add_argument(
        "--seeds", type=int, default=30,
        help="number of consecutive seeds starting from zero (default: 30)"
    )
    parser.add_argument(
        "--nodes", type=int, default=300,
        help="nodes per synthetic graph (default: 300, minimum: 12)"
    )
    parser.add_argument(
        "--overwrite", action="store_true",
        help="explicitly allow replacing existing locally generated graph fixtures"
    )
    return parser.parse_args(argv)


def run(args) -> int:
    if args.seeds < 1:
        raise SystemExit("--seeds must be >= 1")
    if args.nodes < 12:
        raise SystemExit("--nodes must be >= 12 for the included generators")

    destinations = [
        (name, generator, seed, args.output_dir / f"{name}_{seed}.pkl")
        for name, generator in GENERATORS.items()
        for seed in range(args.seeds)
    ]
    if not args.overwrite:
        existing = [str(path) for _, _, _, path in destinations if path.exists()]
        if existing:
            raise SystemExit(
                f"Refusing to overwrite {len(existing)} generated graph fixtures "
                f"(first: {existing[0]}). Pass --overwrite or a new --output-dir."
            )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, generator, seed, path in destinations:
        graph = generator(n=args.nodes, seed=seed)
        mode = "wb" if args.overwrite else "xb"
        with path.open(mode) as stream:
            pickle.dump(graph, stream, protocol=pickle.HIGHEST_PROTOCOL)
    print(
        f"Generated {len(destinations)} trusted local graphs "
        f"({len(GENERATORS)} families x {args.seeds} seeds, {args.nodes} nodes) "
        f"in {args.output_dir}"
    )
    return len(destinations)


def main(argv=None):
    run(parse_args(argv))


if __name__ == "__main__":
    main()
