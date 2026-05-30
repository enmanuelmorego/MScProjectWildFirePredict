import pandas as pd



def extract_temporal_sample(df_fire_in         : pd.DataFrame, 
                            current_grid_id_in : str,
                            current_date_in    : pd.Timestamp, 
                            used_comp_keys_in  : set[str], 
                            temporal_gap_months: int = 6,
                            date_span_days     : int = 15,
                            span_limit_days    : int = 60) -> str | None:
    """
    Find the composite key of a temporal sample.

    A temporal sample is selected from the same grid as the target
    observation and centred around a date occurring a specified number
    of months before the target observation date.

    The search begins using a +/- date_span_days window around the target
    centroid date. If no valid sample is found, the search window is
    expanded incrementally until either a sample is found or
    span_limit_days is exceeded.

    If multiple valid samples are available, one is selected at random.
    If no valid sample can be found, None is returned.

Criteria:
    - Same grid_id as current_grid_id_in.
    - Date approximately temporal_gap_months before current_date_in.
    - composite_key must not already exist in used_comp_keys_in.

    Args:
        df_fire_in (pd.DataFrame): Data set containing all of the candidate fire observations
        current_grid_id_in (str): Grid identifier of the target observation
        current_date_in (pd.Timestamp): Date of target observation
        used_comp_keys_in (set[str]): Set of composite keys that have already been selected and should therefore be excluded 
        temporal_gap_months (int, optional): Number of months prior to current_date_in around which the search is centred. Defaults to 6.
        date_span_days (int, optional): Initial search window in days on either side of the centroid date. Defaults to 15.
        span_limit_days (int, optional): Maximum search window permitted before abandoning the search. Defaults to 60.

    Returns:
        str | None: A composite_id value of the selected sample, or None if no sample is available
    """    
    working_span_days = date_span_days
    # Calculate date date to extract samples from
    sample_date_centroid = current_date_in - pd.DateOffset(months = temporal_gap_months)

    # Find the samples
    while True:
        # Generate date range
        min_date = sample_date_centroid - pd.DateOffset(days = working_span_days)  
        max_date = sample_date_centroid + pd.DateOffset(days = working_span_days) 
        # Extract potential set of samples 
        df_potential_samples = df_fire_in[  (df_fire_in['grid_id'] == current_grid_id_in) 
                                          & (~df_fire_in['composite_key'].isin(used_comp_keys_in))
                                          & (df_fire_in['date'] >= min_date)
                                          & (df_fire_in['date'] <= max_date)]
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

if __name__ == '__main__':
    import pandas as pd

    df_fire = pd.DataFrame({"grid_id": ["A", "A", "A", "A", "B", "B", "C"],
                            "date": pd.to_datetime(["2020-06-15",  
                                                    "2020-06-20",  
                                                    "2020-07-01",  
                                                    "2020-12-15",  
                                                    "2020-06-15",
                                                    "2019-11-20",
                                                    "2020-12-15"]),
                            "composite_key": ["A_20200615",
                                            "A_20200620",
                                            "A_20200701",
                                            "A_20201215",
                                            "B_20200615",
                                            "B_20191120",
                                            "C_20201215"]})
               
    samples_dict = {'fire_lbl_comp_key'       : [],
                    'temporal_sample_comp_key': [],
                    'spatial_sample_comp_key' : [],
                    'used_comp_keys'          : set()}
    
    sample_short = extract_temporal_sample(df_fire_in=df_fire,
                                              current_grid_id_in="B",
                                              current_date_in=pd.Timestamp("2020-06-15"),
                                              used_comp_keys_in = samples_dict['used_comp_keys'])
    print(sample_short)
