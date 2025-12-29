!pip3 install pgmpy
import pandas as pd
from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.estimators import MaximumLikelihoodEstimator
from pgmpy.inference import VariableElimination

def build_dbn(csv_path="traits.csv"):
    df = pd.read_csv(csv_path, header=1)

    df['Base of costa with two pale interruptions'] = (
        df['Base of costa with two pale interruptions'].fillna('')
    )

    features = [c for c in df.columns if c not in
                ["Species", "Region", "Considered", "Probability", "Image"]]

    edges = [("Species", f) for f in features]
    model = DiscreteBayesianNetwork(edges)

    model.fit(df, estimator=MaximumLikelihoodEstimator)
    inference = VariableElimination(model)

    return model, inference, features
