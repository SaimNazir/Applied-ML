# Import libraries
from azureml.core import Run, Model
import argparse
import pandas as pd
import numpy as np
import joblib
import os
import pandas as pd
import numpy as np
import lightgbm as lgb

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OrdinalEncoder
from sklearn.compose import ColumnTransformer
from sklearn.metrics import classification_report

# Get parameters
parser = argparse.ArgumentParser()
parser.add_argument(
    "--training-data", type=str, dest="training_data", help="training data"
)
args = parser.parse_args()
training_data = args.training_data

# Get the experiment run context
run = Run.get_context()

# load the prepared data file in the training folder
print("Loading Data...")
file_path = os.path.join(training_data, "data.csv")
df_data = pd.read_csv(file_path)

# Separate features and labels
X = df_data.iloc[:, :-1]
y = df_data.iloc[:, -1:]

# Split data into training set and test set
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=df_data["is_defect"],
)
# Train adecision tree model
print("Training a decision tree model...")
y_train_tr = y_train.to_numpy().ravel()
y_test_tr = y_test.to_numpy().ravel()


def split_num_cat(train_x):

    # Get list of numerical variables
    num_variables = train_x.select_dtypes(include="number").columns.tolist()
    print(num_variables, len(num_variables), "numerical variables")

    # Get list of categorical variables
    cat_variables = train_x.select_dtypes(exclude="number").columns.tolist()
    print(cat_variables, len(cat_variables), "categorical variables")

    return num_variables, cat_variables


numeric_variables, categorical_variables = split_num_cat(X_train)


num_pipeline = Pipeline(
    steps=[("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]
)


cat_pipeline = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="constant", fill_value="none")),
        (
            "labelencoder",
            OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1),
        ),
    ]
)


preprocessor = ColumnTransformer(
    transformers=[
        ("number", num_pipeline, numeric_variables),
        ("category", cat_pipeline, categorical_variables),
    ]
)


"""Baseline"""


def evalu(model, cv=True):

    process = Pipeline(steps=[("preprocessor", preprocessor), ("clf", model)])

    model_fitted = process.fit(X_train, y_train_tr)
    y_pred = model_fitted.predict(X_test)

    print(classification_report(y_test_tr, y_pred))

    if cv == True:
        scores = cross_val_score(
            model_fitted, X_test, y_test_tr, cv=3, scoring="recall"
        )
        print(scores.mean())

    return model_fitted, y_pred


model, baseline_pred = evalu(lgb.LGBMClassifier())

# Save the trained model in the outputs folder
print("Saving model...")
os.makedirs("outputs", exist_ok=True)
model_file = os.path.join("outputs", "model.pkl")
joblib.dump(value=model, filename=model_file)

# Register the model
print("Registering model...")
Model.register(
    workspace=run.experiment.workspace,
    model_path=model_file,
    model_name="model",
    tags={"Training context": "Pipeline"},
)


run.complete()
