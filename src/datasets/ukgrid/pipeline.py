import src.datasets.ukgrid.loader as l

from pathlib import Path

def load_ukgrid_main(data_dir: Path, file_name: str, crs: str):

    df_ukgrid = l.load_uk_grid(data_dir, file_name, crs)
    return df_ukgrid

if __name__ == "__main__":
    # python3 -m src.datasets.ukgrid.pipeline
    PROJ_HOME = Path(__file__).resolve().parents[3] 
    data_dir = Path(PROJ_HOME)/"data"

    x = load_ukgrid_main(data_dir, "ukcp18-uk-land-12km.shp", "EPSG: 4326")
    print(x.head())