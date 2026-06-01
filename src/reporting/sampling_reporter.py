import numpy as np
def basic_desc_sampled(sampled_dict_in: dict, sampling_type: str) -> dict:
    """Calculates basic descriptives values from the sampled data set
    Allows to get an overview of the sampling procedure results

    Args:
        sampled_dict_in (dict): Dictionary containing the results of the sampling process
        sampling_type (str): String to indicate whether the user wants to calculate the basic stats for temporal or spatial sampling

    Returns:
        (dict): Contains the calculated stats
    
    Example:
    {'n_fire'     : n_fire,
     'n_sampled'  : n_sampled,
     'n_missing'  : n_missing,
     'pct_missing': pct_missing}

    """
    sampling_input = sampling_type.lower()
    valid_inputs = ['temporal', 'spatial']
    if sampling_input not in ('temporal', 'spatial'):
        raise ValueError(f"Please enter valid value for `sampling_type` parameter. \nOptions: {valid_inputs} ")
    
    sampling_type_key = {'temporal': 'temporal_sample_comp_key',
                         'spatial': 'spatial_sample_comp_key'}
    sampling_key = sampling_type_key[sampling_input]
    
    n_fire      = len(sampled_dict_in['fire_lbl_comp_key'])
    n_sampled   = len([s for s in sampled_dict_in[sampling_key] if s is not None])
    n_missing   = len([s for s in sampled_dict_in[sampling_key] if s is None])
    pct_missing = round(n_missing / n_fire,2)


    return {'n_fire'     : n_fire,
            'n_sampled'  : n_sampled,
            'n_missing'  : n_missing,
            'pct_missing': pct_missing}

def desc_stats_spatial_samples(dist_values_list: list) -> dict: 
    """Calculates the basic descriptive statistics on the distance from sample to fire observation

    Args:
        dist_values_list (list): List of the distance (in meters) of the sample taken for each fire observation

    Returns:
        dict: Dictionary containing the basic descriptive stats
    """
    distance_values = [d for d in dist_values_list if d is not None]
    return {'mean_dist'  : round(np.mean(distance_values)),
            'median_dist': round(np.median(distance_values)),
            'std_dist'   : round(np.std(distance_values)),
            'min_dist'   : round(np.min(distance_values)),
            'max_dist'   : round(np.max(distance_values))}

def create_sampling_statistics(sampled_dict_in: dict) -> dict:
    """Wrapper functiont that calls the statistics generating functions

    Args:
        sampled_dict_in (dict): Dictionary with sampled values

    Returns:
        dict: Dicitonary with sampling statistics
    """    
    temp_basic    = basic_desc_sampled(sampled_dict_in, 'temporal')
    spatial_basic = basic_desc_sampled(sampled_dict_in, 'spatial')
    spatial_spec  = desc_stats_spatial_samples(sampled_dict_in['spatial_sample_dist'])
    return {'spatial_samples_stats': spatial_basic | spatial_spec,
            'temporal_samples_stats':  temp_basic}


if __name__ == "__main__":

    test_desc = [10, None, 22, 100, 40, None, 22]
    print(desc_stats_spatial_samples(test_desc))