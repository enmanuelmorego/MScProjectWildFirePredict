# Functions specific to Google Earth Engine connection and satelite images processing 
import ee
import geopandas as gpd
import pandas as pd

def geodf_to_ee(geo_df: gpd.GeoDataFrame) -> ee.FeatureCollection:
    """
    Convert GeoPandasDataFrame to a GoogleEarth Feature Collection to extract Sentinel-2 images

    Args:
  