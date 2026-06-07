import ee
import pandas as pd
import transforms.sentinel2_transforms as st

def request_sentinel2_data(df_sampled: pd.DataFrame, dict_batches: dict, gee_proj_name: str):
    try:
        ee.Initialize(project = gee_proj_name)
    except:
        ee.Authenticate()
        ee.Initialize(project = gee_proj_name)

    for batch_name, batch_df in st.sampled_to_batch_dfs(dict_batches, df_sampled):
        print(batch_name)
        