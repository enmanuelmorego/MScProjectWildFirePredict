import pandas as pd
import random as rd

def extract_temporal_samples(df_fire_in: pd.DataFrame, 
                             current_grid_id_in: str,
                             current_date_in: pd.Timestamp, 
                             dict_samples_in: dict, 
                             temporal_gap_months: int = 6,
                             date_span_days: int      = 15,
                             span_limit_days: int     = 60):
    
    sample_found      = False
    working_span_days = date_span_days
    unavailable_comp_keys = dict_samples_in['used_comp_keys']
    # Calculate date date to extract samples from
    sample_date_centroid = current_date_in - pd.DateOffset(months = temporal_gap_months)

    # Find the samples
    while not sample_found:
        # Generate date range
        min_date = sample_date_centroid - pd.DateOffset(days = date_span_days)  
        max_date = sample_date_centroid + pd.DateOffset(days = date_span_days) 
        # Extract potential set of samples 
        df_potential_samples = df_fire_in[  (df_fire_in['grid_id'] == current_grid_id_in) 
                                          & (df_fire_in['composite_key'] not in unavailable_comp_keys)
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
                dict_samples_in['temporal_sample_comp_key'].append(None)
                sample_found = True
            
        # Randomly select index of row to select
        select_row = rd.randint(0, int_potential_samples)
        temporal_sample = df_potential_samples.loc[select_row, composite_key_idx]  # type: ignore
        dict_samples_in['temporal_sample_comp_key'].append(temporal_sample)
        dict_samples_in['used_comp_keys'].append(temporal_sample)
        sample_found = True
    return dict_samples_in

