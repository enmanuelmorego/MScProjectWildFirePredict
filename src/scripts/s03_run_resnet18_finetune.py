#from ml_models.resnet_fine_tune import fine_tune_resnet18
from ml_models.resnet_fine_tune import FineTuneDataset
from scripts.s00_set_parameters import PARAMETERS
from data_io.sentinel2_io import load_sentinel2_as_arrays

from torchvision.models import (resnet18, ResNet18_Weights)

import utils.file_utils as fu
import ml_models.ml_utils as mu

import pandas as pd
import numpy as np
import torch

"""
This module and process follows the structure and logic of the PyTorch tutorial on transfer learning:
https://pytorch.org/tutorials/beginner/transfer_learning_tutorial.html    
"""
# ==================
# LOAD PARAMETERS
# =================
DATA_DIR = PARAMETERS['DATA_DIR']
# Please note that parameters specific to data preparation and fine tuning are defined in this module
# as the fine tuning process is not part of the regular execution of this program
n_load_files_sentinel = 2 # Set to None to load all available Sentinel-2 data files
                          # Set to an integer to limit the number of files loaded for testing purposes
dataloaders_batch_size = 4
dataloaders_num_workers = 0


model_basic = resnet18(weights = ResNet18_Weights.DEFAULT)

# ==================
# DATA PREPARATION
# ==================
# Load data 
files_sentinel          = fu.get_filepaths(DATA_DIR, "Sentinel2", "npz")
all_x, all_y, all_dates = load_sentinel2_as_arrays(files_sentinel, n_load = n_load_files_sentinel)
# Create temporary metadata dataframe
df_metadata = pd.DataFrame({"idx": np.arange(len(all_x)), 
                            "date": all_dates})
# Split into train and test
df_train, df_test = mu.train_test_temporal_split(df_metadata, sort_col = 'date', train_size = 0.7)
# Extract indices to fetch observations from the arrays 
train_idx = df_train["idx"].to_numpy()
test_idx  = df_test["idx"].to_numpy()
# Create datasets and dataloaders
image_dataset = {'train': FineTuneDataset(all_x[train_idx], all_y[train_idx]), # type: ignore
                 'val'  : FineTuneDataset(all_x[test_idx],  all_y[test_idx])}  # type: ignore
dataloaders   = {'train': torch.utils.data.DataLoader(image_dataset['train'], batch_size=dataloaders_batch_size, shuffle=True,  num_workers=dataloaders_num_workers),
                 'val'  : torch.utils.data.DataLoader(image_dataset['val'],   batch_size=dataloaders_batch_size, shuffle=False, num_workers=dataloaders_num_workers)}
dataset_sizes = {x: len(image_dataset[x]) for x in ['train', 'val']}
class_names   = ["No Fire", "Fire"]
device        = ("cuda" if torch.cuda.is_available() else "cpu")

# ===================
# VALIDATION
# =================
inputs, labels = next(iter(dataloaders["train"]))

print(f"Using device: {device}")

print(f"1. Passed Expected format: {inputs.shape == (dataloaders_batch_size, 3, 128, 128)}")
print(inputs.shape)

print(f"2. Passed Expected format: {labels.shape == (dataloaders_batch_size,)}")
print(labels.shape)
