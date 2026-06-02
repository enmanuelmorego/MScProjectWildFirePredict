import pandas as pd
import geopandas as gpd


def extract_temporal_sample(df_all_in         : pd.DataFrame, 
                            current_grid_id_in : int,
                            current_date_in    : pd.Timestamp, 
                            used_comp_keys_in  : set[str], 
                            temporal_gap_months: int = 6,
                            date_span_days     : int = 15,
                            span_limit_days    : int = 60) -> str | None:
    """
    Find the composite key of a temporal sample

    A temporal sample is selected from the same grid as the target
    observation and centred around a date occurring a specified number
    of months before the target observation date

    The search begins using a +/- `date_span_days` window around the target
    centroid date. If no valid sample is found, the search window is
    expanded incrementally until either a sample is found or
    `span_limit_days` is exceeded

    If multiple valid samples are available, one is selected at random
    If no valid sample can be found, None is returned

Criteria:
    - Same `grid_id` as `current_grid_id_in`
    - Date approximately `temporal_gap_months` before `current_date_in`
    - `composite_key` must not already exist in `used_comp_keys_in`

    Args:
        df_all_in (pd.DataFrame): Data set containing all of the candidate observations (fire and no fire)
        current_grid_id_in (int): Grid identifier of the target observation
        current_date_in (pd.Timestamp): Date of target observation
        used_comp_keys_in (set[str]): Set of composite keys that have already been selected and should therefore be excluded 
        temporal_gap_months (int, optional): Number of months prior to current_date_in around which the search is centred. Defaults to 6.
        date_span_days (int, optional): Initial search window in days on either side of the centroid date. Defaults to 15.
        span_limit_days (int, optional): Maximum search window permitted before abandoning the search. Defaults to 60.

    Returns:
        str | None: A composite_id value of the selected sample, or None if no sample is available
    """    
    # Filter dataset 
    df_candidates     = df_all_in[df_all_in['fire_lbl'] == False]
    # Initialise working span variable
    working_span_days = date_span_days
    # Calculate date to extract samples from
    sample_date_centroid = current_date_in - pd.DateOffset(months = temporal_gap_months)

    # Find the samples
    while True:
        # Generate date range
        min_date = sample_date_centroid - pd.DateOffset(days = working_span_days)  
        max_date = sample_date_centroid + pd.DateOffset(days = working_span_days) 
        # Extract potential set of samples 
        df_potential_samples = df_candidates[  (df_candidates['grid_id'] == current_grid_id_in) 
                                             & (~df_candidates['composite_key'].isin(used_comp_keys_in))
                                             & (df_candidates['date'] >= min_date)
                                             & (df_candidates['date'] <= max_date)]
        # Get total number of potential samples
        int_potential_samples = df_potential_samples.shape[0]
        # If no potential samples are identified
        if  int_potential_samples < 1:
            # Expand the number of days 
            working_span_days += date_span_days
            # If span limit is exceed, then no nample is found
            if working_span_days > span_limit_days:
                return None
            continue
        # Randomly select index of row to select
        temporal_sample = str(df_potential_samples.sample(n=1)['composite_key'].iloc[0])  # type: ignore
        return temporal_sample

def extract_spatial_sample(df_nofire_in: gpd.GeoDataFrame, 
                           x_tgt_in: float,
                           y_tgt_in: float,
                           closest_k_grids: int = 10,
                           max_distance_meters: int = 50000) -> tuple[str | None, float | None]:
    """Find the composite key of a spatial sample

    A spatial sample is selected from the same day as the fire observation from a set of
    `grid_ids` that have not had any wildfires recorded in the dataset

    The no-fire samples are stored in `df_nofire_in`
    The coordinates from the fire observation are used to calculate the distance between each `df_nofire` row and the target observation
    The `x_coord` and `y_coord` values correspond to the British National Grid coordinate system used by the UKCP18 12km grid. These coordinates are expressed in meters. 
    This allows the use of Eucledian Distance to find the closest grids 
    A threshold of `max_distance_meters` is set to avoid sampling locations that are too far from the target value
    A random sample is selected from the `closest_k_grids` found to avoid an overly deterministic sample
    
    Args:
        df_nofire_in (gpd.GeoDataFrame): Data frame containing observations corresponding to grids that have not seen fire in the dataset
        x_tgt_in (float): X coordinate of target, expressed in meters
        y_tgt_in (float): Y coordinate of target, expressed in meters
        closest_k_grids (int, optional): Number of the total closests samples to select as candidate values. Defaults to 10.
        max_distance (int, optional): Maximum distance allowed for an observation to be considered a candidate value. Defaults to 50000.

    Returns:
        tuple[str | None, float | None]: The composite key of the selected sample and the associated distance, in meters, to target values
    """
    
    df_candidates = df_nofire_in.copy()
    # Calculate the Eucledian Distance between the target inputs and the available observations to sample
    df_candidates['distance'] = ((df_candidates['x_coord'] - x_tgt_in)**2 + (df_candidates['y_coord'] - y_tgt_in)**2)**0.5
    # Limit candidates to a distance threshold
    df_candidates = df_candidates[df_candidates['distance'] <= max_distance_meters]
    # Sort values to select closest
    df_candidates = df_candidates.sort_values('distance')
    # Select top candidates
    df_candidates = df_candidates.head(closest_k_grids)
    # Fail safe, in case no values are found
    if df_candidates.empty:
        return None, None
    # Sample single, random candidate
    sample_row = df_candidates.sample(n=1)
    sample_key = sample_row['composite_key'].iloc[0]
    sample_dist = sample_row['distance'].iloc[0]

    return sample_key, sample_dist

