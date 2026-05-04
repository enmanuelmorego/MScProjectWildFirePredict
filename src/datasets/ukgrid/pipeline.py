import src.datasets.ukgrid.loader as l
from pathlib import Path
import pandas as pd
import geopandas as gpd

def load_ukgrid_main(df_days_in: pd.DataFrame, data_dir: Path, file_name: str, crs: str) -> dict[str, gpd.GeoDataFrame]:

    df_ukgrid                 = l.load_uk_grid(data_dir, file_name, crs)
    df_daily_grid             = df_ukgrid.copy()
    df_daily_grid['join_key'] = 1
    df_daily_grid             = df_daily_grid.merge(df_days_in, on='join_key').drop(columns='join_key')
    return {'df_ukgrid'   : df_ukgrid,
            'df_daily_grid': df_daily_grid}
