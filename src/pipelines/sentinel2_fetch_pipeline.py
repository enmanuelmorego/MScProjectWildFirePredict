from concurrent.futures import ThreadPoolExecutor
import ee
import pandas as pd
import transforms.sentinel2_transforms as st
import data_io.sentinel2_io as sio
import utils.file_utils as fu
import time


def request_sentinel2_data(df_sampled: pd.DataFrame, dict_batches: dict, parameters: dict) -> None:

    tstart        = time.perf_counter()
    gee_proj_name = parameters["GEE_PROJECT"]
    proj_home     = parameters['PROJ_HOME']
    data_dir      = parameters['DATA_DIR']
    run_timestamp = parameters['RUN_TIMESTAMP']
    logs_dir      = proj_home / "outputs" / "logs"
    
    # Initiliase list to save composite keys with no image(s) found
    missing_composite_keys = []
    batch_statistics       = []
    try:
        ee.Initialize(project = gee_proj_name)
    except:
        ee.Authenticate()
        ee.Initialize(project = gee_proj_name)

    for batch_name, batch_df in st.sampled_to_batch_dfs(dict_batches, df_sampled):
        batch_size = batch_df.shape[0]
        print("-"*80)
        print(f"\t📦 STARTING BATCH: {batch_name} [SIZE]: {batch_size}")
        # Initialise objects for batch
        image_list, label_list, composite_key_list = [], [], []

        with ThreadPoolExecutor(max_workers = 6) as executor:
            sentinel2_results = executor.map(lambda row: sio.fetch_sentinel_data_observation(row, batch_name, run_timestamp, parameters),
                                             batch_df.itertuples())
        for d in sentinel2_results:
            if d['success']:
                image_list.append(d["image"])
                label_list.append(d["fire_lbl"])
                composite_key_list.append(d["composite_key"])
            else:
                missing_composite_keys.append(d)

        batch_statistics.append({"date": run_timestamp,
                                 "batch": batch_name,
                                 "n_requested": batch_size,
                                 "n_fetched": len(image_list)})
        if len(image_list) == 0:
            print(f"⚠️ 0 images found for batch {batch_name}")
            continue
            
        # Save batch as npz file
        sio.save_sentinel_nps(image_list, label_list, composite_key_list, batch_name, data_dir)
    if len(missing_composite_keys) > 0:
        # Create df to write to csv for missing composite keys
        df_missing_composite_keys =  pd.DataFrame(missing_composite_keys)
        fu.write_df_to_csv(df_missing_composite_keys, logs_dir, f"{run_timestamp}_missing_sentinel2_images")
    # Create df to write to csv for batch statics
    df_batch_statistics       = pd.DataFrame(batch_statistics)
    fu.write_df_to_csv(df_batch_statistics, logs_dir, f"{run_timestamp}_sentinel2_download_stats")

    tend     = time.perf_counter()
    duration = tend - tstart
    print("=======================")
    print(f"Total Duration: {duration//60}mins {duration%60}secs")




        