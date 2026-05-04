"""
Module to run all the data load, and transformations to prepare all tabular data for transformations
"""

from src.scripts.set_parameters import VALIDATION_DATE
import src.utils.run_control as rc

def run_tabular():
    # Validation rule
    rc.validate_params_update(VALIDATION_DATE)


if __name__ == "__main__":
    # python3 -m src.scripts.run_tabular
    run_tabular()
    
