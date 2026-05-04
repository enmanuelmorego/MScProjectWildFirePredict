import src.utils.file_utils as fu
import src.data.viirs.

# Temp
import os
from pathlib import Path
os.environ.setdefault("DATA_DIR", str(Path(__file__).resolve().parents[3] / "data"))
# temp

def load_viirs_main():
    viirs_files = fu.get_filepaths('VIIRS', "csv")
    viirs_to_load    = to_load_viirs(viirs_files,date_range)

    print(f"Found {len(viirs_files)} files") 
    for i in viirs_files:
        print(i)

if __name__ == "__main__":

    load_viirs_main()
