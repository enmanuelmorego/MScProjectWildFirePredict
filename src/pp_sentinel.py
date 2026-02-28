import ee
import tensorflow as tf
import numpy as np
import os
from pathlib import Path
import tensorflow as tf
import pandas as pd

def sampled_to_batch(df_sampled: pd.DataFrame, batch_size: int = 800) -> dict:
    """
    Function that takes the sampled data and splits it into batches manageable for `Sentinel` download

    Requisites:
    - DataFrame batches must be <= 800 rows. This is important to avoid RAM crashes, requests errors, among other
    - All batches must contain complete day ranges. All values associated with a given date must be included in the batch
    - The reason for the requirement above is to ensure that start-end filenames can be used to accuratetly fetch the data covering the period mentioned in the filename

    Naming Convention:
        Batches names follow the convention `YYYY_Bnnn_YYYYMMDD_YYYYMMDD_sentinel_batch` where:
         - `YYYY` is the current year
         - `Bn` is Batch number. This is important as if a single day contains more than 800 values, it can still be uniquely stored by simply adding +1 to the nnn value
         - `YYYYMMDD_YYYYMMDD` are the dates from-to that the data currently covers

    Cases:
        - If 2020-01-01 contains 700 observations, and 2020-01-01 contains 200 observations, then batch size will be only 700 and only include the records for 2020-01-01
        - If 2020-01-01 contains 900 observations, then two batches are generated: 
            - `2020_B001_20200101_20200101_sentinel_batch`
            - `2020_B002_20200101_20200101_sentinel_batch`

    Args:
        - df_sampled (df): Data frame containing the sampled data, preprocessed
        - batch_size (int): Set to 800 as max as default. But can be adjusted if needed

    Raises:
        - ValueError: if user passes a `batch_size` > 800

    Returns:
        - dictionary (dict): The date period covered by each batch as key, and the actual data covering the period as value
    """
    df_batches = df_sampled.copy()
    # Generate counts for each date object 
    df_batches = (df_batches.groupby('date')
                  .agg({"date_count": ['count']}))

def fetch_sentinel_data(geom: ee.Geometry, date_str: str) -> np.ndarray: 
    """
    Fetches raw pixels from Google Earth Engine (GEE) into RAM.

    This function does a cloud to RAM rather than to Disk process. It creates a 5-day 
    median composite to mitigate cloud cover and requests a GeoTIFF 
    download URL for a specific 12km grid.

    Args:
        geom_ee (ee.Geometry): The GEE geometry object defining the clip area.
        date_str (str): The target date (YYYY-MM-DD) for the satellite observation.

    Returns:
        numpy.ndarray: A raw 3D array  
        Note: The band order is [B2, B3, B4, B8] (Blue, Green, Red, NIR).

    Raises:
        requests.exceptions.RequestException: If the GEE download URL fails to resolve.
        tifffile.TiffFileError: If the downloaded bytes cannot be parsed as a TIFF.
    """
    pass

def transform_sentinel_data(sentinel_npyarray: np.ndarray):
    """
    Transforms the downloaded raw pixels array into a format that is suitable for CNN processing
    The function replaces all `nan` with `0` values, it organises the order of the bands to `(H, W, 4)`, and resizes the data to 128 x 128

    Args:
        sentinel_npyarray (np.ndarray): Raw 3D pixel array 

    Returns:
        sentinel_npyarray (np.ndarray): resized and transformed numpy array
    """
    pass
