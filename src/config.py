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
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"



