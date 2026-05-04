# MScProjectWildFirePredict Architecture

The project is divided into modules, which have specific resposibilities. An overview of the modules is shown here, and below, each of the sections is expanded with futher details

## Overview
```
MScProjectWildFirePredict/
|- src/         # The codebase of the program
|- scripts/     # Execution of program, split by flow checkpoints
|- notebooks/   # Reads outputs/transformations, contains analysis
|- data/        # Input data used in the project
|- outputs/     # Output objects from analysis
```
## Codebase
Contains all of the code for the project 

Note to self (delete later):
```
list(Path(<some_path>).glob("*"))
```
```
MScProjectWildFirePredict/
|- src
|   | - utils/
|       |- file_utils.py [get_file_paths(), select_files()]
|   | - data/
|       |- viirs/
|       |   |- loader.py
|       |   |- transforms.py
|       |   |- pipeline.py
|       |   |- output.py [where reelevant]
|       |- fwi/
|       |   |- loader.py
|       |   |- transforms.py
|       |   |- pipeline.py
|       |- ukgrid/
|       |   |- loader.py
|       |   |- transforms.py
|       |   |- pipeline.py
|       |- sentinel2/
|       |   |- loader.py
|       |   |- transforms.py
|       |   |- pipeline.py
|   |- preprocessing/
|   |- ml_model/
|   |   |- feature_extraction.py
|   |   |- create_ml_dataset.py
|   |   |- random_forest.py

``` 
## Data Files
This module contains files and objects used to build the different components of the program. It is further split by type of data, i.e., raw inputs, preprocessed, etc. 
```
|
|- data/
|   |- raw/
|       |- fwi/           # .grib files for each year
|       |- ukgrid/        # .shp files to split UK into grids
|       |- viirs/         # .csv files fire labels for each year
|   |- preprocessed/  
|       |- sampled/       # .csv of sampled data, per year
|       |- sentinel2/     # .npz downloaded from sampled dataset
|       |- satellitefeat/ # .csv of sampled sentinel features
|   |- ml_model_input/    # .csv of sampled + sentinel2 features
```


## Refactor 1 – Generalise file selection
- Replace `to_load_viirs` with generic `select_files`
- Reuse across VIIRS and FWI
- Support filtering by year + suffix