import pandas as pd
from pathlib import Path
from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.estimators import MaximumLikelihoodEstimator
from pgmpy.inference import VariableElimination

HERE = Path(__file__).resolve().parent

def build_dbn(csv_path=None):
    if csv_path is None:
        csv_path = HERE / "traits.csv"
    else:
        csv_path = Path(csv_path)

    if not csv_path.exists():
        raise FileNotFoundError(f"DBN training file not found: {csv_path}")

    df = pd.read_csv(csv_path, header=3)
    features = [
        c for c in df.columns
        if c not in ["Species", "Region", "Considered", "Probability", "Image"]
    ]

    edges = [("Species", f) for f in features]
    model = DiscreteBayesianNetwork(edges)
    model.fit(df, estimator=MaximumLikelihoodEstimator)

    inference = VariableElimination(model)

    return model, inference, features
