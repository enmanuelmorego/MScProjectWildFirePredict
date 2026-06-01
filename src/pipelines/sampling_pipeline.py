import pandas as pd
import geopandas as gdp
import src.sampling.sampling_functions as sf
from typing import cast 

def create_samples_dict(df_in: gdp.GeoDataFrame) -> dict:

    # Create subsets of dataframes
    df      = df_in.copy()
    df_fire = df[df['fire_lbl'] == True]

    # Extract dataset that has never seen a fire 
    df_nofire = df[~df['grid_id'].isin(df_fire['grid_id'])]

    # Initialise dictionary to store samples
    samples_dict = {'fire_lbl_comp_key'       : [],
                    'temporal_sample_comp_key': [],
                    'spatial_sample_comp_key' : [],
                    'spatial_sample_dist'     : [],
                    'used_comp_keys'          : set()}
    
    # Extract samples
    for row in df_fire.itertuples():
        # Extract relevant elements from fire observation
        composite_tgt = row.composite_key
        grid_tgt      = cast(int, row.grid_id)
        date_tgt      = cast(pd.Timestamp, row.date)
        x_tgt         = cast(float, row.x_coord)
        y_tgt         = cast(float, row.y_coord)
        used_comp_key = samples_dict['used_comp_keys']
        # Prepare datasets to sample from (reduce size for more efficiency)
        df_to_sample_temporal = df[df['grid_id'] == grid_tgt]
        df_to_sample_spatial  = df_nofire[df_nofire['date'] == date_tgt]
        # Find samples
        temp_sample                 = sf.extract_temporal_sample(df_to_sample_temporal, grid_tgt, date_tgt, used_comp_key)
        spatial_sample, sample_dist = sf.extract_spatial_sample(df_to_sample_spatial, x_tgt, y_tgt)
        # SAve results in dictionary 
        samples_dict['fire_lbl_comp_key'].append(composite_tgt)
        samples_dict['temporal_sample_comp_key'].append(temp_sample)
        samples_dict['spatial_sample_comp_key'].append(spatial_sample)
        samples_dict['spatial_sample_dist'].append(sample_dist)
        if temp_sample is not None:
            samples_dict['used_comp_keys'].add(temp_sample)
        if spatial_sample is not None:
            samples_dict['used_comp_keys'].add(spatial_sample)
    
    return samples_dict
