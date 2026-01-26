# --------------------------
# SET UP
# --------------------------
import os
os.environ.setdefault("RUN_DEMO", "ON")
import src.config as c
import src.load_data as ld

# --------------------------
# VIIRS DATA
# --------------------------
viirs_dict = ld.viirs_load_pipeline(dir_name = 'VIIRS',
                                    date_range = [2019,2020])
df_viirs = viirs_dict.get('df_viirs')
print(df_viirs.head())
