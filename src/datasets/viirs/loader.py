"""
Method that contains all the functions to load the VIIRS data
"""
from pathlib import Path

def select_viirs_files(files: list[Path], year_load: list[int] | None = None) -> list[Path]:
    """  Function to select the VIIRS files to load from local storage. The list of files is filtered if a year is specified

    Args:
        files (list[Path]): List of strings containing a full file path for each of the files to load
        year_load (list[int] | None, optional): An integer representing a year to load the data - If not provided, the default with load all data. Defaults to None.

    Returns:
        list[Path]: List of paths to be loaded
    """    
    if not year_load:
        return files
    
    files_out = []
    for year in year_load:
        str_search = str(year)
        files_out.extend([f for f in files if str_search in f.name])
    if not files_out:
        print(f"⚠️ WARNING:\nNo files found for years {year_load}")
    return files_out