#from ml_models.resnet_fine_tune import fine_tune_resnet18
from ml_models.resnet_feature_extractor import SentinelData
from scripts.s00_set_parameters import PARAMETERS

from torchvision.models import (resnet18, ResNet18_Weights)

import utils.file_utils as fu

import numpy as np

# Load parameters
DATA_DIR = PARAMETERS['DATA_DIR']

# Load basic model
model_basic = resnet18(weights = ResNet18_Weights.DEFAULT)
# Load data 
files_sentinel = fu.get_filepaths(DATA_DIR, "Sentinel2", "npz")
counter = 0
all_x = []
all_y = []
all_dates = []
n = len(files_sentinel)
for f in files_sentinel:
    data = SentinelData(f)
    data.get_dates()

    all_x.append(data.x)
    all_y.append(data.y)
    all_dates.append(data.dates)
    counter += 1
    print(f"{counter}/{n}", end = "\r")
# Concatenate all observations into single arrays


print(len(all_x))
print(len(all_y))
print(len(all_dates))
