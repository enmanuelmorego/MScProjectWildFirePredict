import src.utils.file_utils as fu
import src.datasets.viirs.loader as l
import src.datasets.viirs.transforms as t

# Temp
import os
from pathlib import Path
os.environ.setdefault("DATA_DIR", str(Path(__file__).resolve().parents[3] / "data"))
# temp

def load_viirs_main(years_to_load: list[int]):
    viirs_files     = fu.get_filepaths('VIIRS', "csv")
    viirs_to_load   = l.select_viirs_files(viirs_files, years_to_load)
    viirs_data      = l.load_viirs(viirs_to_load)
    df_viirs_raw    = t.merge_viirs(viirs_data)
    df_viirs_report = df_viirs_raw['data_report']
    df_viirs_temp   = df_viirs_raw['df']
  
    df_viirs         = filter_viirs(df_viirs_temp)
    df_viirs         = df_viirs.rename(columns = {'acq_date': 'date'})
    df_viirs["date"] = pd.to_datetime(df_viirs["date"])
    df_viirs_geo     = geo_viirs(df_viirs, crs)
    return {'df_viirs': df_viirs_geo,
            'data_report': df_viirs_report}

    return df_viirs_raw
    # print(f"Found {len(viirs_to_load)} files") 
    # for i in viirs_to_load:
    #     print(i)

if __name__ == "__main__":
    # python3 -m src.datasets.viirs.pipeline
    years = []
    print(load_viirs_main(years).keys())
