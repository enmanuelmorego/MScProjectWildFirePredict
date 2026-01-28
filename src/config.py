from pathlib import Path
import os

if os.environ.get('RUN_DEMO').upper().strip() == 'ON': 
    # When running demo, the files used will be the demo files inside the project, in GitHub to allow tests and demo
    dir_level = 1
else:
    # The files in GoogleDrive are set in the parent directory from the code
    # Therefore, the code has to go one level above to access the real resources
    dir_level = 2


PROJECT_ROOT = Path(os.environ.get("PROJECT_ROOT",Path(__file__).resolve().parents[dir_level]))
os.environ['DATA_DIR'] =    str(PROJECT_ROOT / "data")
os.environ['MODELS_DIR'] =  str(PROJECT_ROOT / "models")
os.environ['OUTPUTS_DIR'] = str(PROJECT_ROOT / "outputs")

# Set Coordinate Reference System (CRS) so it is uniform across all data inputs
CRS = "EPSG: 4326"

