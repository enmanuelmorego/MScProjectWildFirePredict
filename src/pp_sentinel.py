import ee
import tensorflow as tf
import numpy as np
import os
from pathlib import Path
import tensorflow as tf
import pandas as pd
import math

def split_batch_greater_than_limit(date_obj: pd.Timestamp, current_group_size: int, batch_size: int, start_batch_num: int) -> tuple[dict, int]:
    """"
    Function to split a group of dates that are greater than the batch limit into subgroups of size appropiate for sentinel fetch process 

    Args:
        - date_obj (pd.Timestamp): The current date object from the main dataframe
        - current_group_size (int): The size of the current group (which is larger than batch_size)
        - batch_size (int): The max size allowed for each batch
        - start_batch_num (int): The current working batch number

    Returns
        - tuple(dict, int): A tuple containing the updated dictionary and the update batch number 
    """
    results      = dict()
    current_year = date_obj.year
    date_str     = date_obj.strftime("%Y%m%d")
    batch_num    = start_batch_num
    start_i      = 0

    while current_group_size > 0: 
        group_name          = f"{current_year}_B{batch_num:03}_{date_str}_{date_str}_sentinel_batch"
        group_size          = min(current_group_size, batch_size)
        end_i               = start_i + group_size
        results[group_name] = {'date'       : [date_obj],
                               'split_group': [start_i, end_i]}
        current_group_size -= group_size
        batch_num          += 1
        start_i             = end_i 

    return results, batch_num

def close_current_batch(group_list: list, batch_num: int) -> tuple[dict, int]:
    """
    Function to close the current working batches. This is applicable when the sum of concurrent group batches hits the 
    batch size limit.
    The funcion performs the following actions:
    - Extracts the earliest date and latest date from the working list (`group_list`) and format the values as strings
    - Generates the batch name
    - Creates a dictionary with the key value pairs where key is file name, and value are all the dates per batch
    - Updates the batch number

    Args:
    - group_list (list): A list of pd.Timestamp object representing the dates of the groups that fit into batch 
    - start_batch_num (int): The current working batch number

    Returns
        - tuple(dict, int): A tuple containing the updated dictionary and the update batch number 
    """
    results = dict()
    # Extract values 
    min_date     = group_list[0].strftime("%Y%m%d")
    max_date     = group_list[-1].strftime("%Y%m%d")
    current_year = group_list[0].year

    group_name          = f"{current_year}_B{batch_num:03}_{min_date}_{max_date}_sentinel_batch"
    results[group_name] = {'date'       : sorted(list(set(group_list))),
                           'split_group': None}
    batch_num          +=1

    return results, batch_num

