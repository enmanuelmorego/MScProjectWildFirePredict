import os

# MUST be first
os.environ.setdefault("RUN_DEMO", "ON")

print("🏁 Running the program has started!! ")

import src.config as c
print("🔎 PROJECT_ROOT:")
print(f"\t{c.PROJECT_ROOT}")

print("🔎 DATA DIRECTORY:")
print(f"\t{os.environ.get('DATA_DIR')}")

import src.load_data as ld

viirs_files =     ld.get_filepaths('VIIRS')
viirs_to_load =   ld.to_load_viirs(viirs_files,[2019,2020])
viirs_data =      ld.load_viirs(viirs_to_load)
df_viirs_raw =    ld.merge_viirs(viirs_data)
df_viirs_report = df_viirs_raw.get('data_report')
df_viirs_temp =   df_viirs_raw.get('df')
df_viirs =        ld.filter_viirs(df_viirs_temp)
print(df_viirs.head())
