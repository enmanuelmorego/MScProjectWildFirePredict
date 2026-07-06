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


def validate_composite_keys(df_features: pd.DataFrame, df_sampled: pd.DataFrame, primary_key: str = 'composite_key'):

    # Extract primary key values
    keys_features = df_features[primary_key]
    keys_sampled = df_sampled[primary_key] 

    # Find values in features not in sampled
    missing_keys = set(keys_sampled)  - set(keys_features)
    extra_keys   = set(keys_features) - set(keys_sampled) 

    if len(missing_keys):
        print(f"⚠️  {len(missing_keys)} composite keys in [sampled] not in [extracted features]")
    if len(extra_keys):
        print(f"⚠️  {len(extra_keys)} composite keys in [extracted features] not in [sampled]")



if __name__ == "__main__":
    df_feat = pd.DataFrame({'composite_key': ['001','001','005', '002','003'],
                            'feat_01': [0,11,1,3 ,2],
                            'feat_02': [0,11,1,8,110]})
    df_sampled = pd.DataFrame({'composite_key': ['001','001','001', '002','003'],
                            'feat_01': [0,11,1,3 ,2],
                            'feat_02': [0,11,1,8,110]})
    validate_composite_keys(df_feat, df_sampled)