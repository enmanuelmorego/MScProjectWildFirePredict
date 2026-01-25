from pathlib import Path
import os

if os.environ.get('RUN_DEMO').upper().strip() == 'ON': 
    # When running demo, the files used will be the demo files inside the project, in GitHub to allow tests and demo
    dir_level = 1
else:
    # The files in GoogleDriv