import src.utils.file_utils as fu
import loaders.fwi_loader as l

from pathlib import Path

def load_fwi_main(data_dir: Path, requested_years: list[int], dir_name: str = "FWI"):
    fwi_csv_files  = fu.get_filepaths(data_dir, dir_name, "csv")
    fwi_grib_files = fu.get_filepaths(data_dir, dir_name, "grib")
    fwi_files      = l.select_fwi_files(fwi_csv_files, fwi_grib_files, requested_years)

    # 1. Check if any files are required from CEMS API
    fetch_from_api = fwi_files['required_years']
    if fetch_from_api:
        print("\t📈 Fetching FWI data from CDS API...")
        fetch_fwi_api(fetch_from_api, fwi_path)
        # Refresh requirements to include newly downloaded data
        fwi_files = os.listdir(fwi_path)
        requirements = check_drive_fwi(df_uk_daily_grid, fwi_files)
    
    # 2. If Grib file needs to be transformed to csv
    grib_to_csv = requirements['available_grib']
    if grib_to_csv:
        print("\t➡️ Transforming .grib to .csv...")
        for g in grib_to_csv:
        transform_grib_to_csv(fwi_path   = fwi_path, 
                                grib_fname = g,
                                grb_name   = grb_name,
                                df_uk_grid = df_uk_grid,
                                crs_val    = crs)
        # Refresh requirements to include newly transformed data
        fwi_files = os.listdir(fwi_path)
        requirements = check_drive_fwi(df_uk_daily_grid, fwi_files)

    # 3. Load csv data
    fwi_csv_files = requirements['available_csv']
    # Initialise object to store data
    fwi_list = []
    for f in fwi_csv_files:
        fname_load = Path(fwi_path)/f
        df_load = pd.read_csv(fname_load)
        fwi_list.append(df_load)
    df_fwi = pd.concat(fwi_list, ignore_index = True)
    df_fwi["date"] = pd.to_datetime(df_fwi["date"])
    return df_fwi

        return fwi_files


if __name__ == "__main__":
    # python3 -m src.pipelines.fwi_pipeline
    year = [2019,2020,2017]
    ddir = Path(__file__).resolve().parents[2]
    ddir = ddir / 'data'
    x = load_fwi_main(ddir, year)
    print(x)

    