#!/usr/bin/env python3

import os
import pickle
import pandas as pd
import networkx as nx

rows=[]

for f in sorted(os.listdir("data/graphs")):

    if not f.endswith(".pkl"):
        continue

    G=pickle.load(open(os.path.join("data/graphs",f),"rb"))

    deg=[d for _,d in G.degree()]

    rows.append({
        "graph":f,
        "family":f.rsplit("_",1)[0],
        "nodes":G.number_of_nodes(),
        "edges":G.number_of_edges(),
        "avg_degree":sum(deg)/len(deg),
        "max_degree":max(deg),
        "degree_std":pd.Series(deg).std(),
        "hub_ratio":max(deg)/(sum(deg)/len(deg)),
        "density":nx.density(G),
        "assortativity":nx.degree_assortativity_coefficient(G)
    })

df=pd.DataFrame(rows)

df.to_csv("results/topology_metrics.csv",index=False)

print(df.groupby("family")[[
    "avg_degree",
    "max_degree",
    "degree_std",
    "hub_ratio"
]].mean().round(2))

print()
print("Saved -> results/topology_metrics.csv")
