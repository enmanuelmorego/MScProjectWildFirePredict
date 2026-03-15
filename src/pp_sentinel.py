import ee
import numpy as np
import os
from pathlib import Path
import pandas as pd
from typing import Generator
import requests
import tifffile
import io
from skimage.transform import resize
import utils as u
from datetime import datetime 
import re

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

def sampled_to_batch(df_sampled: pd.DataFrame, next_batch_num: int, batch_size: int = 800) -> dict:
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
        - next_batch_num (int): Batch number value to act as the starting point. Takes into account existing batches on disk
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
    batch_num    = next_batch_num
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

def sampled_to_batch_dfs(batch_dict: dict, df_sampled: pd.DataFrame) -> Generator[tuple[str, pd.DataFrame], None, None]:
    """
    The function takes the batch_dict containing the batch name and the dates corresponding to each batch
    It iterates thru the values of the dictionary and filters the data frame to only contain the rows relevant to the batch

    Args:
        - batch_dict (dict): Dictionary containing batch name and the dates correspoding to each batch
        - df_sampled (df): Data frame containing the sampled data, preprocessed

    Yields:
        - batch_name (str): The name of the processed batch
        - df_filtered (df): Filtered data frame meeting the batch requirements

    Note:
        This function yields the results rather tahn returning a dataframe to save memory and keeping computer from freezing
    """
    df_sampled = df_sampled.sort_values('date').reset_index(drop = True)
    for batch_name, batch_df in batch_dict.items():
        split_indeces = batch_df.get('split_group', None)
        group_dates   = batch_df.get('date',        None)
        df_filtered   = df_sampled[df_sampled['date'].isin(group_dates)].copy()

        if split_indeces is not None:
            start_i, end_i = split_indeces 
            df_filtered = df_filtered.iloc[start_i:end_i]

        yield batch_name, df_filtered

def fetch_sentinel_data(geom: ee.Geometry, date_str: str, satelite_params: dict ) -> np.ndarray: 
    """
    Fetches raw pixels from Google Earth Engine (GEE) into RAM.

    Retrieves an ImageCollection filtered by location and a 6-day window (target date and -5 days to target).
    It computes a median composite to mitigate the impact of cloud cover and other noise before downloading as GeoTIFF
    
    Args:
        geom (ee.Geometry): The GEE geometry object defining the clip area
        date_str (str): The target date (YYYY-MM-DD) for the satellite observation
        satelite_params (dict): Dictionary containingthe various parameters specifying the specific values for fetching the correct satelite images
                                
                                Note:
                                   All the parameters specifying the details of the satelite images are passed via a dictionary. However, if any of these parameters are emtpy, 
                                   the function will provide the default values instead 

    Returns:
        numpy.ndarray: A raw 3D array  
        Note: The band order is [B2, B3, B4, B8] (Blue, Green, Red, NIR)

    Raises:
        requests.exceptions.RequestException: If the GEE download URL fails to resolve
        tifffile.TiffFileError: If the downloaded bytes cannot be parsed as a TIFF
    """
    # Extract satelite objects
    #TODO remove default values as this is dangerous to code here due to changing updates
    satelite_img    = satelite_params.get('satelite_img',    "COPERNICUS/S2_SR_HARMONIZED")
    satelite_bands  = satelite_params.get('satelite_bands',  ["B2","B3","B4","B8"])
    satelite_scale  = satelite_params.get('satelite_scale',  80)
    satelite_format = satelite_params.get('satelite_format', 'GEO_TIFF')
    crs             = satelite_params.get('crs',             'EPSG:4326').replace(" ", "")

    # Get satelite img object
    img      = (ee.ImageCollection(satelite_img)
                .filterBounds(geom)
                .filterDate(ee.Date(date_str).advance(-5, 'day'),
                            ee.Date(date_str).advance( 1, 'day'))
                            .select(satelite_bands)
                            .median()
                            .clip(geom)) 
    url      = img.getDownloadURL({'scale' : satelite_scale,
                                   'crs'   : crs.replace(" ",""),
                                   'region': geom,
                                   'format': satelite_format})
    response = requests.get(url, timeout = 30)
    response.raise_for_status()

    with io.BytesIO(response.content) as f:
        return tifffile.imread(f)

def transform_sentinel_data(sentinel_npyarray: np.ndarray) -> np.ndarray:
    """
    Transforms the downloaded raw pixels array into a format that is suitable for CNN processing
    The function replaces all `nan` with `0` values, it organises the order of the bands to `(H, W, 4)`, and resizes the data to 128 x 128

    Args:
        sentinel_npyarray (np.ndarray): Raw 3D pixel array 

    Returns:
        sentinel_npyarray (np.ndarray): resized and transformed numpy array
    """
    pixel_data = np.nan_to_num(sentinel_npyarray, nan = 0.0)
    # Adjust axis: Expected format (H, W, 4)
    if pixel_data.shape[0] == 4:
        pixel_data = np.moveaxis(pixel_data, 0, -1)
    elif pixel_data.shape[1] == 4:
        pixel_data = np.moveaxis(pixel_data, 1, -1)
    # Resize data
    pixel_data_resized = resize(pixel_data, (128,128), anti_aliasing = True).astype('float32')
    return pixel_data_resized

def save_sentinel_nps(image_list: list, label_list: list, composite_key_list: list, batch_name: str) -> None:

    x     = np.array(image_list)
    y     = np.array(label_list)
    ids   = np.array(composite_key_list)
    fname = f"{batch_name}.npz"
    fout  = Path(os.environ.get('DATA_DIR'))/ 'Sentinel2'/fname
    np.savez_compressed(fout, x=x, y=y, composite_key=ids)
    print(f"\n\t 🎉 Success! Saved {fname} ({x.nbytes / 1e6:.2f}")

