import utils.file_utils as fu
from pathlib import Path

markdown = f"""
# MScProjectWildFirePredict Architecture

The project is divided into modules, which have specific responsibilities. An overview of the modules is shown here, and below, each of the sections is expanded with further details

## Overview
```
| MScProjectWildFirePredict/
{fu.build_dir_tree(Path(Path(__file__).resolve().parents[2]), False)}
```

## Codebase
```
MScProjectWildFirePredict/
| src/
{fu.build_dir_tree(Path("src"), False)}
```
"""