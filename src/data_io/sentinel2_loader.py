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