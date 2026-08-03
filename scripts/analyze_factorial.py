#!/usr/bin/env python3

import pandas as pd

df=pd.read_csv("results/factorial_validation.csv")

print("="*80)
print("GLOBAL MEANS")
print("="*80)

global_summary=(
    df.groupby("configuration")
      .agg(
        graphs=("graph","count"),
        mean_cut=("edge_cut","mean"),
        median_cut=("edge_cut","median"),
        std_cut=("edge_cut","std"),
        mean_runtime=("runtime","mean")
      )
      .sort_values("mean_cut")
)

print(global_summary.round(3))

print()
print("="*80)
print("BY FAMILY")
print("="*80)

for family in sorted(df.family.unique()):

    print()
    print("#",family)

    t=(
        df[df.family==family]
        .groupby("configuration")
        .agg(
            mean_cut=("edge_cut","mean"),
            median=("edge_cut","median"),
            runtime=("runtime","mean")
        )
        .sort_values("mean_cut")
    )

    print(t.round(2))

print()
print("="*80)
print("WINS")
print("="*80)

wins=[]

for graph in sorted(df.graph.unique()):

    x=df[df.graph==graph]

    best=x.edge_cut.min()

    y=x[x.edge_cut==best]

    for _,r in y.iterrows():

        wins.append({
            "configuration":r.configuration
        })

wins=pd.DataFrame(wins)

print(
    wins.groupby("configuration")
        .size()
        .sort_values(ascending=False)
)

print()
print("="*80)
print("AVERAGE IMPROVEMENT VS BASELINE")
print("="*80)

baseline=df[df.configuration=="baseline"][["graph","edge_cut"]]
baseline=baseline.rename(columns={"edge_cut":"baseline"})

z=df.merge(baseline,on="graph")

z["improvement"]=z.baseline-z.edge_cut
z["improvement_%"]=100*z.improvement/z.baseline

summary=(
    z.groupby("configuration")
     .agg(
        mean_improvement=("improvement_%","mean"),
        median=("improvement_%","median"),
        max=("improvement_%","max"),
        min=("improvement_%","min")
     )
     .sort_values("mean_improvement",ascending=False)
)

print(summary.round(3))

print()
print("="*80)
print("FAMILY WINNERS")
print("="*80)

for family in sorted(z.family.unique()):

    s=(
        z[z.family==family]
        .groupby("configuration")
        .improvement_
        .mean() if False else
        z[z.family==family]
        .groupby("configuration")["improvement_%"]
        .mean()
    )

    print()
    print(family)
    print(s.sort_values(ascending=False).round(2))

print()
print("="*80)
print("RUNTIME EFFICIENCY")
print("="*80)

eff=(
    z.groupby("configuration")
    .agg(
        improvement=("improvement","mean"),
        runtime=("runtime","mean")
    )
)

eff["improvement_per_second"]=eff.improvement/eff.runtime

print(
    eff.sort_values(
        "improvement_per_second",
        ascending=False
    ).round(3)
)