def sampled_to_batch(df_sampled: pd.DataFrame, batch_size: int = 800) -> dict:
    """
    Function that takes the sampled data and splits it into batches manageable for `Sentinel` download

    Requisites:
    - DataFrame batches must be <= 800 rows. This is important to avoid RAM crashes, requests errors, among other
    - All batches must contain complete day ranges. All values associated with a given date must be included in the batch
    - The reason for the requirement above is to ensure that start-end filenames can be used to accuratetly fetch the data covering the period mentioned in the filename

    Naming Convention:
        Batches names follow the convention `YYYY_Bnnn_YYYYMMDD_YYYYMMDD_sentinel_batch` where:
         - `YYYY` is the current year
         - `Bn` is Batch number. This is important as if a single day contains more than 800 values, it can still be uniquely stored by simply adding +1 to the nnn value
         - `YYYYMMDD_YYYYMMDD` are the dates from-to that the data currently covers

    Cases:
        - If 2020-01-01 contains 700 observations, and 2020-01-01 contains 200 observations, then batch size will be only 700 and only include the records for 2020-01-01
        - If 2020-01-01 contains 900 observations, then two batches are generated: 
            - `2020_B001_20200101_20200101_sentinel_batch`
            - `2020_B002_20200101_20200101_sentinel_batch`

    Args:
        - df_sampled (df): Data frame containing the sampled data, preprocessed
        - batch_size (int): Set to 800 as max as default. But can be adjusted if needed

    Raises:
        - ValueError: if user passes a `batch_size` > 800

    Returns:
        - dictionary (dict): The date period covered by each batch as key, and the actual data covering the period as value. The dictionary also contains a `split_group`
                             list. 
                             When emtpy, then the batch is extracted by filtering all rows with the dates in the `date` key
                             When populated, limit the number of rows of the corresponding date to the value in `split_group`
        
        Example::

                out_dict = {'2023_B000_20230101_20230101_sentinel_batch': {'date': [Timestamp('2023-01-01 00:00:00')], 
                                                                            'split_group': None}, 
                            '2023_B001_20230102_20230102_sentinel_batch': {'date': [Timestamp('2023-01-02 00:00:00')], 
                                                                            'split_group': None}, 
                            '2023_B002_20230103_20230103_sentinel_batch': {'date': [Timestamp('2023-01-03 00:00:00')], 
                                                                            'split_group': [x_start, x_end]}, 
                            '2023_B003_20230103_20230103_sentinel_batch': {'date': [Timestamp('2023-01-03 00:00:00')], 
                                                                            'split_group': [x_start, x_end]}}

    """
    if not isinstance(batch_size, int) or batch_size > 800:
        raise ValueError("Batch size must be an integer <= 800")
    
    df_batches = df_sampled.copy()
    df_batches = df_batches.sort_values('date').reset_index(drop = True)
    # Generate counts for each date object 
    df_batches   = df_batches.groupby('date')['date'].count().reset_index(name = "count")
    batch_num    = 0
    groups_dict  = dict()
    group_buffer = []

    for row in df_batches.itertuples():
        current_group_size = row.count
        date               = row.date   

        # Single group is larger than size limit         
        if current_group_size > batch_size:
            # If there is a batch that had been building, finalise/close that batch
            if group_buffer:
                  batch_dict, batch_num = close_current_batch(group_buffer, batch_num)
                  groups_dict.update(batch_dict)
                  group_buffer = []
            # Split large group into smaller batches
            large_batch_dict, batch_num = split_batch_greater_than_limit(date, current_group_size, batch_size, batch_num)
            groups_dict.update(large_batch_dict)
            continue

        # When the group_buffer surpasses size limit
        if len(group_buffer) + current_group_size > batch_size:
            batch_dict, batch_num = close_current_batch(group_buffer, batch_num)
            groups_dict.update(batch_dict)
            group_buffer = []
        
        # Add new date value
        group_buffer.extend([date]*current_group_size)

    # Cases where the last group was not added to the dict inside the loop
    if group_buffer:
        batch_dict, batch_num = close_current_batch(group_buffer, batch_num)
        groups_dict.update(batch_dict)

    return groups_dict

def sampled_to_batch_dfs(batch_dict: dict, df_sampled: pd.DataFrame):
    """
    The function takes the batch_dict containing the batch name and the dates corresponding to each batch
    It iterates thru the values of the dictionary and filters the data frame to only contain the rows relevant to the batch

    Args:
        - batch_dict (dict): Dictionary containing batch name and the dates correspoding to each batch
        - df_sampled (df): Data frame containing the sampled data, preprocessed

    Retuns:
        - dict: Dictionary cotaining file names as keys and filtered data frames as values 
    """
    df_sampled = df_sampled.sort_values('date').reset_index(drop = True)
    dict_df = dict()
    for k, v in batch_dict.items():
        split_indeces = v.get('split_group', None)
        group_dates   = v.get('date',        None)
        df_filtered   = df_sampled[df_sampled['date'].isin(group_dates)].copy()

        if split_indeces is not None:
            start_i, end_i = split_indeces 
            df_filtered = df_filtered.iloc[start_i:end_i]

        dict_df[k] = df_filtered

    return dict_df 


def fetch_sentinel_data(geom: ee.Geometry, date_str: str) -> np.ndarray: 
    """
    Fetches raw pixels from Google Earth Engine (GEE) into RAM.

    This function does a cloud to RAM rather than to Disk process. It creates a 5-day 
    median composite to mitigate cloud cover and requests a GeoTIFF 
    download URL for a specific 12km grid.

    Args:
        geom_ee (ee.Geometry): The GEE geometry object defining the clip area.
        date_str (str): The target date (YYYY-MM-DD) for the satellite observation.

    Returns:
        numpy.ndarray: A raw 3D array  
        Note: The band order is [B2, B3, B4, B8] (Blue, Green, Red, NIR).

    Raises:
        requests.exceptions.RequestException: If the GEE download URL fails to resolve.
        tifffile.TiffFileError: If the downloaded bytes cannot be parsed as a TIFF.
    """
    pass

def transform_sentinel_data(sentinel_npyarray: np.ndarray):
    """
    Transforms the downloaded raw pixels array into a format that is suitable for CNN processing
    The function replaces all `nan` with `0` values, it organises the order of the bands to `(H, W, 4)`, and resizes the data to 128 x 128

    Args:
        sentinel_npyarray (np.ndarray): Raw 3D pixel array 

    Returns:
        sentinel_npyarray (np.ndarray): resized and transformed numpy array
    """
    pass
