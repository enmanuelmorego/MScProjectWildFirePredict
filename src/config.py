from pathlib import Path
import os

PROJECT_ROOT = Path(
    os.environ.get(
        "PROJECT_ROOT",
        Path(__file__).resolve().parents[2]
    )
)

DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
