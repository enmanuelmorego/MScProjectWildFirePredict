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
    df_viirs = df_viirs.rename(columns = {'acq_date': 'date'})
    df_viirs_joined = gpd.sjoin(df_viirs, df_uk_grid, how = 'inner', predicate = 'within')
    df_viirs_summary = (df_viirs_joined
                        .groupby(['grid_id', 'date'], as_index = False)
                        .agg(viirs_n  = ('frp', 'size'),
                             frp_max  = ('frp', 'max'),
                             frp_mean = ('frp', 'mean')))
    df_viirs_summary['fire_lbl'] = True
    
    return df_viirs_summary
