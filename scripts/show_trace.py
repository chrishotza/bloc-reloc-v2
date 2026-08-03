#!/usr/bin/env python3

import pandas as pd

df=pd.read_csv("results/refine_trace.csv")

for variant in df.variant.unique():

    print()
    print("="*70)
    print(variant)
    print("="*70)

    print(df[df.variant==variant][[
        "iteration",
        "weighted_cost",
        "edge_cut",
        "accepted",
        "rejected"
    ]].to_string(index=False))
