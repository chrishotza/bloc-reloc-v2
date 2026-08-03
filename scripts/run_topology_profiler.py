import os
import pickle
import pandas as pd

from src.topology_profiler import TopologyProfiler

prof=TopologyProfiler()

rows=[]

for f in sorted(os.listdir("data/graphs")):

    if not f.endswith(".pkl"):
        continue

    with open(os.path.join("data/graphs",f),"rb") as h:
        G=pickle.load(h)

    r=prof.profile(G)

    r["graph"]=f
    r["family"]=f.rsplit("_",1)[0]

    rows.append(r)

    print(f"{f:30s} OK")

df=pd.DataFrame(rows)

df.to_csv(
    "results/topology_profiler.csv",
    index=False
)

print()
print("="*60)
print(df.groupby("family").mean(numeric_only=True).round(3))
print("="*60)
print()
print("Saved -> results/topology_profiler.csv")
