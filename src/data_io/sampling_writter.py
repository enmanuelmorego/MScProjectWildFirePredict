"""
Module to encapsulate functions to write sampling files to disk
"""
import pandas as pd 
from pathlib import Path
import os 
def write_sampled_pre_sentinel(df_sampled_in: pd.DataFrame, 
                               data_dir     : Path,
                               tgt_dir      : str = "SampledFireNoFire",
                               file_name    : str = "sampled_firenofire") -> None:

    """
    Takes sampled data (pre sentinel download) and writes .csv files to disk
    Data is split by year
    """
    # Get years in sampled_df
    years = df_sampled_in['date'].dt.year.unique()
    # Create output dir - if missing
    output_dir = data_dir / tgt_dir
    os.makedirs(output_dir, exist_ok = True)

    for year in years:
        fname = f"{year}_{file_name}.csv"
        fout  = output_dir/fname
        # Subset dataset
        df_out = df_sampled_in[df_sampled_in['date'].dt.year == year]
        # Write file 
        df_out.to_csv(fout, index = False)
