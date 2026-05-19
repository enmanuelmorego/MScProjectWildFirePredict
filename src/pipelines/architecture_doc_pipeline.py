from utils.architecture_builder import markdown
from pathlib import Path


folder = Path(__file__).resolve().parents[2]
fout = folder/"AutoArchitecture.md"

with open("AutoArchitecture.md", "w") as f:
    f.write(markdown)