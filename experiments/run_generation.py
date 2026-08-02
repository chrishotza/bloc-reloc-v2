import os
import pickle

from src.bloc_reloc_v2.generators import GENERATORS


os.makedirs("data/graphs", exist_ok=True)

for name, generator in GENERATORS.items():
    for seed in range(30):
        G = generator(seed=seed)

        path = f"data/graphs/{name}_{seed}.pkl"

        with open(path, "wb") as f:
            pickle.dump(G, f)

print("Graphs generated successfully")
