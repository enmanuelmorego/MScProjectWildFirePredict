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
|- tests/       # Unit tests
```
## Codebase
Contains the code for the project 

```
MScProjectWildFirePredict/
|- src
|   | - utils/
|       |- file_utils.py [get_file_paths(), select_files()]
|   | - datasets/
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
## Scripts
This folder contains the modules that performs specific step in the program.
These are split into separate, independent components as they are usually run in isolation, but the outputs of the previous feeds onto the next. 

The file structure is shown below, but an in text explanation is also provided for clarity 

`validation_checks.py` = Contains functions used to check and validate expected rules for when the program is being executed

`set_parameters.py` = Define all the values for the variables to be used by all scripts in the program. This includes years to process, file names, etc. This module is called by all modules below.

*Note:*

*`set_parameters.py` has a date field which needs to be updated with the date of run. A safeguard is implemented to ensure parameters are reviewed before execution. 
If the configuration date does not match the current run date, a warning is raised.*

`run_tabular.py` = Loads and processes all tabular data in the project. It also performs preprocessing steps and sampling. The output are `.csv` files with the preprocessed and sampled data

`run_satellite_fetch.py` = Loads the `.csv` preprocessed and sampled data and fetches the Sentinel-2 data from GEE. Stores Sentinel2-2 data as `.npz` files to local disk.

`run_feature_extraction.py` = Loads the `.npz` files and uses a CNN architecture to extract the features to be used in the analysis. This module also loads the sampled `.csv` files and joins them. It saves `.csv` per year containing all data ready for modelling. 

`run_train_ml_model.py` = Trains the model
....
```
MScProjectWildFirePredict/
|- scripts/
|   |- validation_checks.py
|   |- set_parameters.py
|   |- run_tabular.py
|   |- run_satellite_fetch.py
|   |- run_feature_extraction.py
|   |- run_train_ml_model.py
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