def fetch_available_sentinel_files(data_folder: str = "Sentinel2", file_extension: str = ".npz") -> list:
    """
    Function that finds all available `np` sentinel data in local disk
    Arguments are provided, but populated with default values 

    Args:
        - data_folder(str = Sentinel2): Folder name of the location where the Sentinel2 data is stored
        - file_extension(str = .npz): File extension to identify the relevany file types

    Returns:
        - list: List containing the full file paths of all available sentinel files
        
    """
    # Get the full file names from directory
    files = u.get_filepaths(data_folder)
    # Keep only the relevant file types
    files = [f for f in files if re.search(file_extension, str(f)) is not None]
    return files

def load_sentinel_composite_keys(sentinel_files: list) -> pd.DataFrame:
    """
    Function that loads all the composite keys for the availabel Sentinel2 images in disk
    as a single column dataframe

    Args:
        - sentinel_files(list): A list containing the full paths of all available Sentinel2 files

    Returns:
        - df (pd.DataFrame): A data frame containing one column, composite_key, and all the available values from files 
    """
    sentinel_data_list = []
    for f in sentinel_files:
        data = np.load(f)
        sentinel_data_list.append(data['composite_key'])

    combined_ids = np.concatenate(sentinel_data_list)
    df           = pd.DataFrame(combined_ids, columns = ['composite_key'])
    return df

def find_required_sentinel_from_sampled(df_sampled: pd.DataFrame, sentinel_composite_key: pd.DataFrame) -> pd.DataFrame:
    """
    Function that takes the sampled data frame and the available Sentinel2 Composite keys
    It finds all the values in the sampled dataframe not covered by the existing Sentinel2 data
    and returns the data frame with only the rows that require Sentinel2 data download

    Args:
        - df_sampled (pd.DataFrame): Sampled data frame
        - sentinel_composite_key (pd.DataFrame): Dataframe containing all available composite_keys in Sentinel2 local data

    Returns:
        - df (pd.DataFrame): A copy of df_sampled containing only the rows of data not currently existing in Sentinel2 local data
    """
    df_samp                  = df_sampled.copy()
    df_sent                  = sentinel_composite_key.copy()
    df_samp['composite_key'] = df_samp['composite_key'].astype(str)
    df_sent['composite_key'] = df_sent['composite_key'].astype(str)

    df_pending         = df_samp.merge(df_sent, on = 'composite_key', how = 'left', indicator = True)
    df_pending         = df_pending[df_pending['_merge'] == 'left_only']
    df_pending         = df_pending.drop(columns = ['_merge'])
    df_pending['date'] = pd.to_datetime(df_pending['date'])
    df_pending         = df_pending.sort_values(by = ['date', 'grid_id']).reset_index(drop = True)

    return df_pending

def required_sentinel_pipeline(df_sampled):
    """
    Wrapper function to find the rows that require sentinel2 download based on the input sampled data
    """
    sentinel_available   = fetch_available_sentinel_files()
    if not sentinel_available:
        # Return df_sampled as all are required
        df_sampled['date'] = pd.to_datetime(df_sampled['date'])
        df_sampled = df_sampled.sort_values(by = ['date', 'grid_id']).reset_index(drop = True)
        return df_sampled
    sentinel_comp_keys   = load_sentinel_composite_keys(sentinel_available)
    df_sentinel_required = find_required_sentinel_from_sampled(df_sampled, sentinel_comp_keys)
    return df_sentinel_required

def fetch_max_batch_num():
    """
    Function that fetches the max batch number existing on disk
    If there is no files available, then the function returns 1 to be used as the first batch, 
    Else, +1 is added to the latest existing batch to avoid duplication of batches

    Returns:
        int: An integer, representing the max batch number value + 1, as this will be the starting value for the next batch
    """
    files     = fetch_available_sentinel_files()
    max_batch = 0
    for f in files:
        batch_str = re.search(r"[B]\d{3}", str(f)).group()
        batch_int = int(batch_str[1:])
        if batch_int > max_batch:
            max_batch = batch_int
    max_batch = int(max_batch) + 1
    return max_batch 

def sentinel_download_pipeline(df: pd.DataFrame, gee_proj_name: str, sentinel_params: dict, batch_size: int = 800) -> None:
    """
    Pipeline to fetch, download and save sentinel pixels as numpy arrays
    """
    try:
        ee.Initialize(project = gee_proj_name)
    except:
        ee.Authenticate()
        ee.Initialize(project = gee_proj_name)
    sentinel_max_batch_num = fetch_max_batch_num()
    sentinel_batches       = sampled_to_batch(df, sentinel_max_batch_num, batch_size)

    for batch_name, batch_df in sampled_to_batch_dfs(sentinel_batches, df):
        print("-"*80)
        print(f"\t📦 STARTING BATCH: {batch_name}")
        # Generate objects per batch
        image_list, label_list, composite_key_list = [], [], []

        for row in batch_df.itertuples():
            i = row.Index
            try:
                geom          = ee.Geometry(row.geometry.__geo_interface__)
                date          = row.date
                fire_lbl      = row.fire_lbl
                composite_key = row.composite_key  
                # Fetch sentinel data
                sentinel_data = fetch_sentinel_data(geom, date, sentinel_params)
                sentinel_data = transform_sentinel_data(sentinel_data)
                # Generate objects to save
                image_list.append(sentinel_data)
                label_list.append(fire_lbl)
                composite_key_list.append(composite_key)
                print(f"\t✅ Downloaded & Resized {i+1}: sentinel_data.shape")
            except Exception as e:
                print(f"\t❌ Error on row {i}: {e}")
        # Save batch as npz file
        save_sentinel_nps(image_list, label_list, composite_key_list, batch_name)
