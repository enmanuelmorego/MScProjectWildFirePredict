"""
Method that contains all the functions to load the UK Grid data
"""
import geopandas as gpd
from pathlib import Path

def load_uk_grid(data_dir: Path, file_name: str, crs: str) -> gpd.GeoDataFrame:
    """  Function to load the shapefile containing the UK grid to use as base

    Args:
        data_dir (Path): Directory of data folder
        file_name (str): Name of the file to load
        crs (str): Coordinate Reference System, ensure all data is consistent across the project

    Returns:
        gpd.GeoDataFrame: UK Grid dataset with the grid allocated
    """  

    grid_path = data_dir/'UKGrid'/file_name
    uk_grid = gpd.read_file(grid_path)
    uk_grid = uk_grid.rename(columns = {'id': 'grid_id'})
    uk_grid = uk_grid.to_crs(crs)
    return uk_grid