import pandas as pd
import numpy as np
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent

def build_masked_nb(csv_path=None):
    if csv_path is None:
        csv_path = HERE / "linked_ds.csv"
    else:
        csv_path = Path(csv_path)

    df = pd.read_csv(csv_path)
    df.columns = df.columns.astype(str).str.strip()

    meta_cols = {"Species", "Region", "Considered", "Probability", "Image"}
    features = [c for c in df.columns if c not in meta_cols]

    # Convert to numeric, keep NaN for missing
    for f in features:
        df[f] = pd.to_numeric(df[f], errors="coerce")

    species_list = sorted(df["Species"].unique())

    prior = (
        df["Species"]
        .value_counts(normalize=True)
        .to_dict()
    )

    likelihood = defaultdict(lambda: defaultdict(dict))

    for sp in species_list:
        sub = df[df["Species"] == sp]

        for f in features:
            observed = sub[f].dropna()
            if observed.empty:
                continue

            counts = observed.value_counts().to_dict()
            total = sum(counts.values())

            for val, cnt in counts.items():
                likelihood[sp][f][int(val)] = cnt / total

    return {
        "features": features,
        "species": species_list,
        "prior": prior,
        "likelihood": likelihood
    }
