import src.utils.file_utils as fu
import loaders.fwi_loader as l

from pathlib import Path

def load_fwi_main(data_dir: Path, requested_years: list[int], dir_name: str = "FWI"):
    fwi_csv_files  = fu.get_filepaths(data_dir, dir_name, "csv")
    fwi_grib_files = fu.get_filepaths(data_dir, dir_name, "grib")
    fwi_files      = l.select_fwi_files(fwi_csv_files, fwi_grib_files, requested_years)

    return fwi_files


if __name__ == "__main__":
    # python3 -m src.datasets.fwi.pipeline
    year = [2019,2020,2017]
    ddir = Path(__file__).resolve().parents[3]
    ddir = ddir / 'data'
    x = load_fwi_main(ddir, year)
    print(x)

    