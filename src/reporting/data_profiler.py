
import pandas as pd

def extract_dataset_metadata(df: pd.DataFrame, df_name: str, include_fire_metrics: bool = False) -> dict:
    """Function that calculates and extracts metadata information from a given data frame. Intended to be used with inputs
    Depending on the input type, the functione extracts different metrics from different columns
    

    Args:
        df (pd.DataFrame): Input data frame to analyse
        df_name (str): Name of the dataframe to be analysed
        include_fire_metrics (bool, optional): Indicates whether fire data is to be analysed. Applicable to preprocessed data, but not applicable to raw inputs. Defaults to False.

    Returns:
        dict: A metadata dictionary containing all relevant information. Final dataframe will vary depending on input (* indicates object in dict may vary)
        {`'dataset_name'        : ...,
          'df_type'             : ...,
          'columns'             : ...,
          'total_rows'          : ...,
          'date_to'*            : ...,
          'date_from'*          : ..., 
          'total_grids'*        : ...,
          'grid_min'*           : ...,
          'grid_max'*           : ...,
          'viirs_true_obs'*     : ...,
          'fire_lbl_proportion'*: ...,
          'unique_viirs_grids'* : ..., 
          'fwi_notna'*          : ...
        }
        `
    """
    # ------------------------
    # REUSED VARIABLES
    # ------------------------
    cols_in_df = df.columns
    # ------------------------
    # GENERAL METADATA
    # ------------------------
    metadata = {'dataset_name': df_name,
                'df_type'     : type(df).__name__,
                'columns'     : list(df.columns),
                'total_rows'  : int(df.shape[0])
                }
    # ------------------------
    # DATES METADATA
    # ------------------------
    if 'date' in cols_in_df:
        metadata['date_from'] = (df['date'].min().strftime("%Y-%m-%d"))
        metadata['date_to']   = (df['date'].max().strftime("%Y-%m-%d"))
    # ------------------------
    # SPATIAL METADATA
    # ------------------------
    if 'grid_id' in cols_in_df:
        metadata['total_grids'] = int(df['grid_id'].nunique())
        metadata['grid_min']    = int(df['grid_id'].min())
        metadata['grid_max']    = int(df['grid_id'].max())
    # ------------------------
    # FIRE METADATA
    # ------------------------
    if include_fire_metrics:
        fire_obs                        = (df[df['fire_lbl'] == True].shape[0])
        metadata['viirs_true_obs']      = fire_obs
        metadata['fire_lbl_proportion'] = round((fire_obs / int(df.shape[0])),4)
        metadata['unique_viirs_grids']  = int(df[df['fire_lbl'] == True]['grid_id'].nunique())

    if 'fwi_max' in cols_in_df:
        metadata['fwi_notna'] = int(df[df['fwi_max'].notna()].shape[0])
    # ------------------------
    # RETURN
    # ------------------------
    return metadata