#!/usr/bin/env python3

import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.tree import DecisionTreeClassifier

print("="*70)
print("MULTIVARIATE TOPOLOGY ANALYSIS")
print("="*70)

topo=pd.read_csv("results/topology_profiler.csv")
exp=pd.read_csv("results/affinity_ablation.csv")

pivot=exp.pivot(
    index="graph",
    columns="variant",
    values="edge_cut"
)

pivot["improvement"]=pivot["baseline"]-pivot["affinity_modified"]
pivot["improvement_%"]=100*pivot["improvement"]/pivot["baseline"]

df=topo.merge(
    pivot[["improvement","improvement_%"]],
    left_on="graph",
    right_index=True
)

features=[
    "density",
    "avg_degree",
    "degree_std",
    "max_degree",
    "hub_ratio",
    "degree_gini",
    "clustering",
    "transitivity",
    "core_number",
    "diameter",
    "avg_path",
    "communities",
    "modularity"
]

X=df[features].copy()
X=X.fillna(X.mean())

print()
print("="*70)
print("CORRELATION WITH IMPROVEMENT")
print("="*70)

corr=X.copy()
corr["improvement_%"]=df["improvement_%"]

print(
    corr.corr(numeric_only=True)["improvement_%"]
    .sort_values(ascending=False)
)

print()
print("="*70)
print("PCA")
print("="*70)

Xs=StandardScaler().fit_transform(X)

pca=PCA(n_components=2)

Y=pca.fit_transform(Xs)

df["PC1"]=Y[:,0]
df["PC2"]=Y[:,1]

print("Explained variance:")
print(np.round(pca.explained_variance_ratio_,4))

print()

print(df.groupby("family")[["PC1","PC2"]].mean())

print()
print("="*70)
print("KMEANS")
print("="*70)

km=KMeans(
    n_clusters=4,
    random_state=42,
    n_init=20
)

df["cluster"]=km.fit_predict(Xs)

print(
    pd.crosstab(
        df.family,
        df.cluster
    )
)

print()
print("="*70)
print("DECISION TREE")
print("="*70)

y=np.where(
    df.improvement>0,
    "WIN",
    np.where(
        df.improvement<0,
        "LOSS",
        "DRAW"
    )
)

tree=DecisionTreeClassifier(
    max_depth=4,
    random_state=42
)

tree.fit(Xs,y)

imp=pd.Series(
    tree.feature_importances_,
    index=features
).sort_values(ascending=False)

print(imp)

print()
print("="*70)
print("TOP 10 VARIABLES")
print("="*70)

print(imp.head(10))

df.to_csv(
    "results/topology_multivariate.csv",
    index=False
)

print()
print("Saved -> results/topology_multivariate.csv")
