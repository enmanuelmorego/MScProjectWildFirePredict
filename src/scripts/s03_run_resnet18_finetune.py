#from ml_models.resnet_fine_tune import fine_tune_resnet18
from ml_models.resnet_fine_tune import FineTuneDataset
from scripts.s00_set_parameters import PARAMETERS
from data_io.sentinel2_io import load_sentinel2_as_arrays

from torchvision.models import (resnet18, ResNet18_Weights)

import utils.file_utils as fu
import ml_models.ml_utils as mu

import pandas as pd
import numpy as np

# Load parameters
DATA_DIR = PARAMETERS['DATA_DIR']

# Load basic model
model_basic = resnet18(weights = ResNet18_Weights.DEFAULT)
# Load data 
files_sentinel = fu.get_filepaths(DATA_DIR, "Sentinel2", "npz")
all_x, all_y, all_dates = load_sentinel2_as_arrays(files_sentinel, n_load = 2)
# Create temporary metadata dataframe
df_metadata = pd.DataFrame({"idx": np.arange(len(all_x)), 
                            "date": all_dates})
# Split into train and test
df_train, df_test = mu.train_test_temporal_split(df_metadata, sort_col = 'date', train_size = 0.7)
train_idx = df_train["idx"].to_numpy()
test_idx = df_test["idx"].to_numpy()

print(train_idx.dtype)
print(test_idx.dtype)

image_dataset = {'train': FineTuneDataset(all_x[train_idx], all_y[train_idx]),
                 'val': FineTuneDataset(all_x[test_idx],    all_y[test_idx])
                 }
print(image_dataset["train"][0])