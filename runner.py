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

viirs_files =   ld.get_filepaths('VIIRS')
viirs_to_load = ld.to_load_viirs(viirs_files,[2019,2020])
viirs_data =    ld.load_viirs(viirs_to_load)
df_viirs =      ld.merge_viirs(viirs_data)

print(df_viirs.get('data_report'))
