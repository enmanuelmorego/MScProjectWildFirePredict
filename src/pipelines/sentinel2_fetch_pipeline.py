import ee
import pandas as pd
import transforms.sentinel2_transforms as st
import data_io.sentinel2_io as sio
from typing import Any

def request_sentinel2_data(df_sampled: pd.DataFrame, dict_batches: dict, parameters: dict):

    gee_proj_name = parameters["GEE_PORJ_NAME"]
    data_dir      = parameters['DATA_DIR']
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
                # Generate objects to save
                image_list.append(sentinel_data)
                label_list.append(fire_lbl)
                composite_key_list.append(composite_key)
                print(f"\t✅ Downloaded & Resized {i+1}: sentinel_data.shape")
            except Exception as e:
                print(f"\t❌ Error on row {i}: {e}")
        # Save batch as npz file
        sio.save_sentinel_nps(image_list, label_list, composite_key_list, batch_name, data_dir)
        