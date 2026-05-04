"""
Module containing functions to manage and control the run process
"""
from datetime import date
def validate_params_update(validation_date: date):
    """Function to validate and check user have updated parameters before running pipeline

    Args:
        validation_date (date): Validation date object from set_parameters.py file

    Raises:
        ValueError: Stop function if the date does not match today
    """
    # Get today's date
    today = date.today()
    if today != validation_date:
        raise ValueError("❌ Please update object VALIDATION_DATE in location:/nsrc/scripts/set_parameters.py")
 