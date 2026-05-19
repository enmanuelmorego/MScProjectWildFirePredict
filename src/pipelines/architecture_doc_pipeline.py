from utils.architecture_builder import markdown
from utils.file_utils import open_file
from pathlib import Path

"""
To make changes to the content of the .md file, open `src/utils/architecture_builder.py`
"""

folder = Path(__file__).resolve().parents[2]
fout = folder/"Project Structure.md"

with open(fout, "w") as f:
    f.write(markdown)
open_file(fout)