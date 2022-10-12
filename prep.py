# Import libraries
import os
import argparse
import pandas as pd
from azureml.core import Run, Dataset, Workspace

# Get parameters
parser = argparse.ArgumentParser()
parser.add_argument("--input-data", type=str, dest="raw_dataset_id", help="raw dataset")
parser.add_argument(
    "--prepped-data",
    type=str,
    dest="prepped_data",
    default="prepped_data",
    help="Folder for results",
)
args = parser.parse_args()
save_folder = args.prepped_data

# Get the experiment run context
run = Run.get_context()

# load the data (passed as an input dataset)
print("Loading Data...")

ws = Workspace.from_config()
df = Dataset.get_by_name(ws, name="batch-data")  # how get data there remember
df.download(target_path=".", overwrite=True)


num_variables = df.select_dtypes(include="number").columns.tolist()
cat_variables = df.select_dtypes(exclude="number").columns.tolist()


df_1 = df.copy()

# Remove nulls
def get_NA_cols(dataframe):

    percent = (
        dataframe.isnull().sum() / dataframe.isnull().count()
    ).sort_values() * 100
    percent = percent[percent > 30]

    ls = list(percent.index)
    ls.remove("RootCause")
    return ls


columns = get_NA_cols(df_1)
df_1.drop(columns, axis=1, inplace=True)

# Save the prepped data
print("Saving Data...")
os.makedirs(save_folder, exist_ok=True)
save_path = os.path.join(save_folder, "data.csv")
df_1.to_csv(save_path, index=False, header=True)

# End the run
run.complete()
