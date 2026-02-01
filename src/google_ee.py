# Functions specific to Google Earth Engine connection and satelite images processing 
import ee

def load_image_collection(sat: str) -> ee.imagecollection:
    """
    Load an image collection using the specified Satelite parameter in `config.py` file

    Args:
        sat (str): String containing the satelite name
    """
    try:
        ee.Initialize(project = "ee-enmanuelmorego")
    except:
        ee.Authenticate()
        ee.Initialize(project = "ee-enmanuelmorego")
    sat_img_col = ee.ImageCollection(sat)
    return sat_img_col
