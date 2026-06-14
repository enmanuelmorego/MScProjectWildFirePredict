import ee
import pandas as pd
import transforms.sentinel2_transforms as st
import data_io.sentinel2_io as sio
import utils.file_utils as fu
from typing import Any


def request_sentinel2_data(df_sampled: pd.DataFrame, dict_batches: dict, parameters: dict):

    gee_proj_name = parameters["GEE_PROJECT"]
    data_dir      = parameters['DATA_DIR']
    run_timestamp = parameters['RUN_TIMESTAMP']
    logs_dir      = data_dir / "outputs" / "logs"
    
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
        for row in batch_df.itertuples():
            row: Any
            i = row.Index
            try:
                geom          = ee.Geometry(row.geometry.__geo_interface__)
                date          = row.date
                fire_lbl      = row.fire_lbl
                composite_key = row.composite_key
                # Request Sentinel data
                sentinel_data = sio.fetch_sentinel_data(geom, date, parameters)
                sentinel_data = st.transform_sentinel_data(sentinel_data)
                # Check that image was found
                if sentinel_data.size == 0:
                    print(f"⚠️ No sentinel2 data found for {composite_key}")
                    missing_composite_keys.append({"date": run_timestamp,
                                                   "batch": batch_name,
                                                   "composite_key": composite_key,
                                                   "missing_sentinel2_data": True})
                    continue
                # Generate objects to save
                image_list.append(sentinel_data)
                label_list.append(fire_lbl)
                composite_key_list.append(composite_key)
                print(f"\t✅ Downloaded & Resized {i+1}: sentinel_data.shape")
            except Exception as e:
                print(f"\t❌ Error on row {i}: {e}")
        # Generate batch statistics 
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




        