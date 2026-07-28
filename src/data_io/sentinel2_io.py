from pathlib import Path
from typing import Any

from tqdm import tqdm
from ml_models.resnet_feature_extractor import SentinelData

import transforms.sentinel2_transforms as st
import utils.file_utils as fu
import utils.datasets_utils as du
import utils.validation_checks as vc
import pandas as pd
import numpy as np
from tqdm import tqdm

import ee
import requests
import tifffile
import io



def fetch_sentinel_data(geom: ee.Geometry, date_str: str, satelite_params: dict ) -> np.ndarray: 
    """Fetches raw pixels from Google Earth Engine (GEE) into RAM.

    Retrieves an ImageCollection filtered by location and a 6-day window (target date and -5 days to target).
    It computes a median composite to mitigate the impact of cloud cover and other noise before downloading as GeoTIFF

    Args:
        geom (ee.Geometry): The GEE geometry object defining the clip area
        date_str (str): The target date (YYYY-MM-DD) for the satellite observation
        satelite_params (dict): Dictionary containingthe various parameters specifying the specific values for fetching the correct satelite images

    Returns:
        np.ndarray: A array of numbers representing the images' pixels


    Raises:
        requests.exceptions.RequestException: If the GEE download URL fails to resolve
        tifffile.TiffFileError: If the downloaded bytes cannot be parsed as a TIFF
    """

    # Extract satelite objects
    satelite_img    = satelite_params['SATELLITE_IMAGES']
    satelite_bands  = satelite_params['SATELLITE_BANDS']
    satelite_scale  = satelite_params['SATELLITE_SCALE']
    satelite_format = satelite_params['SATELLITE_FORMAT']
    crs             = satelite_params['CRS']

    # Get satelite img object
    img      = (ee.ImageCollection(satelite_img)
                .filterBounds(geom)
                .filterDate(ee.Date(date_str).advance(-5, 'day'),
                            ee.Date(date_str).advance( 1, 'day'))
                            .select(satelite_bands)
                            .median()
                            .clip(geom)) 
    url      = img.getDownloadURL({'scale' : satelite_scale,
                                   'crs'   : crs.replace(" ",""),
                                   'region': geom,
                                   'format': satelite_format})
    response = requests.get(url, timeout = 30)
    response.raise_for_status()

    with io.BytesIO(response.content) as f:
        raw_data = tifffile.imread(f)
        return raw_data

def fetch_sentinel_data_observation(row: Any, batch_name: str, run_timestamp: str, parameters: dict) -> dict:
    """Fetch sentinel2 wrapper function that takes a row of data from `sampled_df` and calls the relevant funcitons
    to make the GEE request.
    It returns a dictionary when the request is succesful (no error and not empty)
    When emtpy, the dictionary records the relevant data points and returns False as success
    If an error occurs, this is caught by Try, Except block and a dictionary is generated in the Except block to record issue(s)

    Args:
        row (Any): Row from `itertuples()` fetched from `sampled_df`
        batch_name (str): Name of current working batch
        run_timestamp (str): Timestamp label for current run
        parameters (dict): Dictionary containing program's parameters. Fetched from `set_parameters.py` script

    Returns:
        _type_: Dictionary with relevant details of fetch process

    Example:
        On success:
            `{"success": False, "date": run_timestamp,"batch": batch_name,"composite_key": composite_key,"missing_sentinel2_data": True,"error_msg": None}`

        On emtpy return
            `{"success": True,"image": sentinel_data,"fire_lbl": fire_lbl,"composite_key": composite_key}`

        On failure
            `{"success": False,"date": run_timestamp,"batch": batch_name,"composite_key": composite_key,"missing_sentinel2_data": True,"error_msg": str(e)}`
    """
    idx           = row.Index
    date          = row.date
    fire_lbl      = row.fire_lbl
    composite_key = row.composite_key

    
    if idx % 10 == 0:
        print(f" 📡 🌐 💾      ", end = "\r", flush = True)
    else:
        print(f" . . .      ", end = "\r", flush = True)


    try:
        geom = ee.Geometry(row.geometry.__geo_interface__) 
        sentinel_data = fetch_sentinel_data(geom, date, parameters) 
        sentinel_data = st.transform_sentinel_data(sentinel_data)
        if sentinel_data.size == 0:
            return {"success": False,
                    "date": run_timestamp,
                    "batch": batch_name,
                    "composite_key": composite_key,
                    "missing_sentinel2_data": True,
                    "error_msg": None}
        # When sentinel_data/size is > 0
        return {"success": True,
                "image": sentinel_data,
                "fire_lbl": fire_lbl,
                "composite_key": composite_key}
    except Exception as e:
        return {"success": False,
                "date": run_timestamp,
                "batch": batch_name,
                "composite_key": composite_key,
                "missing_sentinel2_data": True,
                "error_msg": str(e)}

