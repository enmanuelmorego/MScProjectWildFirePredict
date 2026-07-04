"""
Module containing functions to manage and control the run process
"""
from datetime import date
from pathlib import Path
import utils.file_utils as u
import pandas as pd

def validate_params_update(validation_date: date, params_file: str = "set_parameters.py"):
    """Function to validate and check user have updated parameters before running pipeline

    Args:
        validation_date (date): Validation date object from set_parameters.py file
        params_file (str): Name of the file containing the parameter values

    Raises:
        ValueError: Stop function if the date does not match today
    """
    # Get today's date
    today = date.today()
    if today != validation_date:
        param_file_full = (Path(__file__).parent/params_file)
        u.open_file(param_file_full)
        raise ValueError(f"\n\t❌ Please update object VALIDATION_DATE with today's dates in location:\n\t   src/scripts/{params_file}")
    
def validate_data_load_dict(dict_dfs: dict[int, pd.DataFrame | None]) -> None:
    """Checks the loaded sampled df dicitonary. If any year has missing data, then raise FileNotFoundError and notify user how this can be corrected

    Args:
        dict_dfs (dict[int, pd.DataFrame  |  None]): Dataframe containing loaded data by year

    Raises:
        FileNotFoundError: If any of the years has None instead of dataframe 
    """
    missing_years = [y for y, d in dict_dfs.items() if d is None]

    if len(missing_years) >0:
        raise FileNotFoundError(f"\n❌ Missing csv files for year(s) {missing_years}"
                                "\nPlease add the missing year(s) value(s) to [YEAR_FILTER] list in [src/scripts/set_parameters.py]"
                                "\nand run script [src/scripts/run_tabular.py] to create the missing file(s)")