#!/usr/bin/env python3

import os
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np

from sklearn.preprocessing import LabelEncoder

from sklearn.model_selection import StratifiedKFold, cross_validate

from sklearn.metrics import (
    confusion_matrix,
    classification_report
)

from sklearn.tree import DecisionTreeClassifier

from sklearn.ensemble import (
    RandomForestClassifier,
    ExtraTreesClassifier,
    GradientBoostingClassifier
)

DATA="results/regime_dataset_clean.csv"

df=pd.read_csv(DATA)

# ============================================================
# REMOVE RARE CLASSES
# ============================================================

counts=df.best_policy.value_counts()

rare=counts[counts<2].index.tolist()

if rare:

    print()
    print("Rare classes removed:",rare)

    df=df[~df.best_policy.isin(rare)].copy()

# ============================================================
# FEATURES
# ============================================================

DROP=[

    "graph",
    "family",
    "best_policy"

]

X=df.drop(columns=DROP)

X=X.fillna(0)

le=LabelEncoder()

y=le.fit_transform(df.best_policy)

feature_names=list(X.columns)

# ============================================================
# MODELS
# ============================================================

models={

"DecisionTree":
DecisionTreeClassifier(
max_depth=5,
random_state=42
),

"RandomForest":
RandomForestClassifier(
n_estimators=500,
random_state=42,
n_jobs=-1
),

"ExtraTrees":
ExtraTreesClassifier(
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

importance_rows=[]

summary=[]

best_model=None
best_score=-1

print("="*90)
print("CLEAN REGIME VALIDATION")
print("="*90)

for name,model in models.items():

    scores=cross_validate(

        model,

        X,

        y,

        cv=cv,

        scoring={

            "acc":"accuracy",

            "bal":"balanced_accuracy",

            "f1":"f1_macro"

        },

        return_estimator=True

    )

    acc=np.mean(scores["test_acc"])
    bal=np.mean(scores["test_bal"])
    f1=np.mean(scores["test_f1"])

    print()
    print("-"*90)
    print(name)
    print("-"*90)

    print(f"Accuracy          : {acc:.4f}")
    print(f"Balanced Accuracy : {bal:.4f}")
    print(f"Macro F1          : {f1:.4f}")

    summary.append({

        "model":name,

        "accuracy":acc,

        "balanced_accuracy":bal,

        "macro_f1":f1

    })

    model.fit(X,y)

    if acc>best_score:

        best_score=acc
        best_model=(name,model)

    imp=pd.Series(

        model.feature_importances_,

        index=feature_names

    ).sort_values(ascending=False)

    print()
    print(imp.head(15))

    for r,(feat,val) in enumerate(imp.items(),1):

        importance_rows.append({

            "model":name,

            "rank":r,

            "feature":feat,

            "importance":val

        })

    pred=model.predict(X)

    cm=confusion_matrix(y,pred)

    print()
    print("Confusion Matrix")
    print(cm)

    print()
    print(classification_report(

        y,

        pred,

        target_names=le.classes_

    ))

# ============================================================
# SAVE REPORTS
# ============================================================

summary=pd.DataFrame(summary)

summary.to_csv(

    "results/model_validation_summary.csv",

    index=False

)

importance=pd.DataFrame(importance_rows)

importance.to_csv(

    "results/model_feature_importance_clean.csv",

    index=False

)

consensus=(

    importance[
        importance["rank"]<=10
    ]

    .groupby("feature")

    .agg(

        appearances=("model","count"),

        mean_rank=("rank","mean"),

        mean_importance=("importance","mean")

    )

    .sort_values(

        ["appearances","mean_rank"],

        ascending=[False,True]

    )

)

consensus.to_csv(

    "results/consensus_variables_clean.csv"

)

print()
print("="*90)
print("CONSENSUS")
print("="*90)
print(consensus)

# ============================================================
# SHAP (optional)
# ============================================================

try:

    import shap

    model_name,model=best_model

    print()
    print("="*90)
    print("SHAP")
    print("="*90)
    print("Best model:",model_name)

    explainer=shap.TreeExplainer(model)

    values=explainer.shap_values(X)

    if isinstance(values,list):

        vals=np.mean(

            np.abs(np.stack(values)),

            axis=(0,1)

        )

    else:

        vals=np.mean(

            np.abs(values),

            axis=0

        )

    shap_df=pd.DataFrame({

        "feature":feature_names,

        "mean_abs_shap":vals

    }).sort_values(

        "mean_abs_shap",

        ascending=False

    )

    shap_df.to_csv(

        "results/shap_importance.csv",

        index=False

    )

    print()
    print(shap_df.head(20))

except Exception as e:

    print()
    print("SHAP skipped:",e)

print()
print("="*90)
print("FILES GENERATED")
print("="*90)

print("results/model_validation_summary.csv")
print("results/model_feature_importance_clean.csv")
print("results/consensus_variables_clean.csv")

if os.path.exists("results/shap_importance.csv"):
    print("results/shap_importance.csv")

