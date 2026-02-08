# Functions specific to Google Earth Engine connection and satelite images processing 
import ee
import geopandas as gpd
import pandas as pd
import os
import load_data as ld
from pathlib import Path

def geodf_to_ee(geo_df: gpd.GeoDataFrame) -> ee.FeatureCollection:
    """
    Convert GeoPandasDataFrame to a GoogleEarth Feature Collection to extract Sentinel-2 images

    Args:
        geo_df (GeoDataFrame): Data frame containing the plygon for the UK Grids, for each date of the date range
                               Expected columns:
                               - 'date' (datetime or date-like)
                               - 'id'   (grid identifier)
                               - 'geometry' (polygon geometry)

    Returns:
        ee.FeatureCollection
           A FeatureCollection where each feature represents a single
            (grid_id, date) combination.
    """
    features = []
    for _, r in geo_df.iterrows():
        date_f  = r["date"].strftime("%Y-%m-%d")
        coords  = [list(r.geometry.exterior.coords)]
        geom    = ee.Geometry.Polygon(coords)
        feature = ee.Feature(geom,
                             {'date'       : date_f,
                              'grid_id'    : r['grid_id'],
                              'sentinel_id': None,
                              'cloud_pct'  : None})
        features.append(feature)
    return ee.FeatureCollection(features)

def attach_s2_metadata(feature: ee.Feature, s2: ee.imagecollection) -> ee.Feature:
    """
    Takes the Feature of a Feature Collection object constructed from the UK Grid data, and returns
    the metadata for the matching images in Sentinel-2 (sentinel-2 is a global ee variable, defined outside this function)
    - Read FC date
    - Read FC Geometry
    - Find matching images in Sentinel-2
        - Date + 1 day window
        - Overlaps with geometry (Defined UK Grids)
    - Choose one image (least cloudy, better quality, more information)
    - Attach metadata to feature

    Args:
        feature (ee.Feature):
            A single Earth Engine Feature representing one UK grid cell
            for one specific date

        s2 (ee.ImageCollection):
            Sentinel-2 image collection (e.g. COPERNICUS/S2_SR_HARMONIZED)

    Returns:
        ee.Feature:
            The input feature with additional properties:
              - 'sentinel_id' : Sentinel-2 image system ID (if found)
              - 'cloud_pct'   : CLOUDY_PIXEL_PERCENTAGE (if found)
              - 'has_image'   : 1 if an image was found, else 0
    """
    # Extract date
    date = ee.Date(feature.get("date"))
    # Extract Geometry
    geom = feature.geometry()
    # Filter Sentinel Class by date and Geometry (location)
    s2_day = (s2
              .filterDate(date, date.advance(1,"day"))
              .filterBounds(geom)
              .sort("CLOUDY_PIXEL_PERCENTAGE"))
    # Choose least cloudy image
    img = s2_day.first()
    # Return results
    return feature.set({"sentinel_id": ee.Algorithms.If(img, img.get("system:id"), None),
                        "cloud_pct":   ee.Algorithms.If(img, img.get("CLOUDY_PIXEL_PERCENTAGE"), None),
                        "has_image":   ee.Algorithms.If(img,1,0)})

def google_ee_request(batch_dict: dict, sat_img_collection: ee.ImageCollection) -> None:
    """
    Submit Google Earth export tasks for each of the batches in the `batch_dict` input dictionary

    For each set batch
    - The data is transformed to ee.FeatureCollection
    - Sentinel-2 Metadata is attached (and Sentinel-2 identifying id)
    - Feature without images are excluded
    - Results are exported directly to GoogleDrive as a csv file

    Args:
        batch_dict (dict):
            A dictionary containing the batch name, and a data frame for each batch

        sat_img_collection (ee.ImageCollection):
            Sentinel-2 image collection used to retrieve metadata

    Returns:
        None - Function submits EE export request 
    """
    # Iterate thru each batch
    for key in batch_dict:
        df_request = batch_dict.get(key)
        start = (df_request['date'].min()).strftime('%Y%m%d')
        end   = (df_request['date'].max()).strftime('%Y%m%d')
        fname = f"{start}-{end}_sentinel_images_layer1"

        fc_request = geodf_to_ee(df_request)
        fc_s2      = fc_request.map(lambda f: attach_s2_metadata(f, sat_img_collection))
        fc_export  = (fc_s2
                      .filter(ee.Filter.eq("has_image",1))
                      .select(['date','grid_id','sentinel_id','cloud_pct'])
                      .map(lambda f: f.setGeometry(None)))
        
        task = ee.batch.Export.table.toDrive(collection  = fc_export,
                                             description = fname,
                                             folder      = "Sentinel2",
                                             fileFormat  = "CSV")
        task.start()

def google_ee_request_runner(satelite: str, df_grid_date: pd.DataFrame, required_days: list) -> None:
    """
    Runs the Google EarthEngine functions to request Sentinel Images from Google EarthEngine
    
    Steps:
    - Authenticates with Google Earth Engine
    - Ensures to retrieve/request only data not currently available in GoogleDrive of the project 
    - If requests are needed, these are split into manageable batches 
    - Submits GoogleEE task request

    Args:
        satelite (str): Earth Engine image collection identifier

        df_grid_date (DataFrame): UK grid expanded by day, containing at least:
                                  - 'date'
                                  - 'id'
                                  - 'geometry'

        required_days (List): Lsit containing all of the daily dates of data required 
            
    """
    # Authenticate connection
    try:
        ee.Initialize(project = "ee-enmanuelmorego")
    except:
        ee.Authenticate()
        ee.Initialize(project = "ee-enmanuelmorego")
    # Get image collection     
    sat_img_col = ee.ImageCollection(satelite)
    # Split the data into manageable batches for Google EE
    data_batch = ld.batch_create_sentinel(df_grid_date, required_days)
    # Iterate thru each batch and request the metadata for each batch
    google_ee_request(data_batch, sat_img_col)
    print(f"\t⚠️ Please note: Currently requesting data from Google EE. Please check GoogleDrive to ensure the requested data is available\n\tGoogle EE request may take hrs/days ")