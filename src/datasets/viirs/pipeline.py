import src.utils.file_utils as fu
import src.datasets.viirs.loader as l

# Temp
import os
from pathlib import Path
os.environ.setdefault("DATA_DIR", str(Path(__file__).resolve().parents[3] / "data"))
# temp

def load_viirs_main(years_to_load: list[int]):
    viirs_files   = fu.get_filepaths('VIIRS', "csv")
    viirs_to_load = l.select_viirs_files(viirs_files, years_to_load)

    print(f"Found {len(viirs_to_load)} files") 
    for i in viirs_to_load:
        print(i)

if __name__ == "__main__":
    # python3 -m src.datasets.viirs.pipeline
    years = []
    load_viirs_main(years)
