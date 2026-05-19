"""
Module containing functions to manage and control the run process
"""
from datetime import date
from pathlib import Path
import utils.file_utils as u

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
    
