#!/usr/bin/env python3

import pandas as pd
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.preprocessing import LabelEncoder

# ==========================
# LOAD DATA
# ==========================

topo = pd.read_csv("results/topology_multivariate.csv")

dyn = pd.read_csv("results/search_dynamics.csv")

# ==========================
# FINAL STATE OF EACH RUN
# ==========================

final = (
    dyn.sort_values("iteration")
       .groupby(["graph","configuration"])
       .tail(1)
       .copy()
)

# plateau

plateau=[]

for (g,cfg),x in dyn.groupby(["graph","configuration"]):

    x=x.sort_values("iteration")

    last=x.edge_cut.iloc[-1]

    p=int(x[x.edge_cut==last].iteration.min())

    plateau.append({
        "graph":g,
        "configuration":cfg,
        "plateau":p
    })

plateau=pd.DataFrame(plateau)

final=final.merge(
    plateau,
    on=["graph","configuration"]
)

# ==========================
# BEST CONFIGURATION
# ==========================

best=(
    final.sort_values("edge_cut")
         .groupby("graph")
         .head(1)
)

master=topo.merge(
    best[
        [
            "graph",
            "configuration",
            "edge_cut",
            "runtime",
            "plateau",
            "acceptance_ratio"
        ]
    ],
    on="graph"
)

master.rename(
    columns={
        "configuration":"best_policy",
        "edge_cut":"best_cut"
    },
    inplace=True
)

master.to_csv(
    "results/meta_learning_dataset.csv",
    index=False
)

# ==========================
# FEATURES
# ==========================

features=[

"density",
"avg_degree",
"degree_std",
"max_degree",
"hub_ratio",
"degree_gini",
"clustering",
"transitivity",
"assortativity",
"core_number",
"diameter",
"avg_path",
"spectral_radius",
"algebraic_connectivity",
"communities",
"modularity",
"PC1",
"PC2",
"cluster"

]

X=master[features].fillna(0)

enc=LabelEncoder()

y=enc.fit_transform(master.best_policy)

# ==========================
# TREE
# ==========================

tree=DecisionTreeClassifier(
    max_depth=4,
    random_state=42
)

tree.fit(X,y)

importance=pd.Series(
    tree.feature_importances_,
    index=features
).sort_values(ascending=False)

print("="*80)
print("FEATURE IMPORTANCE")
print("="*80)

print(importance.round(4))

print()

print("="*80)
print("DECISION RULES")
print("="*80)

print(
    export_text(
        tree,
        feature_names=features
    )
)

print()

print("="*80)
print("BEST POLICY DISTRIBUTION")
print("="*80)

print(
    master.best_policy
          .value_counts()
)

importance.to_csv(
    "results/meta_feature_importance.csv"
)

with open(
    "results/meta_decision_tree.txt",
    "w"
) as f:

    f.write(
        export_text(
            tree,
            feature_names=features
        )
    )

print()

print("Saved:")
print(" results/meta_learning_dataset.csv")
print(" results/meta_feature_importance.csv")
print(" results/meta_decision_tree.txt")

