from pathlib import Path
import pandas as pd
from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.estimators import MaximumLikelihoodEstimator
from pgmpy.inference import VariableElimination

HERE = Path(__file__).resolve().parent

def build_dbn(csv_path=None):
    if csv_path is None:
        csv_path = HERE / "linked_ds.csv"
    else:
        csv_path = Path(csv_path)

    df = pd.read_csv(csv_path, header=0)
    df.columns = df.columns.astype(str).str.strip()

    features = [
        c for c in df.columns
        if c not in {"Species", "Region", "Considered", "Probability", "Image"}
    ]
    
    for f in features:
        if f == "98":
            df = df[df[f].isin([0,1,2,3])]
        else:
            df = df[df[f].isin([0,1])]
        
    df.columns = (
        list(df.columns[:5]) +
        [str(i) for i, _ in enumerate(features)]
    )

    features = {str(i) for i, _ in enumerate(features)}
    
    edges = [("Species", f) for f in features]
    model = DiscreteBayesianNetwork(edges)
    
    state_names = {f: [0, 1] for f in features}
    state_names["98"] = [0,1,2,3]
    state_names["Species"] = sorted(df["Species"].unique())
    
    model.fit(
        df,
        estimator=MaximumLikelihoodEstimator,
        state_names={
            f: sorted(df[f].dropna().unique())
            for f in features
        }
    )


    inference = VariableElimination(model)

    return model, inference, features
