#!/usr/bin/env python3

import os
import pandas as pd

RESULTS="results"

print("="*90)
print("LAB INVENTORY")
print("="*90)

for f in sorted(os.listdir(RESULTS)):

    path=os.path.join(RESULTS,f)

    if not os.path.isfile(path):
        continue

    size=os.path.getsize(path)/1024

    print(f"{f:45s} {size:10.1f} KB")

print()

print("="*90)
print("CSV SUMMARY")
print("="*90)

for f in sorted(os.listdir(RESULTS)):

    if not f.endswith(".csv"):
        continue

    path=os.path.join(RESULTS,f)

    try:

        df=pd.read_csv(path)

        print()

        print("-"*90)
        print(f)

        print("rows :",len(df))
        print("cols :",len(df.columns))
        print("columns:")

        for c in df.columns:
            print("   ",c)

    except Exception as e:

        print(f)
        print("ERROR:",e)

print()

print("="*90)
print("DONE")
print("="*90)
