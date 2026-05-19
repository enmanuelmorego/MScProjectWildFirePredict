"""
Module that contains all pre processing steps to transform raw tabular data into a single data dataframe
"""
import pandas as pd
import geopandas as gpd

def aggregate_viirs_to_grid(df_viirs: gpd.GeoDataFrame, df_uk_grid: gpd.GeoDataFrame) -> pd.DataFrame:
    """Function that summarises VIIRS data and generates fire/nofire labels for each `grid_id` `date` pairs (and renames acq_date to date)
       
       Each VIIRS observation corresponds to an identified fire. All observations within a grid get summarised into a single
       row of data. Summary stats are taken for the following values:
       - Number of VIIRS observations in grid (`n`)
       - Max FRP value in grid
       - Mean FRP value
    Args:
        df_viirs (gpd.GeoDataFrame): Dataframe containing the data from VIIRS satellite
        df_uk_grid (gpd.GeoDataFrame): Geo data frame with all the UK grid coordinates

    Returns:
        pd.DataFrame: Dataframe with VIIRS data collapsed per grid, with max and mean values for each grid
            The dataframe contains only those `grid_id` where a VIIRS signal was present
    """
    df_viirs        = df_viirs.rename(columns = {'acq_date': 'date'})
    df_viirs_joined = gpd.sjoin(df_viirs, df_uk_grid, how = 'inner', predicate = 'within')
    df_viirs_summary = (df_viirs_joined
                        .groupby(['grid_id', 'date'], as_index = False)
                        .agg(viirs_n  = ('frp', 'size'),
                             frp_max  = ('frp', 'max'),
                             frp_mean = ('frp', 'mean')))
    df_viirs_summary['fire_lbl'] = True
    
    return df_viirs_summary

def build_tabular_dataset(df_viirs: pd.DataFrame, dict_dfs: dict) -> gpd.GeoDataFrame:
    """Combines `df_viirs` with `grid_ids` to the df containing all grids+days combination (`df_daily_grid`) and also with `df_fwi`

    Fills in NAs for the following variables with the following values:

    - fire_lbl = False
    - viirs_n  = 0
    - far_max  = 0
    - frp_mean = 0

    Args:
        df_viirs (pd.DataFrame): Data frame containing VIIRS data with grid ids
        dict_dfs (dict): Dictionary containg all loaded raw inputs

    Returns:
        (gpd.GeoDataFrame): Data frame preprocessed with all the datasets combined into a single df
    """
    # ------------------------
    # EXTRACT DFs
    # ------------------------
    df_grids_day  = dict_dfs['df_daily_grid']
    df_fwi        = dict_dfs['df_fwi']
    # ------------------------
    # PROCESS VIIRS
    # ------------------------
    df_viirs_grid             = df_grids_day.merge(df_viirs, on = ['grid_id','date'], how = 'left')
    df_viirs_grid['fire_lbl'] = (df_viirs_grid['fire_lbl']
                                 .astype('boolean')
                                 .fillna(False))
    df_viirs_grid[['viirs_n', 'frp_max', 'frp_mean']] = df_viirs_grid[['viirs_n', 'frp_max', 'frp_mean']].fillna(0)
    # ------------------------
    # PROCESS FWI
    # ------------------------
    df_fwi_viirs_grid = df_viirs_grid.merge(df_fwi,
                                            on = ['grid_id','date'],
                                            how = 'left')
    
    return df_fwi_viirs_grid

def remove_na_fwi_grid1(df: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Removes grid_id = 1 from the dataset as the FWI value for grid_id 1 was missing across the sample
    
    During spatial validation of the FWI raster-to-grid mapping, grid_id = 1 (a coastal grid in south-west England) was found to
    have missing FWI values for all day

    Rationale

        - The grid represents <0.1% of all spatial units,
        - FWI is entirely missing for that grid across all dates,
        - Imputation would introduce artificial meteorological signal,

    the grid is removed from the modelling dataset to preserve
    data integrity.

    This is only removed IF grid_id == 1 AND fwi value is NA

    Args:
        df (gpd.GeoDataFrame): Preprocessed dataframe

    Returns:
        gpd.GeoDataFrame: Dataset excluding grid_id = 1.
    """
    remove = ((df['grid_id'] == 1) &
              (df['fwi_max'].isna()))
  
    rr = remove.sum()
    if rr > 0:
        print(f"\tℹ️  Removed {rr} rows with grid_id == 1")
    else:
        print(f"\t✅  No grids to remove - grid_id contains data")

    df_out = df[~remove].copy()
    return df_out

def create_composite_key(df: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Function that creates composite key, which is the unique identifier for each row (primary key). 
    It also validates the column to ensure there are no duplicates and can be used as primary key

    Args:
        df (gpd.GeoDataFrame): preprocessed dataframe with all the inputs combined

    Raises:
        ValueError: If `composite_key` contains duplicated values, then cannot be used a primary key, raises ValueError

    Returns:
        gpd.GeoDataFrame: copy of input dataframe with an added `composite_key` column
    """
    # ------------------------
    # CREATE COMPOSITE KEY
    # ------------------------
    df_out = df.copy()
    df_out['composite_key'] = (df_out['grid_id'].astype(str) + 
                               df_out['date'].dt.strftime("%Y%m%d"))
    # ------------------------
    # VALDIATE COMPOSITE KEY
    # ------------------------
    total_rows        = df_out.shape[0]
    total_unique_keys = int(df_out['composite_key'].nunique())
    if total_rows != total_unique_keys:
        raise ValueError("❌ There are duplicated values in composite_key")
    
    return df_out