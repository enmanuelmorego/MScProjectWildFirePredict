

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

if __name__ == "__main__":
    d = {'fire_lbl_comp_key': []}
    print(basic_desc_sampled(d, 'spatial'))