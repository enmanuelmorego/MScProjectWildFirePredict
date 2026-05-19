import utils.file_utils as fu
import data_io.viirs_loader as l
import transforms.viirs_transforms as t

import pandas as pd
import geopandas as gpd
from typing import TypedDict
from pathlib import Path


# Pre define complex dictionaries type hints
class ViirsPipelineOutput(TypedDict):
    df_viirs: gpd.GeoDataFrame
    data_report: dict | None

def load_viirs_main(years_to_load: list[int], data_dir: Path, crs: str, dir_name: str = "VIIRS", file_extension:str = "csv") -> ViirsPipelineOutput:
    viirs_files       = fu.get_filepaths(data_dir, dir_name, file_extension)
    viirs_to_load     = l.select_viirs_files(viirs_files, years_to_load)
    viirs_data        = l.load_viirs(viirs_to_load)
    df_viirs_raw      = t.merge_viirs(viirs_data)
    dict_viirs_report = df_viirs_raw['data_report']
    df_viirs_temp     = df_viirs_raw['df']
    df_viirs          = t.filter_viirs(df_viirs_temp)
    df_viirs          = df_viirs.rename(columns = {'acq_date': 'date'})
    df_viirs["date"]  = pd.to_datetime(df_viirs["date"])
    df_viirs_geo      = t.transform_to_geo_viirs(df_viirs, crs)
    return {'df_viirs'   : df_viirs_geo,
            'data_report': dict_viirs_report}

if __name__ == "__main__":
    # Use this to run: python3 -m src.datasets.viirs.pipeline
    from pathlib import Path
    years = [2018]
    crs = "EPSG: 4326" 
    ddir = Path(__file__).resolve().parents[3]
    ddir = ddir / 'data'
    output = load_viirs_main(years, ddir, crs)
    print(output.get('data_report'))
    df_v = output.get('df_viirs')
    print(df_v.shape)