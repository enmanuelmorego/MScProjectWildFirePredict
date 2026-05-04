
import loaders.fwi_loader as l
import transforms.fwi_transforms as t

from pathlib import Path

import geopandas as gpd

def load_fwi_main(df_uk_grid_in: gpd.GeoDataFrame, data_dir: Path, requested_years: list[int], grb_name: str, crs: str, dir_name: str = "FWI"):

    fwi_path  = Path(data_dir)/dir_name
    fwi_files = l.fwi_file_availability_wrapper(data_dir, requested_years, dir_name)

    # 1. Check if any files are required from CEMS API
    fetch_from_api = fwi_files['required_years']
    if fetch_from_api:
        l.fwi_fetch_from_api(fetch_from_api, fwi_path)
        # Refresh requirements to include newly downloaded data
        fwi_files = l.fwi_file_availability_wrapper(data_dir, requested_years, dir_name)

    # 2. If Grib file needs to be transformed to csv
    grib_to_csv = fwi_files['available_grib']
    if grib_to_csv:
        for g in grib_to_csv:
            t.transform_grib_to_csv(fwi_path = fwi_path, grib_fname = g, grb_name = grb_name, df_uk_grid = df_uk_grid_in, crs_val = crs)
        # Refresh requirements to include newly transformed data
        fwi_files = l.fwi_file_availability_wrapper(data_dir, requested_years, dir_name)

    # 3. Load csv data
    fwi_csv_files = fwi_files['available_csv']
    df_fwi        = l.fwi_load_csv_files(fwi_csv_files, fwi_path)

    return df_fwi


if __name__ == "__main__":
    # python3 -m src.pipelines.fwi_pipeline
    year = [2019,2020,2017]
    ddir = Path(__file__).resolve().parents[2]


    