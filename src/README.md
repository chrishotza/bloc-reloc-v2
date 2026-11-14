# Source

Implementation of BLOC-RELOC v2.

Design goals:
- reproducibility
- isolated experiments
- controlled ablation studies

## Refinement trace semantics

In new runs, `trace[].accepted` counts **committed** block relocations
and accepted 2-swaps, not every improving destination considered during
candidate evaluation. A single vertex can be tested against multiple better
blocks but can move to only one per visit. `trace[].rejected` still counts
non-improving candidate evaluations and should not be interpreted as a count
of finalized reverse moves. Historical CSVs/figures remain unchanged; any
fresh trace should be identified by its code revision before comparing
acceptance metrics across releases.
