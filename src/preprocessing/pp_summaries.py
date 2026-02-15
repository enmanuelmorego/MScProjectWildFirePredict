'''
Scripts that collapses and summarises data frames into specified format for analysis
'''
import pandas as pd
import geopandas as gpd
import src.utils as u

def summarise_viirs(df_viirs: pd.DataFrame, df_uk_grid: gpd.GeoDataFrame) -> pd.DataFrame:
    """
    Function that summarises VIIRS data and generates fire/nofire labels for each `grid_id` `date` pairs (and renames acq_date to date)

    Each VIIRS observation corresponds to an identified fire. All observations within a grid get summarised into a single
    row of data. Summary stats are taken for the following values:
        - Number of VIIRS observations in grid (`n`)
        - Max FRP value in grid
        - Mean FRP value

    Args:
        df_viirs (dataframe): Dataframe containing the data from VIIRS satellite
        df_uk_grid (GeoDataframe): Geo data frame with all the UK grid coordinates

    Returns:
        df: Dataframe with VIIRS data collapsed per grid, with max and mean values for each grid
            The dataframe contains only those `grid_id` where a VIIRS signal was present

    """
    df_viirs = df_viirs.rename(columns = {'acq_date': 'date'})
    df_viirs_joined = gpd.sjoin(df_viirs, df_uk_grid, how = 'inner', predicate = 'within')
    df_viirs_summary = (df_viirs_joined
                        .groupby(['grid_id', 'date'], as_index = False)
                        .agg(viirs_n  = ('frp', 'size'),
                             frp_max  = ('frp', 'max'),
                             frp_mean = ('frp', 'mean')))
    df_viirs_summary['fire_lbl'] = True
    
    return df_viirs_summary

def combined_dfs(dict_dfs: dict):
    """
    Combines all data sources into a single data frame with all the relevant features for the model (Except for sentinel image data)
    Left joins the df_viirs_summary to the df_daily_uk by (`grid_id`, `date`) to have a full dataset with fire observations labels and UK grid data 
    Fills in NAs for the following variables with the following values:

        - fire_lbl = False
        - viirs_n  = 0
        - far_max  = 0
        - frp_mean = 0
    """
    # Extract data frames from dictionary
    try:
        df_grids_day  = dict_dfs['df_daily_grid']
        df_viirs_summ = dict_dfs['df_viirs_summary']
        df_fwi        = dict_dfs['df_fwi']
    except KeyError as e:
        raise KeyError(f"❌ Missing required dataframe {e}")

    # Process VIIRS data
    df_viirs_grid                                     = df_grids_day.merge(df_viirs_summ, on = ['grid_id','date'], how = 'left')
    df_viirs_grid['fire_lbl']                         = (df_viirs_grid['fire_lbl']
                                                        .astype('boolean')
                                                        .fillna(False))
    df_viirs_grid[['viirs_n', 'frp_max', 'frp_mean']] = df_viirs_grid[['viirs_n', 'frp_max', 'frp_mean']].fillna(0)

    # Process FWI data
    df_fwi_viirs_grid = df_viirs_grid.merge(df_fwi,
                                            on = ['grid_id','date'],
                                            how = 'left')
    
    return df_fwi_viirs_grid

def remove_na_fwi_grid1(df: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Removes grid_id = 1 from the dataset as the FWI value for grid_id 1 was missing across the sample

    During spatial validation of the FWI raster-to-grid mapping, grid_id = 1 (a coastal grid in south-west England) was found to
    have missing FWI values for all day

    Rationale

        - The grid represents <0.1% of all spatial units,
        - FWI is entirely missing for that grid across all dates,
        - Imputation would introduce artificial meteorological signal,

    the grid is removed from the modelling dataset to preserve
    data integrity.

    This is only removed IF grid_id == 1 AND fwi value is NA

    Returns:
        
        pd.DataFrame
            Datas