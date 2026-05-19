
# MScProjectWildFirePredict Architecture

The project is divided into modules, which have specific responsibilities. An overview of the modules is shown here, and below, each of the sections is expanded with further details

## Overview
```
| MScProjectWildFirePredict/
|   |- data
|   |   |- FWI
|   |   |   |- Archive
|   |   |- SampledFireNoFire
|   |   |- Sentinel2
|   |   |   |- Archive
|   |   |- UKGrid
|   |   |- VIIRS
|   |- outputs
|   |   |- 202602270531_RUNNING_DEMO_ON
|   |   |- 202603151653_RUNNING_DEMO_ON
|   |   |- 202603151657_RUNNING_DEMO_ON
|   |   |- 202603151759_RUNNING_DEMO_ON
|   |   |- 202603160600_RUNNING_DEMO_ON
|   |   |- 202603162046_RUNNING_DEMO_ON
|   |   |- 202603162058_RUNNING_DEMO_ON
|   |   |- 202603162100_RUNNING_DEMO_ON
|   |   |- 202603162104_RUNNING_DEMO_ON
|   |   |- 202603172038_RUNNING_DEMO_ON
|   |   |- 202603180608_RUNNING_DEMO_ON
|   |   |- maps
|   |- src
|   |   |- data_io
|   |   |- pipelines
|   |   |- reporting
|   |   |- scripts
|   |   |- transforms
|   |   |- utils
|   |- tests
```

## Codebase
```
MScProjectWildFirePredict/
|- src/
|   |- __init__.py
|   |- data_io
|   |   |- fwi_loader.py
|   |   |- ukgrid_loader.py
|   |   |- viirs_loader.py
|   |- load_data.py
|   |- pipelines
|   |   |- architecture_doc_pipeline.py
|   |   |- fwi_pipeline.py
|   |   |- tabular_load_pipeline.py
|   |   |- ukgrid_pipeline.py
|   |   |- viirs_pipeline.py
|   |- pp_sentinel.py
|   |- preprocessing_general.py
|   |- reporting
|   |   |- data_profiler.py
|   |- scripts
|   |   |- __init__.py
|   |   |- run_tabular.py
|   |   |- set_parameters.py
|   |   |- validation_checks.py
|   |- transforms
|   |   |- fwi_transforms.py
|   |   |- preprocessing_transforms.py
|   |   |- viirs_transforms.py
|   |- utils
|   |   |- __init__.py
|   |   |- architecture_builder.py
|   |   |- datasets_utils.py
|   |   |- file_utils.py
|   |- utils.py
```

### Notes:
#### .../Pipelines/
This folder contains a `.py` for each of the pipelines. The files might contain only one function, and be quite shallow. However, this was a conscious design choice to allow easy testing and debugging of pipeline processes, as it is easier to read than having large scripts with many orchestrators. 

### Scripts
This folder contains the modules that performs specific steps in the program.
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

```
MScProjectWildFirePredict/
|- src/
|   |- scripts/
|   |   |- __init__.py
|   |   |- run_tabular.py
|   |   |- set_parameters.py
|   |   |- validation_checks.py
```

## Data Files
This module contains files and objects used to build the different components of the program. It is further split by type of data, i.e., raw inputs, preprocessed, etc. 

```
MScProjectWildFirePredict/
|- data/
|   |- FWI
|   |   |- 2017FWI.grib
|   |   |- 2018FWI.csv
|   |   |- 2018FWI.grib
|   |   |- 2019FWI.csv
|   |   |- 2019FWI.grib
|   |   |- Archive
|   |   |   |- 2018FWI.csv
|   |   |   |- 2019FWI.csv
|   |   |   |- 2019FWI.grib
|   |- SampledFireNoFire
|   |   |- 2018_sampled_firenofire.csv
|   |   |- 2019_sampled_firenofire.csv
|   |- Sentinel2
|   |   |- 2018_B001_20180101_20180311_sentinel_batch.npz
|   |   |- 2018_B002_20180312_20180413_sentinel_batch.npz
|   |   |- 2018_B003_20180414_20180505_sentinel_batch.npz
|   |   |- 2018_B004_20180506_20180528_sentinel_batch.npz
|   |   |- 2018_B005_20180529_20180616_sentinel_batch.npz
|   |   |- 2018_B006_20180617_20180701_sentinel_batch.npz
|   |   |- 2018_B007_20180702_20180715_sentinel_batch.npz
|   |   |- 2018_B008_20180716_20180731_sentinel_batch.npz
|   |   |- 2018_B009_20180801_20180823_sentinel_batch.npz
|   |   |- 2018_B010_20180824_20180919_sentinel_batch.npz
|   |   |- 2018_B011_20180920_20181014_sentinel_batch.npz
|   |   |- 2018_B012_20181015_20181123_sentinel_batch.npz
|   |   |- 2018_B013_20181124_20181231_sentinel_batch.npz
|   |   |- Archive
|   |- UKGrid
|   |   |- ukcp18-uk-land-12km.dbf
|   |   |- ukcp18-uk-land-12km.prj
|   |   |- ukcp18-uk-land-12km.shp
|   |   |- ukcp18-uk-land-12km.shx
|   |- VIIRS
|   |   |- viirs-jpss1_2018_United_Kingdom.csv
|   |   |- viirs-jpss1_2019_United_Kingdom.csv
|   |   |- viirs-jpss1_2020_United_Kingdom.csv
|   |   |- viirs-jpss1_2021_United_Kingdom.csv
|   |   |- viirs-jpss1_2022_United_Kingdom.csv
|   |   |- viirs-jpss1_2023_United_Kingdom.csv
|   |   |- viirs-jpss1_2024_United_Kingdom.csv
|   |   |- viirs-snpp_2018_United_Kingdom.csv
|   |   |- viirs-snpp_2019_United_Kingdom.csv
|   |   |- viirs-snpp_2020_United_Kingdom.csv
|   |   |- viirs-snpp_2021_United_Kingdom.csv
|   |   |- viirs-snpp_2022_United_Kingdom.csv
|   |   |- viirs-snpp_2023_United_Kingdom.csv
|   |   |- viirs-snpp_2024_United_Kingdom.csv
```
**Raw inputs:**
- FWI = `.grib` files for each year
- UKGrid = `.shp` files to split UK into grids
- VIIRS = `.csv` files fire labels for each year

**PreProcessed:**
- Sentinel2 = `.npz` downloaded from sampled dataset
- SampledFireNoFire = `.csv` of sampled data, per year

**ML Model Input:**
