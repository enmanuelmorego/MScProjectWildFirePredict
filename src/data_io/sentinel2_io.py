from pathlib import Path
import os
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
    """
    x     = np.array(image_list)
    y     = np.array(label_list)
    ids   = np.array(composite_key_list)
    fname = f"{batch_name}.npz"
    fout  = data_dir/'Sentinel2'/fname
    np.savez_compressed(fout, x=x, y=y, composite_key=ids)
    print(f"\n\t 🎉 Success! Saved {fname} ({x.nbytes / 1e6:.2f}")