def create_y_target_sampled_df(dict_sampled_dict: dict, df_all_in: gpd.GeoDataFrame) -> pd.DataFrame: 
    """Takes the sampled composite keys stored in the dictionary and combines them into a single 
    data frame.
    Data frame is then left joined with `df_all_in` to extract relevant values to aid the creation
    of the final sampled dataset. All columns are suffixed with '_y' to show distinction when
    joining with the main dataset later

    Args:
        dict_sampled_dict (dict): Dictionary containing the composite_keys of the sampled observations
        df_all_in (gpd.GeoDataFrame): Df containing pre processed tabular data

    Returns:
        pd.DataFrame: Data frame with composite keys of sampled values along with relevant columns. See below
        Columns: `{composite_key_y, sample_type_y, date_y, fire_lbl_y}`
    """
    # Extract values into lists
    fire_ls =    [x for x in dict_sampled_dict["fire_lbl_comp_key"]        if x is not None]
    temp_ls =    [x for x in dict_sampled_dict['temporal_sample_comp_key'] if x is not None]
    spatial_ls = [x for x in dict_sampled_dict['spatial_sample_comp_key']  if x is not None]
    # Combine into a single dataframe
    df_comp_key_y = pd.concat([pd.DataFrame({'composite_key': fire_ls,
                                             'sample_type': 'fire'}),
                               pd.DataFrame({'composite_key': temp_ls,
                                             'sample_type': 'temporal'}),
                               pd.DataFrame({'composite_key': spatial_ls,
                                             'sample_type': 'spatial'})],
                            ignore_index = True)
    # Extract variables from main df
    df_y = pd.merge(df_comp_key_y, df_all_in, how = 'left', on = 'composite_key')
    # # Select relevant columns 
    df_y = df_y[['composite_key', 'grid_id', 'sample_type', 'date', 'fire_lbl']]
    df_y = df_y.add_suffix("_y")

    return df_y

def create_sampled_df(df_all_in: gpd.GeoDataFrame, df_sampled: pd.DataFrame) -> pd.DataFrame:
    """Creates sampled dataset by combining the sampled target variables with their respective t-1 observations
    and preditor variables. 
    It creates a `bridge_composite_key` by taking the date of teh tgt value - 1 day, the composite key is created and 
    joined with `df_all_in` dataset to create the final sampled data set from which sentinel 2 data is fetched for

    Args:
        df_all_in (gpd.GeoDataFrame): Tabular data set containing day x grid + predictors
        df_sampled (pd.DataFrame): Transformed sampled dataset - Target (y) variable

    Returns:
        pd.DataFrame: sampled dataframe with both x and y (minus sentinel-2 features)
    """
    # Create bridge composite key (1 day before the y observations)
    df_tgt_y_values = df_sampled.copy()
    df_tgt_y_values["bridge_composite_key_y"] = df_tgt_y_values["grid_id_y"].astype(str) + (df_tgt_y_values["date_y"]-pd.DateOffset(days=1)).dt.strftime("%Y%m%d")
    # Join sampled df with df_all_in to create sampled dataset
    df_sampled = pd.merge(df_tgt_y_values, df_all_in, how = 'left', left_on = 'bridge_composite_key_y', right_on = 'composite_key')
    return df_sampled

if __name__ == '__main__':
    import pandas as pd

    df_fire = pd.DataFrame({"grid_id": [1, 1, 1, 1, 2, 2, 3],
                            "date": pd.to_datetime(["2020-06-15",  
                                                    "2020-06-20",  
                                                    "2020-07-01",  
                                                    "2020-12-15",  
                                                    "2020-06-15",
                                                    "2020-12-15",
                                                    "2020-12-15"]),
                            "composite_key": ["1_20200615",
                                              "1_20200620",
                                              "1_20200701",
                                              "1_20201215",
                                              "2_20200615",
                                              "2_20201215",
                                              "3_20201215"]})
               
    samples_dict = {'fire_lbl_comp_key'       : [],
                    'temporal_sample_comp_key': [],
                    'spatial_sample_comp_key' : [],
                    'used_comp_keys'          : {"A_20200620"}}
             
    sample = extract_temporal_sample(df_all_in=df_fire,
                                    current_grid_id_in=1,
                                    current_date_in=pd.Timestamp("2020-12-15"),
                                    used_comp_keys_in = samples_dict['used_comp_keys'])
    
    print(sample)
