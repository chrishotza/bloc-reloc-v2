# BLOC-RELOC v2 Experimental Plan

> **Protocol status / Estado del protocolo:** This document is a **research plan**, not proof that every listed comparison has been executed. The repository also retains archived historical results. The rule below prohibiting copied historical results applies to **new confirmatory runs**, not to the retention of clearly labelled archive artifacts. As currently checked in, the minimal runner implements `baseline` and `affinity_modified`; separate reproducible evidence is needed for additional planned variants and external baselines.
>
> **ES:** Este documento es un **plan experimental**, no una certificación de ejecución. Los resultados históricos archivados se conservan como evidencia diferenciada; la prohibición de copiarlos se aplica a nuevas ejecuciones confirmatorias. Ver [Reproducibility / Reproducibilidad](README.md).


## Objective

Reproduce and evaluate BLOC-RELOC v2 under a controlled protocol.

## Rules

- No historical results copied.
- All results generated inside this repository.
- Fixed datasets.
- Fixed seeds.
- Fixed metrics.

## Evaluation

Baselines:
- BLOC-RELOC v1
- BLOC-RELOC v2
- External reference solvers

Metrics:
- Edge cut
- Balance constraint
- Runtime
- Memory usage
- Variance across seeds

## Ablation

Compare:

1. Original operator
2. Structural affinity modification
3. Hub-aware modification
4. Full BLOC-RELOC v2

## Scientific Claim

The claim must be derived from reproduced experimental evidence.

No claim before experiments.
