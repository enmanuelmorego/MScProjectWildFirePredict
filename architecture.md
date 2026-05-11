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
|   | - data_io/
|       |- viirs_loader.py
|       |- fwi_loader.py
|       |- ukgrid_loader.py
|       |- sentinel2_loader.py
|   | - transforms/
|       |- viirs_transforms.py
|       |- fwi_transforms.py
|       |- ukgrid_transforms.py
|       |- sentinel2_transforms.py
|   | - pipelines/
|       |- viirs_pipeline.py
|       |- fwi_pipeline.py
|       |- ukgrid_pipeline.py
|       |- sentinel2_pipeline.py

|       |- preprocessing_transforms.py
            aggregate_viirs_to_grid() <previoysly summarise_viirs>
            extract_inputs_metadata() (from reporting) prev called dfs_metadata
            build_tabular_dataset() prev called combined_dfs [now houses creation of cmposite_id too]
            remove_na_fwi_grid1()

|       |- below are the transformations, not yet modules
            call preprocessing_pipeline() [this can go into pipeline module]
                call summarise_viirs()
                    Appends grid_id
                    groups by grid_id and date
                    assgns label_fire = True
                    [potentially rename as its not summarising viirs?]
                call dfs_metadata()
                    Validates and compares the combined data with inputs to ensure consistency (more of a qa)
                call json_save() 
                    Save data report as json for inspection later and audit trail
                call combined_dfs()
                    combines all datasets into a single one. including fwi, viirs, and daily grids
                call remove_na_fwi_grid1
                    removes grid_id = 1 from the sataset as the FWI is non-existent for this location
                    Rationale
                        - The grid represents <0.1% of all spatial units,
                        - FWI is entirely missing for that grid across all dates,
                        - Imputation would introduce artificial meteorological signal
                Creates composite key (grid_id + date)
                Creates model summary and save as json (total coumns, rows, grids, etc basic descriptives)
                Returns dataset with all data combined

            And then from this id have to develop a sampling pipeline where for each fire obs i take 2 non fire. 
            - 1. find all grids that have never seen a fire (df_grids_no_fire)
            - 2. 1 of the non fire is the same grid as the fire one but 6 months in the apst and had no fire.  The second is an observation form the same day of the fire, but form a grid that has never seen fire. Select the top 10 closests that match the criteria, and randomly select one (we might want to repeat grids here for data availability and also some spots might repeat in terms of fire every year so no need to make unique)

            final dataset is for easch fire sample, 2 non fire samples..
            Take some descriptives from this dataset and save for reference  


|   |- ml_model/
|   |   |- feature_extraction.py
|   |   |- create_ml_dataset.py
|   |   |- random_forest.py
|   |- reporting/
|   |   |- preprocessing_reporting.py
``` 

### Notes:
#### .../Pipelines/
This folder contains a .py for each of the pipelines. The files might contain only one function, and be quite shallow. However, this was a conscious design choice to allow easy testing and debugging of pipeline processes, as it is easier to read than having large scripts with many orchestrators. 

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


## Process
```
Load datasets (`load_viirs_main`, `load_ukgrid_main`, `load_fwi_main`)
Combine into single dataframe
```

# Continue at:
Implement refactoring of pre processing
migrate tests of:
- test_pp_sentinel
- test_pre_processing_general
- test_utils