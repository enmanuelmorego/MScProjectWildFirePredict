
# MScProjectWildFirePredict Architecture

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
|   |   |- MLInputs
|   |   |- MLModels
|   |   |- SampledFireNoFire
|   |   |- Sentinel2
|   |- outputs
|   |   |- logs
|   |- src
|   |   |- data_io
|   |   |- ml_models
|   |   |- pipelines
|   |   |- reporting
|   |   |- sampling
|   |   |- scripts
|   |   |- transforms
|   |   |- utils
|   |- tests
```

### Codebase
```
MScProjectWildFirePredict/
|- src/
|   |- __init__.py
|   |- data_io
|   |   |- fwi_loader.py
|   |   |- sampled_loader.py
|   |   |- sampling_writter.py
|   |   |- sentinel2_io.py
|   |   |- ukgrid_loader.py
|   |   |- viirs_loader.py
|   |- ml_models
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
|   |   |- s03_run_feature_extractor.py
|   |- transforms
|   |   |- fwi_transforms.py
|   |   |- preprocessing_transforms.py
|   |   |- resnet_feature_extractor.py
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

`s00_set_parameters.py` = Define all the values for the variables to be used by all scripts in the program. This includes years to process, file names, etc. This module is called by all modules below.

*Note:*

*`s00_set_parameters.py` has a date field which needs to be updated with the date of run. A safeguard is implemented to ensure parameters are reviewed before execution. 
If the configuration date does not match the current run date, a warning is raised.*

`s01_run_tabular.py` = Loads and processes all tabular data in the project. It also performs preprocessing steps and sampling. The output are `.csv` files with the preprocessed and sampled data.

`s02_run_sentinel2_fetch.py` = Loads the `.csv` preprocessed and sampled data and fetches the Sentinel-2 data from GEE. Stores Sentinel2-2 data as `.npz` files to local disk.

`s03_run_feature_extraction.py` = Loads the `.npz` files and uses a CNN architecture to extract the features to be used in the analysis. This module also loads the sampled `.csv` files and joins them. It saves `.csv` per year containing all data ready for modelling. 

`run_train_ml_model.py` = Trains the model.

```
MScProjectWildFirePredict/
|- src/
|   |- scripts/
|   |   |- __init__.py
|   |   |- s00_set_parameters.py
|   |   |- s01_run_tabular.py
|   |   |- s02_run_sentinel2_fetch.py
|   |   |- s03_run_feature_extractor.py
```
#### `s01_run_tabular.py`

- Imports parameters from set_parameters.py.
- Loads and preprocesses the VIIRS, FWI and UK Grid datasets.
- Performs the sampling procedure to generate fire and non-fire observations.
- Creates the predictor (X) and target (Y) tabular dataset (excluding Sentinel-2 features).
- Generates sampling reports and descriptive statistics.
- Splits the sampled dataset by year and saves .csv files to disk for later processing.
---

#### `s02_run_setinel2_fetch.py`

- Imports parameters from `set_parameters.py`.
- Uses `YEAR_FILTER` to identify which sampled datasets to process.
    - If any of the requested years do not have a corresponding dataset, the function stops, and notifies the user of what is missing and what needs to be run.
- Takes the list of loaded files, and combines them into a single dataframe.
- Split the data into batches suitable for GEE requests (see `sampled_to_batch`, `sampled_to_batch_df`).
- For each row of the sampled batch df, a request is sent to GEE for Sentinel2 data. 
- Saves downlaoded data as `npz` files to disk for later use.
---

#### `s03_run_feature_extractor.py`

- Imports parameters from `set_parameters.py`.
- Loads all Sentinel2 `.npz` files available in disk (assumes that s01 and s02 processes are complete).
- Loads data containing `composite_keys` for which no Sentinel2 data was found. 
- Loads sampled (pre sentinel2) dataset.
- ResNet18 is used as Feature Extractor - each `.npz` file is loaded, and the image data is processed with the `ResNetFeatExtractor` class.
- Transformation and composite keys are validated and checked with a set of validation functions.
- Final data set is cleaned and merged with the sampled data by `composite_key` (not to be confused with `composite_key_y` which is the composite key of the expected/predicted value - composite key of these observations is kept for traceability).
- Complete ML (machine learning) dataset is saved to disk so next process can simply read this file rather than repeat the processing steps.
---

### Data Files
This module contains files and objects used to build the different components of the program. It is further split by type of data, i.e., raw inputs, preprocessed, etc. 

```
MScProjectWildFirePredict/
|- data/
|   |- MLInputs
|   |- MLModels
|   |- SampledFireNoFire
|   |- Sentinel2
```
**Raw inputs:**
- FWI = `.grib` files for each year.
- UKGrid = `.shp` files to split UK into grids.
- VIIRS = `.csv` files fire labels for each year.

**PreProcessed:**
- Sentinel2 = `.npz` downloaded from sampled dataset.
- SampledFireNoFire = `.csv` of sampled data, per year.

**ML Model Input:**
- MLInputs = `.csv` files with sampled data containing all relevant data to train the model.