def load_missing_sentinel2_from_log(base_dir: Path, data_dir: str) -> pd.DataFrame: 
    """Loads the Sentinel-2 Missing Download log as data frame

    Args:
        base_dir (Path): Directory of project
        data_dir (str): Directory of location of setinel2 download log

    Returns:
        pd.DataFrame: Latest/most recent sentinel2 download log containing any missing composite keys (ie composite keys for which sentinel-2 data was not found)
    """    
    files = fu.get_filepaths(base_dir, data_dir, 'csv') 
    file  = du.get_latest_missing_sentinel_log_filepath(files)
    df_missing_sentinel2 = pd.read_csv(file, dtype={"composite_key": "string"})
    vc.validate_composite_keys_structure(df_missing_sentinel2)
    return df_missing_sentinel2

def load_sentinel2_as_arrays(sentinel_files: list[Path],n_load: int|None = None) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Loads all available Sentinel2 `npz` in `sentinel_files` and combines the data into `np` arrays

    Args:
        sentinel_files (list[Path]): List of filepaths to the Sentinel2 `.npz` files
        n_load (int | None, optional): Number of files to load - allows user to load smaller subsets for testing. Defaults to None.

    Returns:
        tuple[np.ndarray, np.ndarray, np.ndarray]: A tuple containing the combined Sentinel2 data as numpy arrays where:
         - `all_x` is the image data 
         - `all_y` is the fire labels 
         - `all_composite_keys` is the composite keys of the observations (extracted from `composite_key`)
         - `all_dates` is the dates of the observations (extracted from `composite_key`)
    """
    # Limit number of files to load if n_load is specified (this is mainly used for testing purposes)
    if n_load is not None:
        sentinel_files = sentinel_files[:n_load]
    # Initialise emtpy lists to store the data
    all_x              = []
    all_y              = []
    all_composite_keys = []
    all_dates          = []

    for file in tqdm(sentinel_files, desc="Loading Sentinel2 data from disk", dynamic_ncols = True, position = 0):
        # Load Sentinel2 data from file
        data = SentinelData(file)
        # Extract date from composite key
        data.get_dates()
        # Append data to lists
        all_x.append(data.x)
        all_y.append(data.y)
        all_composite_keys.append(data.keys)
        all_dates.append(data.dates)
    
    # Concatenate all observations into single arrays
    all_x              = np.concatenate(all_x, axis = 0)
    all_y              = np.concatenate(all_y, axis = 0)
    all_composite_keys = np.concatenate(all_composite_keys, axis = 0)
    all_dates     = np.concatenate(all_dates, axis = 0)

    return all_x, all_y, all_composite_keys, all_dates


def save_sentinel_nps(image_list: list, label_list: list, composite_key_list: list, batch_name: str, data_dir: Path) -> None:
    """Saves Sentinel2 data to disk as compressed `.npz` file
    
    The functions converts the downloaded image, label and composite key into numpy arrays and stores them in a single compressed file
    The resulting file contains three arrays:

    - `x`: Sentinel-2 image data
    - `y`: Labels associated with each image
    - `composite_key`: Composite keys corresponding to each observation
    Args:
        image_list (list): List containing the Sentinel-2 image arrays
        label_list (list): List containing the target labels associated with each image
        composite_key_list (list): List containing the composite keys corresponding to each observation
        batch_name (str): Name of the current batch. This value is used to generate the output filename
        data_dir (Path): Root data directory where the `Sentinel2` subdirectory is located

    Raises:
        ValueError: If the image list is emtpy, return value error to avoid falsely commiting empty files to disk
    """
    # VALIDATE
    if len(image_list) == 0:
        raise ValueError(f"❌ No observations found for batch {batch_name}")
    # SAVE DATA
    x     = np.array(image_list)
    y     = np.array(label_list)
    ids   = np.array(composite_key_list)
    fname = f"{batch_name}.npz"
    fout  = data_dir/'Sentinel2'/fname
    np.savez_compressed(fout, x=x, y=y, composite_key=ids)
    print(f"\n\t 🎉 Success! Saved {fname} ({x.nbytes / 1e6:.2f}")