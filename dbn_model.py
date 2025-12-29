from pathlib import Path
import pandas as pd
from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.estimators import MaximumLikelihoodEstimator
from pgmpy.inference import VariableElimination

HERE = Path(__file__).resolve().parent

def build_dbn(csv_path=None):
    if csv_path is None:
        csv_path = HERE / "traits.csv"
    else:
        csv_path = Path(csv_path)

    df = pd.read_csv(csv_path, header=3)
    df.columns = df.columns.astype(str).str.strip()

    features = [
        c for c in df.columns
        if c not in {"Species", "Region", "Considered", "Probability", "Image"}
    ]
    for f in features:
        df[f] = df[f].fillna(-1).astype(int)
        
    edges = [("Species", f) for f in features]

    model = DiscreteBayesianNetwork(edges)

    state_names = {
            f: [-1, 0, 1] for f in features
        }
    state_names["Scutal scales as in (A, B, C or D):"] = [0,1,2,3]

    state_names["Species"] = sorted(df["Species"].dropna().unique())
    model.fit(
        df,
        estimator=MaximumLikelihoodEstimator,
        state_names = state_names
    )

    assert model.get_cpds("Species").is_valid_cpd()

    inference = VariableElimination(model)

    return model, inference, features
