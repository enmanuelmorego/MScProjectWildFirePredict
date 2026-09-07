
# MScProjectWildFirePredict
## Table of Contents

- [Getting Started](#getting-started)
    - [Python 3.11](#python-311)
    - [Install Python 3.11](#install-python-311)
    - [Install Pipenv](#install-pipenv)
    - [Install Project Dependencies](#install-project-dependencies)
    - [Activate Environment](#activate-environment)

- [Project Architecture](#project-architecture)
    - [Overview](#overview)
    - [Codebase](#codebase)
    - [Data Files](#data-files)


## Getting Started

This project requires Python 3.11 and Pipenv

### Check if Python 3.11 is installed

Verify that Python 3.11 is installed 

Open the IDE terminal, and run:

Windows:
```
py --version
```

Mac:
```
python3 --version
```

### Install Python 3.11

If Python 3.11 is not installed, download Python 3.11 from:

https://www.python.org/downloads/release/python-3119/

During the installation, make sure to tick: `Add Python to PATH`

Verify that Python 3.11 was succesfully installed 

Windows:
```
py --version
```

Mac:
```
python3 --version
```

### Install Pipenv

```
pip install pipenv 
```

### Install project dependencies

```
pipenv install
```

### Activate environment
```
pipenv shell
```

## Project Architecture

The project is divided into modules, which have specific responsibilities. An overview of the modules is shown here, and below, each of the sections is expanded with further details.

### Overview
```
| MScProjectWildFirePredict/
|   |- data
|   |   |- FWI
|   |   |   |- Archive
|   |   |- MLInputs
|   |   |- MLModels
|   |   |- SampledFireNoFire
|   |   |- Sentinel2
|   |   |   |- Archive
|   |   |- UKGrid
|   |   |- VIIRS
|   |- outputs
|   |   |- logs
|   |   |- plots
|   |- src
|   |   |- data_io
|   |   |- ml_models
|   |   |- pipelines
|   |   |- reporting
|   |   |- sampling
|   |   |- scripts
|   |   |- transforms
|   |   |- utils
|   |- src_archive
|   |- tests
```

### Codebase
```
MScProjectWildFirePredict/
|- src/
|   |- __init__.py
|   |- data_io
|   |   |- fwi_loader.py
|   |   |- ml_io.py
|   |   |- sampled_loader.py
|   |   |- sampling_writter.py
|   |   |- sentinel2_io.py
|   |   |- ukgrid_loader.py
|   |   |- viirs_loader.py
|   |- ml_models
|   |   |- ml_utils.py
|   |   |- ml_visualisations.py
|   |   |- resnet_feature_extractor.py
|   |   |- resnet_fine_tune.py
|   |- pipelines
|   |   |- fwi_pipeline.py
|   |   |- readme_doc_pipeline.py
|   |   |- sampling_pipeline.py
|   |   |- sentinel2_fetch_pipeline.py
|   |   |- tabular_load_pipeline.py
|   |   |- ukgrid_pipeline.py
|   |   |- viirs_pipeline.py
|   |- reporting
|   |   |- data_profiler.py
|   |   |- sampling_reporter.py
|   |- sampling
|   |   |- sampling_functions.py
|   |- scripts
|   |   |- __init__.py
|   |   |- s00_set_parameters.py
|   |   |- s01_run_tabular.py
|   |   |- s02_run_sentinel2_fetch.py
|   |   |- s03.1_run_resnet18_finetune.py
|   |   |- s03.2_run_feature_extractor.py
|   |- transforms
|   |   |- fwi_transforms.py
|   |   |- preprocessing_transforms.py
|   |   |- sentinel2_transforms.py
|   |   |- viirs_transforms.py
|   |- utils
|   |   |- __init__.py
|   |   |- datasets_utils.py
|   |   |- file_utils.py
|   |   |- readme_builder.py
|   |   |- validation_checks.py
```

#### Notes:
##### .../Pipelines/
This folder contains a `.py` for each of the pipelines. The files might contain only one function, and be quite shallow. However, this was a conscious design choice to allow easy testing and debugging of pipeline processes, as it is easier to read than having large scripts with many orchestrators. 

#### Scripts
This folder contains the modules that performs specific steps in the program.

These are split into separate, independent components as they are expected to run in isolation. Each file is prefixed with `sXX` where `X` are digits; this stands for `S`cript 00, 01, etc, which indicates the order in which the files are expected to run. 

The outputs of these files are saved to disk, this means that s03 can be executed at any point as long as s02 had already run and saved its outputs. This allows for better debugging and continuity of the project, as some processed are extremly lenghty and computational expensive.

The file structure is shown below, but an in text explanation is also provided for clarity. 

`validation_checks.py` = Contains functions used to check and validate expected rules for when the program is being executed.

```
MScProjectWildFirePredict/
|- src/
|   |- scripts/
|   |   |- __init__.py
|   |   |- s00_set_parameters.py
|   |   |- s01_run_tabular.py
|   |   |- s02_run_sentinel2_fetch.py
|   |   |- s03.1_run_resnet18_finetune.py
|   |   |- s03.2_run_feature_extractor.py
```

#### `scripts/s00_set_parameters.py` 
 
- Define all the values for the variables to be used by all scripts in the program. This includes years to process, file names, etc. This module is called by all modules below.

*Note:*

*`s00_set_parameters.py` has a date field which needs to be updated with the date of run. A safeguard is implemented to ensure parameters are reviewed before execution. 
If the configuration date does not match the current run date, a warning is raised.*

---

#### `scripts/s01_run_tabular.py`

- Imports parameters from `set_parameters.py`.
- Loads and preprocesses the VIIRS, FWI and UK Grid datasets.
- Performs the sampling procedure to generate fire and non-fire observations.
- Creates the predictor (X) and target (Y) tabular dataset (excluding Sentinel-2 features).
- Generates sampling reports and descriptive statistics.
- Splits the sampled dataset by year and saves .csv files to disk for later processing.
---

#### `scripts/s02_run_setinel2_fetch.py`

- Imports parameters from `set_parameters.py`.
- Uses `YEAR_FILTER` to identify which sampled datasets to process.
    - If any of the requested years do not have a corresponding dataset, the function stops, and notifies the user of what is missing and what needs to be run.
- Takes the list of loaded files, and combines them into a single dataframe.
- Split the data into batches suitable for GEE requests (see `sampled_to_batch`, `sampled_to_batch_df`).
- For each row of the sampled batch df, a request is sent to GEE for Sentinel2 data. 
- Saves downlaoded data as `npz` files to disk for later use.
---

#### `scripts/s03.1_run_resnet18_finetune.py`

- Imports parameters from `set_parameters.py`.
- Loads all Sentinel2 `.npz` files available in disk (assumes that s01 and s02 processes are complete).
- Loads data containing `composite_keys` for which no Sentinel2 data was found. 
- Loads sampled (pre sentinel2) dataset.
- Splits the sampled dataset into train, validate and test sets. The composite keys of each set are saved to disk to use the same split across the project.
- Uses train and validate to FineTune layer 4 of the ResNet-18 CNN.
- Saves updated weights to disk
---

#### `scripts/s03.2_run_feature_extraction.py`

- Loads all Sentinel2 `.npz` files available in disk (assumes that s01, s02 and s03.1 processes are complete).
- ResNet18 is used as Feature Extractor - each `.npz` file is loaded, and the image data is processed with the `ResNetFeatExtractor` class.
- Using class `ResNetFeatExtractor`, the user can selects to perform feature extraction using default (no need to pass parameter value) of pre trained (user passes location of pre trained weights on disk as input argument) weights. 
- Transformation and composite keys are validated and checked with a set of validation functions.
- Final data set is cleaned and merged with the sampled data by `composite_key` (not to be confused with `composite_key_y` which is the composite key of the expected/predicted value - composite key of these observations is kept for traceability).
- Complete ML (machine learning) dataset is saved to disk so next process can simply read this file rather than repeat the processing steps.
---

#### `s01MachineLearningModel.ipynb`

- Last module to run (assumes that s01, s02, s03.1, s03.2 processes are complete)
- Loads ML Inputs generated by previous step
- Runs descriptive statistics analysis, machine learning traning, fine tuning and testing and produces the outputs for the report
- Further details of the module can be found on the notebook


### Data Files
This module contains files and objects used to build the different components of the program. It is further split by type of data, i.e., raw inputs, preprocessed, etc. 

```
MScProjectWildFirePredict/
|- data/
|   |- FWI
|   |   |- Archive
|   |- MLInputs
|   |- MLModels
|   |- SampledFireNoFire
|   |- Sentinel2
|   |   |- Archive
|   |- UKGrid
|   |- VIIRS
```
**Raw inputs:**
- FWI = `.grib` files for each year.
- UKGrid = `.shp` files to split UK into grids.
- VIIRS = `.csv` files fire labels for each year.

**PrebProcessed:**
- Sentinel2 = `.npz` downloaded from sampled dataset.
- SampledFireNoFire = `.csv` of sampled data, per year.

**ML Inputs:**
- MLInputs = `.csv` files with sampled data containing all relevant data to train the model.

**ML Models**
- Contains both `.joblib` and `pt` files
- `pt` are the fine tuned weights from layer 4 of ResNet 18
- `joblib` are the classifier models that are trained. These are saved to disk to allow reruning of the project without the need to re train the classifiers
