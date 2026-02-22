'''
Scripts that collapses and summarises data frames into specified format for analysis
'''
import pandas as pd
import geopandas as gpd
import utils as u
from datetime import datetime

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
            Dataset excluding grid_id = 1.
    """
    remove = ((df['grid_id'] == 1) &
              (df['fwi'].isna())
              )
  
    rr = remove.sum()
    if rr > 0:
        print(f"\tℹ️  Removed {rr} rows with grid_id == 1")
    else:
        print(f"\t✅  No grids to remove - grid_id contains data")

    df_out = df[~remove].copy()
    return df_out

def preprocessing_pipeline(df_dict: dict, run_id: str) -> gpd.GeoDataFrame:
    """
    Wrapper function to execute the preprocessing tasks

    Args:
        df_dict

        run_id (str): String containing the identifiator of the run to save all the relevant logs for the current run
    """
    try:
        df_viirs   = df_dict['df_viirs']
        df_uk_grid = df_dict['df_uk_grid']
    except KeyError as e:
        raise KeyError(f"❌ Missing required dataframe {e}")

    df_viirs_summary            = summarise_viirs(df_viirs, df_uk_grid)
    df_dict['df_viirs_summary'] = df_viirs_summary
    loaded_data_mt              = u.dfs_metadata(df_dict)
    u.save_json(loaded_data_mt,"LOAD_METADATA", run_id)

    df_model_pre_raw = combined_dfs(df_dict)
    df_model_pre     = remove_na_fwi_grid1(df_model_pre_raw)
  #  df_model_sampled = sample_by_fire_lbl(df_model_pre)

    df_model_pre['composite_key'] = (df_model_pre['grid_id'].astype(str) + 
                                     df_model_pre['date'].dt.strftime("%Y%m%d"))

    df_model_summary = {'df_type'            : type(df_model_pre).__name__,
                        'columns'            : list(df_model_pre.columns),
                        'date_from'          : df_model_pre['date'].min().strftime("%Y-%m-%d"),
                        'date_to'            : df_model_pre['date'].max().strftime("%Y-%m-%d"),
                        'total_rows'         : int(df_model_pre.shape[0]),
                        'total_grids'        : int(df_model_pre['grid_id'].nunique()),
                        'grid_min'           : int(df_model_pre['grid_id'].min()),
                        'grid_max'           : int(df_model_pre['grid_id'].max()),
                        'viirs_true_obs'     : int(df_model_pre[df_model_pre['fire_lbl'] == True].shape[0]),
                        'fire_lbl_proportion': int(df_model_pre[df_model_pre['fire_lbl'] == True].shape[0]) / int(df_model_pre.shape[0]),
                        'unique_viirs_grids' : int(df_model_pre[df_model_pre['fire_lbl'] == True]['grid_id'].nunique()),
                        'fwi_notna'          : int(df_model_pre[df_model_pre['fwi'].notna()].shape[0])
                        }
                        
    u.save_json(df_model_summary,"PREPROCESSING_METADATA", run_id)
    

    return df_model_pre

# -------------------------
# SAMPLING FIRE DATAPOINTS
# -------------------------  
"""
Sampling is necessary to reduce computational power and address the imbalanced dataset due to low wildfire occurrence
The chosen ratio is 1:3 but the suite of functions is flexible to adjust this ratio if needed
"""
def sample_fire_values(df_preprocessed: gpd.GeoDataFrame, window_size: int) -> pd.DataFrame:
    """
    Function that extracts the fire label data points from the preprocessed data set
    It selects all rows where a fire was detected, and generates a window of the preceeding X number of days
    which will be used to fetch the satellite images
    This window also includes the actual fire label value as well to avoid sampling this as a no fire observation by mistake

    Args:
        df_preprocessed (GeoDataframe): Preprocessed dataframe containing FWI, FireLabel per day/grid
        window_size (int): How many days of data prior to the fire datapoint
    
    Returns:
        df_out (df): Dataframe containing `date`, `grid_id`, `fire_lbl`,`composite_key'
    """
    # Initialise dictionary to store results per iteration
    dict_sampled_values = {'composite_key': [],
                           'date'         : [],
                           'grid_id'      : []}

    # Generate subset of fire labels
    df_fire                  = df_preprocessed[df_preprocessed['fire_lbl'] == True].copy()

    for r in df_fire.itertuples():
        current_date     = r.date
        current_grid     = r.grid_id
        current_comp_key = r.composite_key
        # Generate window of dates
        current_window = pd.date_range(start = (current_date - pd.Timedelta(days = window_size)),
                                       end   =  current_date)
        n_repeat = len(current_window)
        dict_sampled_values['date'].extend(current_window)
        dict_sampled_values['grid_id'].extend([current_grid] * n_repeat)
        dict_sampled_values['composite_key'].extend([current_comp_key] * n_repeat)

    df_out = pd.DataFrame(dict_sampled_values)
    df_out = df_out.drop_duplicates(subset = ['grid_id','date'])
    return df_out

def sample_nofire_candidates(df_preprocessed: gpd.GeoDataFrame, candidate_window: int) -> dict:
    """
    Function to sample the possible non-fire candidate observations for the sampling ratio process
    For each fire label value, finds all possible non fire labels for the same grid that are +/- X days (defaults to 30) from
    the fire label

    Args: 
        df_preprocessed (GeoDataFrame): Preprocessed dataframe containing FWI, FireLabel per day/grid
        candidate_window (int): Number of days to +/- to find corresponding non fire values for same grid

    Returns:
        dict_out (dict): Dictionary containing composite key for fire label as dict key and no fire valid rows for given composite key
    """  
    df_fire           = df_preprocessed[df_preprocessed['fire_lbl'] == True].copy()
    df_nofire         = df_preprocessed[df_preprocessed['fire_lbl'] == False].copy()
    nofire_candidates = {}

    for r in df_fire.itertuples():
        fire_grid_id       = r.grid_id
        fire_date          = r.date
        fire_composite_key = r.composite_key

        try:
            # Extract ALL potential no fire candidate values
            nofire_sample = df_nofire[(
                                        (df_nofire['grid_id'] == fire_grid_id) &
                                        # Find days within a 30 day range of current date 
                                        ((df_nofire['date'] >= (fire_date - pd.DateOffset(days=candidate_window))) &
                                         (df_nofire['date'] <= (fire_date + pd.DateOffset(days=candidate_window)))) 
                                      )]
            # Save in dictionary
            nofire_candidates[fire_composite_key] = nofire_sample
        except ValueError:
            nofire_candidates[fire_composite_key] = None
    return nofire_candidates

       