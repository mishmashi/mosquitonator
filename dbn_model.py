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

    edges = [("Species", f) for f in features]

    model = DiscreteBayesianNetwork(edges)

    model.fit(
        df,
        estimator=MaximumLikelihoodEstimator,
        state_names={
            f: sorted(df[f].dropna().unique())
            for f in features
        }
    )

    assert model.get_cpds("Species").is_valid_cpd()

    inference = VariableElimination(model)

    return model, inference, features
