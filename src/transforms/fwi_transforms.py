"""
Module of data transformations for FWI
"""
from pathlib import Path
from datetime import datetime
import pandas as pd
import geopandas as gpd

def transform_grib_to_csv(fwi_path: Path, grib_fname: str, grb_name: str, df_uk_grid, crs_val: str) -> None:
    """
    Function that transform a grib file into a csv file. It takes the .grib file, and iterates thru all its elements/message 
    to extract the corresponding data. 
    Then it joins the data to the UK Grid data frame, retaining the `grid_id` to later match using primary key of
    (`df_grid`, `date`)
    For each 12km x 12km grid, it computes both the Max FWI and Mean FWI to be later used for analysis
    It saves the transformed data as a csv file 

    Args:
        fwi_path (Path): Path of the directory containing all the FWI data
    
        grib_fname (str): String containing the file name to load 

        grb_name (str): name of the object to extract from the grib file

        df_uk_grid (df): Data frame contaning the UK grid coordinates. Not dated

        crs_val (str): CRS value used across the project 

    Returns:
        None
    """
    print("\t➡️ Transforming .grib to .csv...")
    fname_path = Path(fwi_path)/grib_fname
    grbs       = pygrib.open(fname_path) # type: ignore
    fwi_msgs   = grbs.select(name=grb_name)

    # Initialise object to store data
    list_fwi: list[gpd.GeoDataFrame] = []
    total                            = len(fwi_msgs)
    i                                = 1

    # Compute grid centroids
    df_grid_centroids_proj = df_uk_grid.to_crs("EPSG:27700")
    df_grid_centroids_proj["geometry"] = df_grid_centroids_proj.geometry.centroid

    # Process data
    for grb in fwi_msgs:
        print(f"\r\t...⚙️  [{grib_fname}] Processing {i} of {total} [{round((i/total)*100,2)}]%", end="")
        # Extract variables
        date       = datetime.strptime(f"{grb.dataDate}{grb.dataTime:04d}", "%Y%m%d%H%M")
        lats, lons = grb.latlons()
        fwi_values = grb.values
        n          = fwi_values.size
        # Load onto a temp dataframe
        df_grib = pd.DataFrame({'date'     : [date] * n,
                                'longitude': lons.ravel(),
                                'latitude' : lats.ravel(),
                                'fwi'      : fwi_values.ravel()})
        # Transform longitude from [0, 360] range (as in grib files) to [-180, 180] range as in UK grid file
        df_grib["longitude"] = df_grib["longitude"].where(df_grib["longitude"] <= 180,
                                                        df_grib["longitude"] - 360)
        df_geo_grib = gpd.GeoDataFrame(df_grib,
                                    geometry = gpd.points_from_xy(df_grib.longitude,
                                                                    df_grib.latitude),
                                    crs = crs_val)
        
        df_geo_grib_proj = df_geo_grib.to_crs("EPSG:27700")
        # Join FWI to UK Grid to get value per Grid
        df_join = gpd.sjoin_nearest(df_grid_centroids_proj,
                                    df_geo_grib_proj[['geometry','fwi']],
                                    how = 'left')
        df_join['date'] = date

        list_fwi.append(df_join)
        # User Messages objects
        i += 1
    
    df_fwi = pd.concat(list_fwi, ignore_index = True)
    df_fwi["date"] = pd.to_datetime(df_fwi["date"]).dt.normalize()
    # Aggregate to daily grid level and compute mean and max
    df_fwi = (df_fwi
                .groupby(["grid_id", "date"], as_index=False)
                .agg(fwi_max=("fwi", "max"),
                    fwi_mean=("fwi", "mean")))
    fname_out = Path(fwi_path)/grib_fname.replace(".grib", ".csv")
    df_fwi.to_csv(fname_out, index = False)
    print(f"\n\t...✅  Succesfully processed {grib_fname}")