"""
Module containing functions to manage and control the run process
"""
from datetime import date
from pathlib import Path
from datetime import datetime 
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
    
def validate_resnet_feature_extractor(df_features: pd.DataFrame) -> None:
    """Checks whether there are duplicated composite keys in the dataframe from the feature extraction process
    If duplicated composite keys do exists, ensure that all features are the same (real duplicates)

    Args:
        df_features (pd.DataFrame): Data frame from feature extraction process

    Raises:
        ValueError: When the same composite key has multiple feature values within the same composite key
    """
    # Find duplicated composite keys
    df_duplicated_keys  = df_features.groupby("composite_key").filter(lambda x: len(x) > 1)
    int_duplicated_rows = df_duplicated_keys.shape[0]
    duplicated_keys     = df_duplicated_keys['composite_key'].unique()
    int_duplicated_keys = duplicated_keys.shape[0]

    if df_duplicated_keys.empty:
        return
    
    if int_duplicated_keys > 0:
        print(f"⚠️  Total [{int_duplicated_keys}] duplicated composite keys ({int_duplicated_rows} rows)")

    # Check that all of the duplicated composite_keys contain the same features (real duplicated)
    df_to_check = df_features[df_features['composite_key'].isin(duplicated_keys)]

    # Check for real duplicates - Expect that all duplicated composite keys also appear as duplicated when considering all the columns
    # If there are less rows in df_checked vs duplicated composite_keys means that the same composite key has different feature values in the rows 
    df_checked       = df_to_check[df_to_check.duplicated(keep = False)]
    int_cheched_rows = df_checked.shape[0] 

    if int_cheched_rows != int_duplicated_rows:
        non_real_duplicated = set(df_duplicated_keys['composite_key']) - set(df_checked['composite_key'])
        raise ValueError(f"\n❌  ERROR  \nFound [{df_duplicated_keys.shape[0] - df_checked.shape[0]}] duplicated composite keys WITH DIFFERENT FEATURE VALUES...\n"
                         f"Inspect values {non_real_duplicated}")


def validate_composite_keys(df_features: pd.DataFrame, 
                            df_sampled: pd.DataFrame, 
                            df_missing_sentinel: pd.DataFrame,
                            primary_key: str = 'composite_key') -> None:
    """Takes two dataframes as inputs (df containing features from ResNet18 and sampled data) and compares their
    composite keys to ensure that no data was missed in the processing of features

    Args:
        df_features (pd.DataFrame): Dataframe resulting from feature extraction process - ResNet18 
        df_sampled (pd.DataFrame): Dataframe containing sampled, preprocessed data
        df_missing_sentinel (pd.DataFrame): Dataframe (from outputs/log) containing the composite keys that were not able to be downloaded
        primary_key (str, optional): Name of the column containing the values to compare. Defaults to 'composite_key'
    """    

    # Extract values that were not able to be downloaded
    set_missed_download = set(df_missing_sentinel[primary_key])
    df_cleaned_sampled  = df_sampled[~df_sampled[primary_key].isin(set_missed_download)]

    # Extract primary key values
    keys_features = set(df_features[primary_key].astype(str))
    keys_sampled  = set(df_cleaned_sampled[primary_key].astype(str))

    # Find values in features not in sampled
    missing_keys = keys_sampled  - keys_features
    extra_keys   = keys_features - keys_sampled 

    if len(missing_keys):
        print(f"⚠️  {len(missing_keys)} composite keys in [sampled] not in [extracted features]\n{missing_keys}")
    if len(extra_keys):
        print(f"⚠️  {len(extra_keys)} composite keys in [extracted features] not in [sampled]\n{extra_keys}")

def valid_composite_key(comp_key: str) -> bool:
    """Validates that composite keys are generated correctly
    It transforms the input into string format, and validates:
    - Lenght of string (expect at least 9 characters, as its date (8) + grid_id)
    - Splits string into date component and grid id component
    - Validates that the grid_id component is only digits
    - Validates that the date component is a valid date

    Args:
        comp_key (str): String/Value Composite key to test

    Returns:
        bool: True when the input is a valid composite key
    """

    # Ensure that the input key is a string
    key_str = str(comp_key)

    # Test string length - expect 8 (date) + 1 (smallest grid_id)
    if len(key_str) < 9:
        return False
    
    # Extract grid_id and date components
    date_id_str = key_str[-8:]
    grid_id_str = key_str[:-8]

    # Ensure that grid_id component is a digit
    if not grid_id_str.isdigit():
        return False
    
    # Ensure date component is actually a date 
    try:
        datetime.strptime(date_id_str, "%Y%m%d")
    except ValueError:
        return False
    return True

def validate_composite_keys_structure(df_in: pd.DataFrame, col: str = "composite_key") -> None:

    invalid_keys = {ck for ck in df_in[col] if not valid_composite_key(ck)}
    
    total_invalid_leys = len(invalid_keys)
    if total_invalid_leys > 0:
        raise ValueError(f"\n❌  ERROR  \nFound {total_invalid_leys} invalid composite keys.\n"
                         f"Examples: {invalid_keys}")


if __name__ == "__main__":
    df_feat = pd.DataFrame({'composite_key': ['00120200501', '512202050101','512202050101','512202050231', '512202050101'],#['001','001','005', '002','003'],
                            'feat_01': [0,11,1,3 ,2],
                            'feat_02': [0,11,1,8,110]})
    df_sampled = pd.DataFrame({'composite_key': ['00120200501','512202050101','00120260231', 
                                                 '512202050231','003'],
                            'feat_01': [0,11,1,3 ,2],
                            'feat_02': [0,11,1,8,110]})
    df_missed = pd.DataFrame({'composite_key': ['001202601011', '1003', '100120260231'],
                              'some_var': ['a','b','c']})
    print(validate_composite_keys(df_feat, df_sampled, df_missed))