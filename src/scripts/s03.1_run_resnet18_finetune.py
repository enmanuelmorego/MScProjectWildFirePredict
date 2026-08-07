
from ml_models.resnet_fine_tune import FineTuneDataset, fine_tune_resnet18
from scripts.s00_set_parameters import PARAMETERS
from data_io.sentinel2_io import load_sentinel2_as_arrays

from torchvision.models import (resnet18, ResNet18_Weights)

import utils.file_utils as fu
import ml_models.ml_utils as mu
import utils.validation_checks as vc

import pandas as pd
import numpy as np

import torch
import time

"""
This module and process follows the structure and logic of the PyTorch tutorial on transfer learning:
https://pytorch.org/tutorials/beginner/transfer_learning_tutorial.html    
"""
start_time = time.time()
# ==================
# LOAD PARAMETERS
# =================
DATA_DIR = PARAMETERS['DATA_DIR']
# Please note that parameters specific to data preparation and fine tuning are defined in this module
# as the fine tuning process is not part of the regular execution of this program
n_load_files_sentinel = None # Set to None to load all available Sentinel-2 data files
                             # Set to an integer to limit the number of files loaded for testing purposes
dataloaders_batch_size = 2
dataloaders_num_workers = 0

# ==================
# DATA PREPARATION
# ==================
# Load data 
files_sentinel          = fu.get_filepaths(DATA_DIR, "Sentinel2", "npz")
all_x, all_y, all_composite_keys, all_dates = load_sentinel2_as_arrays(files_sentinel, n_load = n_load_files_sentinel)
# Create temporary metadata dataframe
df_metadata = pd.DataFrame({"idx"          : np.arange(len(all_x)), 
                            "date"         : all_dates,
                            'composite_key': all_composite_keys,})
# Split into train and test
df_train, df_validation, df_test = mu.train_validate_test_temporal_split(df_metadata, sort_col = 'date', train_size = 0.6, val_size=0.2, test_size=0.2)
vc.validate_train_validation_test_split(df_train, df_validation, df_test)
# Save train, validation, test 
df_train_val_test = pd.DataFrame({"composite_key": pd.concat([df_train["composite_key"],
                                                              df_validation["composite_key"],
                                                              df_test["composite_key"]], ignore_index=True),
                                  "split_category": (["train"] * len(df_train) +
                                                     ["validation"] * len(df_validation) +
                                                     ["test"] * len(df_test))})
df_train_val_test.to_csv(DATA_DIR/"MLInputs"/"train_val_test_split.csv")

# Extract indices to fetch observations from the arrays 
train_idx      = df_train["idx"].to_numpy()
validation_idx = df_validation["idx"].to_numpy()
# Create datasets and dataloaders
image_dataset = {'train': FineTuneDataset(all_x[train_idx],       all_y[train_idx]), # type: ignore
                 'val'  : FineTuneDataset(all_x[validation_idx],  all_y[validation_idx])}  # type: ignore
dataloaders   = {'train': torch.utils.data.DataLoader(image_dataset['train'], batch_size=dataloaders_batch_size, shuffle=True,  num_workers=dataloaders_num_workers),
                 'val'  : torch.utils.data.DataLoader(image_dataset['val'],   batch_size=dataloaders_batch_size, shuffle=False, num_workers=dataloaders_num_workers)}
dataset_sizes = {x: len(image_dataset[x]) for x in ['train', 'val']}
class_names   = ["No Fire", "Fire"]
device        = ("cuda" if torch.cuda.is_available() else "cpu")

# ===================
# VALIDATION
# =================
inputs, labels = next(iter(dataloaders["train"]))

print(f"=============\n🤖 Using device: {device}\n=============")

print(f"1. Passed Expected format: {inputs.shape == (dataloaders_batch_size, 3, 128, 128)}")
print(inputs.shape)

print(f"2. Passed Expected format: {labels.shape == (dataloaders_batch_size,)}")
print(labels.shape)
# ===================
# FINE TUNING
# =================
model_basic = resnet18(weights = ResNet18_Weights.DEFAULT)
# Freeze all layers
for param in model_basic.parameters():
    param.requires_grad = False
# Unfreeze layer 4
for param in model_basic.layer4.parameters():
    param.requires_grad = True
# Replace classifier 
num_features = model_basic.fc.in_features
model_basic.fc = torch.nn.Linear(num_features, 2)

# Move model to GPU
model_basic = model_basic.to(device)

# Check which parameters are being optimized
print("\n==============\n🔧  Fine tuning model parameters\n=============")
for name, param in model_basic.named_parameters():
    print(f"{name:<40} | {param.requires_grad}")

criterion   = torch.nn.CrossEntropyLoss()
optimizer  = torch.optim.SGD(model_basic.parameters(), lr=0.001, momentum=0.9) #torch.optim.Adam(filter(lambda p: p.requires_grad, model_basic.parameters()), lr=0.001)#torch.optim.SGD(model_basic.parameters(), lr=0.001, momentum=0.9)

model_finetuned = fine_tune_resnet18(model = model_basic, 
                                     criterion = criterion, 
                                     optimizer = optimizer, 
                                     scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.1),
                                     num_epochs = 25, 
                                     dataloaders = dataloaders, 
                                     device = device)

torch.save(model_finetuned.state_dict(),DATA_DIR / "MLModels" / "resnet18_layer4_finetuned.pt")

time_elapsed = time.time() - start_time
print(f'🕰️  Script complete in {time_elapsed // 60:.0f}m {time_elapsed % 60:.0f}s')