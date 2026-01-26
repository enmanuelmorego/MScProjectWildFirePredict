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

viirs_dict = ld.viirs_load_pipeline(dir_name = 'VIIRS',
                                    date_range = [2019,2020])

df_viirs = viirs_dict.get('df_viirs')
print(df_viirs.head())
