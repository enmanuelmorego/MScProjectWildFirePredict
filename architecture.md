# MScProjectWildFirePredict Architecture

## Data Files
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
## Code Base
```
|
|- src
|   | - data/
|       |- viirs/
|       |   |- loader.py
|       |   |- preprocessing.py
|       |   |- pipeline.py
|       |  
|       |- fwi/
|       |   |- loader.py
|       |   |- preprocessing.py
|       |   |- pipeline.py
|       |
|       |- ukgrid/
|       |   |- loader.py
|       |   |- preprocessing.py
|       |   |- pipeline.py
|       |   
|       |- sentinel2/
|       |   |- loader.py
|       |   |- preprocessing.py
|       |   |- pipeline.py
|   |- ml_model/
|   |   |- feature_extraction.py
|   |   |- create_ml_dataset.py
|   |   |- random_forest.py

```