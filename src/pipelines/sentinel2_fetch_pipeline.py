import ee
import pandas as pd
import transforms.sentinel2_transforms as st
import data_io.sentinel2_io as sio
from typing import Any

def request_sentinel2_data(df_sampled: pd.DataFrame, dict_batches: dict, parameters: dict):

    gee_proj_name = parameters["GEE_PROJECT"]
    data_dir      = parameters['DATA_DIR']
    logs_dir      = data_dir / "outputs" / "logs"
    try:
        ee.Initialize(project = gee_proj_name)
    except:
        ee.Authenticate()
        ee.Initialize(project = gee_proj_name)

    for batch_name, batch_df in st.sampled_to_batch_dfs(dict_batches, df_sampled):
        print("-"*80)
        print(f"\t📦 STARTING BATCH: {batch_name}")
        # Initialise objects for batch
        image_list, label_list, composite_key_list = [], [], []
        # Initiliase list to save composite keys with no image(s) found
        missing_keys = []
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
                    missing_keys.append(composite_key)
                    continue
                # Generate objects to save
                image_list.append(sentinel_data)
                label_list.append(fire_lbl)
                composite_key_list.append(composite_key)
                print(f"\t✅ Downloaded & Resized {i+1}: sentinel_data.shape")
            except Exception as e:
                print(f"\t❌ Error on row {i}: {e}")
        # Log missing composite_keys
        if len(missing_keys) > 0:
            log_missing_composite_keys(batch_name_in   = batch_name,
                                       missing_keys_in = missing_keys,
                                       log_dir_in      = logs_dir)
        # Log batch statistics
        log_sentinel_batch_stats(batch_name_in = batch_name,
                                 batch_data_in = image_list,
                                 log_dir_in    = logs_dir)
        # Prevent saving empty batches
        if len(image_list) == 0:
            print(f"\t⚠️ Skipping batch {batch_name}: no images downloaded")
            continue
        # Save batch as npz file
        sio.save_sentinel_nps(image_list, label_list, composite_key_list, batch_name, data_dir)
        