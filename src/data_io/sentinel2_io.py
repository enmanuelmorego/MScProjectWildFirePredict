from pathlib import Path
from typing import Any
import transforms.sentinel2_transforms as st
import ee
import numpy as np
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
    date          = row.date
    fire_lbl      = row.fire_lbl
    composite_key = row.composite_key
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