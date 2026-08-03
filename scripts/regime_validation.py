#!/usr/bin/env python3

import pandas as pd
import numpy as np

from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    RandomForestClassifier,
    ExtraTreesClassifier,
    GradientBoostingClassifier
)
from sklearn.model_selection import StratifiedKFold,cross_val_score

DATA="results/regime_dataset.csv"

df=pd.read_csv(DATA)

# ==========================================================
# FEATURES
# ==========================================================

drop=[

    "graph",
    "family",
    "configuration",
    "best_policy",
    "final_edge_cut"

]

X=df.drop(columns=drop)

X=X.fillna(0)

y=LabelEncoder().fit_transform(df.best_policy)

# ==========================================================
# MODELS
# ==========================================================

models={

    "DecisionTree":
        DecisionTreeClassifier(
            max_depth=5,
            random_state=42
        ),

    "RandomForest":
        RandomForestClassifier(
            n_estimators=400,
            random_state=42,
            n_jobs=-1
        ),

    "ExtraTrees":
        ExtraTreesClassifier(
            n_estimators=400,
            random_state=42,
            n_jobs=-1
        ),

    "GradientBoosting":
        GradientBoostingClassifier(
            random_state=42
        )

}

cv=StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

importance_table=[]

print("="*90)
print("MODEL VALIDATION")
print("="*90)

for name,model in models.items():

    scores=cross_val_score(
        model,
        X,
        y,
        cv=cv,
        scoring="accuracy"
    )

    model.fit(X,y)

    imp=pd.Series(
        model.feature_importances_,
        index=X.columns
    ).sort_values(
        ascending=False
    )

    print()
    print("-"*90)
    print(name)
    print("-"*90)

    print(
        f"Accuracy : "
        f"{scores.mean():.4f}"
        f" +/- {scores.std():.4f}"
    )

    print()

    print(
        imp.head(15)
    )

    for rank,(feat,val) in enumerate(imp.items(),1):

        importance_table.append({

            "model":name,

            "rank":rank,

            "feature":feat,

            "importance":val

        })

importance=pd.DataFrame(
    importance_table
)

importance.to_csv(
    "results/model_feature_importance.csv",
    index=False
)

# ==========================================================
# CONSENSUS
# ==========================================================

top10=(
    importance[
        importance.rank<=10
    ]
)

consensus=(
    top10.groupby("feature")
         .agg(

            appearances=(
                "model",
                "count"
            ),

            mean_importance=(
                "importance",
                "mean"
            ),

            mean_rank=(
                "rank",
                "mean"
            )

         )
         .sort_values(

            [
                "appearances",
                "mean_rank"
            ],

            ascending=[False,True]

         )

)

print()
print("="*90)
print("CONSENSUS VARIABLES")
print("="*90)

print(
    consensus
)

consensus.to_csv(
    "results/consensus_variables.csv"
)

print()

print("Saved:")

print(" results/model_feature_importance.csv")

print(" results/consensus_variables.csv")

