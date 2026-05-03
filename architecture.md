# MScProjectWildFirePredict Architecture

## Folder structure
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