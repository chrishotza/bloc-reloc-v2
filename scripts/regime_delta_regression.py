#!/usr/bin/env python3

import warnings
warnings.filterwarnings("ignore")

import traceback
import numpy as np
import pandas as pd

from sklearn.model_selection import KFold, cross_val_predict

from sklearn.metrics import (
    r2_score,
    mean_absolute_error,
    root_mean_squared_error
)

from sklearn.ensemble import (
    RandomForestRegressor,
    GradientBoostingRegressor
)

# ==========================================================
# LOAD
# ==========================================================

TOPO="results/topology_multivariate.csv"
DYN="results/search_dynamics.csv"

topo=pd.read_csv(TOPO)
dyn=pd.read_csv(DYN)

# ==========================================================
# REMOVE NON-PHYSICAL COLUMNS
# ==========================================================

dropcols=[

    "PC1",
    "PC2",
    "cluster",
    "improvement",
    "improvement_%"

]

topo=topo.drop(
    columns=[c for c in dropcols if c in topo.columns],
    errors="ignore"
)

# ==========================================================
# FINAL RESULTS
# ==========================================================

final=(

    dyn
    .sort_values("iteration")
    .groupby(["graph","configuration"])
    .tail(1)

)[["graph","configuration","edge_cut"]]

pivot=final.pivot(

    index="graph",

    columns="configuration",

    values="edge_cut"

).reset_index()

required=[

    "baseline",
    "affinity",
    "periodic",
    "reactive",
    "affinity_periodic",
    "affinity_reactive"

]

for c in required:

    if c not in pivot.columns:

        raise RuntimeError(f"Missing configuration: {c}")

# ==========================================================
# DELTAS
# ==========================================================

targets=[]

for cfg in required:

    if cfg=="baseline":
        continue

    name=f"delta_{cfg}"

    pivot[name]=pivot[cfg]-pivot["baseline"]

    targets.append(name)

# ==========================================================
# MERGE
# ==========================================================

data=topo.merge(

    pivot,

    on="graph",

    how="inner"

)

feature_cols=[

    c for c in topo.columns

    if c not in [

        "graph",

        "family"

    ]

]

X=(

    data[feature_cols]

    .replace([np.inf,-np.inf],np.nan)

    .fillna(0.0)

)

# force numeric

for c in X.columns:

    X[c]=pd.to_numeric(

        X[c],

        errors="coerce"

    )

X=X.fillna(0.0)

print("="*90)
print("INPUT")
print("="*90)
print("Rows :",len(X))
print("Cols :",len(X.columns))
print("NaN  :",int(X.isna().sum().sum()))
print("Inf  :",int(np.isinf(X.to_numpy()).sum()))

# ==========================================================
# MODELS
# ==========================================================

models={

    "RandomForest":

        RandomForestRegressor(

            n_estimators=500,

            random_state=42,

            n_jobs=-1

        ),

    "GradientBoosting":

        GradientBoostingRegressor(

            random_state=42

        )

}

cv=KFold(

    n_splits=5,

    shuffle=True,

    random_state=42

)

summary=[]
importance=[]

print()
print("="*90)
print("DELTA REGRESSION")
print("="*90)

for target in targets:

    print()
    print("#"*90)
    print(target)
    print("#"*90)

    y=(

        pd.to_numeric(

            data[target],

            errors="coerce"

        )

        .replace([np.inf,-np.inf],np.nan)

        .fillna(0.0)

    )

    for model_name,model in models.items():

        print()
        print(model_name)

        try:

            pred=cross_val_predict(

                model,

                X,

                y,

                cv=cv,

                n_jobs=None

            )

            r2=r2_score(y,pred)
            mae=mean_absolute_error(y,pred)
            rmse=root_mean_squared_error(y,pred)

            print(f"R2   : {r2:.4f}")
            print(f"MAE  : {mae:.4f}")
            print(f"RMSE : {rmse:.4f}")

            summary.append({

                "target":target,
                "model":model_name,
                "R2":r2,
                "MAE":mae,
                "RMSE":rmse

            })

            model.fit(X,y)

            imp=pd.Series(

                model.feature_importances_,

                index=X.columns

            ).sort_values(

                ascending=False

            )

            print()
            print(imp.head(15))

            for rank,(feat,val) in enumerate(imp.items(),1):

                importance.append({

                    "target":target,
                    "model":model_name,
                    "rank":rank,
                    "feature":feat,
                    "importance":val

                })

        except Exception as e:

            print()
            print("MODEL FAILED")
            print(type(e).__name__)
            print(e)

            traceback.print_exc()

            summary.append({

                "target":target,
                "model":model_name,
                "R2":np.nan,
                "MAE":np.nan,
                "RMSE":np.nan

            })

# ==========================================================
# SAVE
# ==========================================================

summary_df=pd.DataFrame(summary)
importance_df=pd.DataFrame(importance)

summary_df.to_csv(

    "results/delta_regression_summary.csv",

    index=False

)

importance_df.to_csv(

    "results/delta_regression_importance.csv",

    index=False

)

print()
print("="*90)
print("FILES GENERATED")
print("="*90)
print("results/delta_regression_summary.csv")
print("results/delta_regression_importance.csv")
print("="*90)

