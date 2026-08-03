#!/usr/bin/env python3

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

from sklearn.preprocessing import LabelEncoder

from sklearn.model_selection import (
    StratifiedKFold,
    cross_validate,
    cross_val_predict
)

from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    accuracy_score,
    balanced_accuracy_score,
    f1_score
)

from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier
)

# ==========================================================
# LOAD
# ==========================================================

df=pd.read_csv("results/regime_dataset_clean.csv")

# remove rare classes

counts=df.best_policy.value_counts()

rare=counts[counts<2].index.tolist()

if rare:
    df=df[~df.best_policy.isin(rare)].copy()

# ==========================================================
# LABELS
# ==========================================================

le=LabelEncoder()

y=le.fit_transform(df.best_policy)

# ==========================================================
# FEATURE SETS
# ==========================================================

drop_common=[
    "graph",
    "family",
    "best_policy"
]

topology_only=[

    c for c in df.columns

    if c not in drop_common

    and not c.startswith("early_")

    and c not in [

        "runtime_baseline",

        "cost_after5",

        "edgecut_after5",

        "plateau_iteration"

    ]

]

warmup=topology_only+[

    "early_acceptance_mean",
    "early_acceptance_std",
    "early_acceptance_max",
    "early_acceptance_min",
    "early_edgecut_slope",
    "early_cost_slope"

]

datasets={

    "TopologyOnly":topology_only,

    "WarmupScheduler":warmup

}

models={

    "RandomForest":
        RandomForestClassifier(
            n_estimators=500,
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

summary=[]
importance=[]

# ==========================================================
# RUN
# ==========================================================

for ds_name,cols in datasets.items():

    X=df[cols].fillna(0)

    print()
    print("="*90)
    print(ds_name)
    print("="*90)

    for model_name,model in models.items():

        print()
        print(model_name)

        scores=cross_validate(

            model,

            X,

            y,

            cv=cv,

            scoring={

                "acc":"accuracy",

                "bal":"balanced_accuracy",

                "f1":"f1_macro"

            }

        )

        pred=cross_val_predict(

            model,

            X,

            y,

            cv=cv

        )

        acc=accuracy_score(y,pred)
        bal=balanced_accuracy_score(y,pred)
        f1=f1_score(y,pred,average="macro")

        print(f"Accuracy          : {acc:.4f}")
        print(f"Balanced Accuracy : {bal:.4f}")
        print(f"Macro F1          : {f1:.4f}")

        cm=confusion_matrix(y,pred)

        print()
        print(cm)

        print()
        print(classification_report(

            y,

            pred,

            target_names=le.classes_

        ))

        summary.append({

            "dataset":ds_name,

            "model":model_name,

            "accuracy":acc,

            "balanced_accuracy":bal,

            "macro_f1":f1

        })

        model.fit(X,y)

        imp=pd.Series(

            model.feature_importances_,

            index=cols

        ).sort_values(

            ascending=False

        )

        print()
        print("TOP VARIABLES")
        print(imp.head(15))

        for r,(feat,val) in enumerate(imp.items(),1):

            importance.append({

                "dataset":ds_name,

                "model":model_name,

                "rank":r,

                "feature":feat,

                "importance":val

            })

# ==========================================================
# SAVE
# ==========================================================

pd.DataFrame(summary).to_csv(

    "results/regime_split_summary.csv",

    index=False

)

pd.DataFrame(importance).to_csv(

    "results/regime_split_importance.csv",

    index=False

)

print()
print("="*90)
print("FILES")
print("="*90)
print("results/regime_split_summary.csv")
print("results/regime_split_importance.csv")
