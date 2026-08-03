import pandas as pd

df=pd.read_csv("results/affinity_ablation.csv")

pivot=df.pivot(index="graph",columns="variant",values="edge_cut")

pivot["improvement_%"]=100*(pivot["baseline"]-pivot["affinity_modified"])/pivot["baseline"]

print()
print("="*70)
print("AFFINITY VALIDATION")
print("="*70)

print()
print("Graphs:",len(pivot))

print()
print("Mean improvement (%):",round(pivot["improvement_%"].mean(),3))
print("Median:",round(pivot["improvement_%"].median(),3))
print("Std:",round(pivot["improvement_%"].std(),3))

print()
print("Wins :",int((pivot["improvement_%"]>0).sum()))
print("Draws:",int((pivot["improvement_%"]==0).sum()))
print("Loss :",int((pivot["improvement_%"]<0).sum()))

print()
print("Top 10 improvements")
print(
    pivot["improvement_%"]
    .sort_values(ascending=False)
    .head(10)
)

print()
print("Worst 10")
print(
    pivot["improvement_%"]
    .sort_values()
    .head(10)
)
