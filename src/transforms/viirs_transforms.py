"""
Module of data transformations for VIIRS
"""
import pandas as pd
import geopandas as gpd
from typing import TypedDict

# Pre define complex dictionaries type hints
class MergeViirsOutput(TypedDict):
    df: pd.DataFrame
    data_report: dict | None

def merge_viirs(viirs_dict: dict[str, pd.DataFrame], append_noaa: bool = True) -> MergeViirsOutput:
    """Takes a dictionary containing data frame from VIIRS products (NOAA and SNPP) and merged them into a single data frame.
    Data from SNPP takes precedence over NOAA as SNPP data is more robust and undergoes more strict QA

    Args:
        viirs_dict (dict[str, pd.DataFrame]): Dictionary containing NOAA and SNPP data frames
        append_noaa (bool, optional): Option for user to completly ignore NOAA data. Defaults to True.

    Raises:
        ValueError: When SNPP data is not provided 

    Returns:
        dict[str, Any]: `df`: Data frame merged. `data_report`: a dictionary containing information on the rows and data origin
    """

    cols_merge = ['longitude','latitude','acq_date']
    df_snpp    = viirs_dict.get('snpp')
    df_noaa    = viirs_dict.get('noaa')

    if df_snpp is None:
        raise ValueError("❌ SNPP data is required")

    if append_noaa and df_noaa is not None:
        # Find values in NOAA not in SNPP 
        df_diff = df_noaa.loc[~df_noaa.set_index(cols_merge).index.isin(df_snpp.set_index(cols_merge).index)]
        df_out  = pd.concat([df_snpp, df_diff], ignore_index = True)

        data_report = {'total_rows_snpp': df_snpp.shape[0],
                       'total_rows_noaa': df_diff.shape[0]}
        return {'df'         : df_out,
                'data_report': data_report}
    else:
        return {'df'         : df_snpp,
                'data_report': None}

def filter_viirs(viirs_data: pd.DataFrame) -> pd.DataFrame:
    """Filters the VIIRS data to only the desired rows to ensure data quality
    - Filter only Vegetation Fires:                     `type == 0`
    - Filter to keep Nominal and high Confidence class: `confidence == 'N' or confidence == 'H'`

    Args:
        viirs_data (pd.DataFrame): Combined, full viirs dataframe

    Returns:
        pd.DataFrame: Dataframe filtered to relevant rows only
    """  
    df_viirs = viirs_data.copy()
    df_viirs['confidence'] = df_viirs['confidence'].str.lower().str.strip()
    df_out = df_viirs[(df_viirs['type'] == 0) & 
                        (df_viirs['confidence'].isin(['h','n']))
                    ].copy()
    return df_out

def transform_to_geo_viirs(viirs_data: pd.DataFrame, crs: str) -> gpd.GeoDataFrame:
    """ Function to transform the VIIRS input data to a GeoPandasDataFrame


    Args:
        viirs_data (pd.DataFrame): Dataframe with VIIRS data, filtered and cleaned
        crs (str): A string containing the EPSG value to set the CRS

    Returns:
        gpd.GeoDataFrame: Transformed dataset from pandas to geopandas
    """
    viirs_geo = gpd.GeoDataFrame(viirs_data, geometry=gpd.points_from_xy(viirs_data.longitude, viirs_data.latitude), crs=crs)
    return viirs_geo