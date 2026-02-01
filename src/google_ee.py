# Functions specific to Google Earth Engine connection and satelite images processing 
import ee
import geopandas as gpd
import pandas as pd

def geodf_to_ee(geo_df: gpd.GeoDataFrame) -> ee.FeatureCollection:
    """
    Convert GeoPandasDataFrame to a GoogleEarth Feature Collection to extract Sentinel-2 images

    Args:
        geo_df (GeoDataFrame): Data frame containing the plygon for the UK Grids, for each date of the date range

    Returns:
        Feature Collection
    """
    features = []
    for _, r in geo_df.iterrows():
        date_f  = r["date"].strftime("%Y-%m-%d")
        coords  = [list(r.geometry.exterior.coords)]
        geom    = ee.Geometry.Polygon(coords)
        feature = ee.Feature(geom,
                             {'date'       : date_f,
                              'grid_id'    : r['id'],
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


def google_ee_request_runner(sat: str, uk_grid_date: pd.DataFrame, required_days: dict):
    """
    Runs the Google EarthEngine functions to request Sentinel Images from Google EarthEngine
    Runner splits the requests to max of 15 days at the time, given that more days causes a request limit error
    """
    # Authenticate connection
    try:
        ee.Initialize(project = "ee-enmanuelmorego")
    except:
        ee.Authenticate()
        ee.Initialize(project = "ee-enmanuelmorego")
    # Get image collection     
    sat_img_col = ee.ImageCollection(sat)
