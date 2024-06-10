import os
import pickle
import sys
from collections import defaultdict
from pathlib import Path

cands_all = defaultdict(dict)
for filename in os.listdir(sys.argv[1]):
    if filename[-7:] != ".pickle" or filename == "cands_all.pickle":
        continue
    filepath = Path(sys.argv[1]) / filename
    with open(filepath, "rb") as f:
        data = pickle.load(f)
    for word, pos, ps, pairs in data:
        cands_all[pos][word] = (ps, pairs)

with open(Path(sys.argv[1]) / "cands_all.pickle", "wb") as f:
    pickle.dump(cands_all, f)
