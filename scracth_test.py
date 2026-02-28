import src.pp_sentinel as pse
import pandas as pd


#             - `2020_B002_20200101_20200101_sentinel_batch`
df = pd.DataFrame({'date': ['2023-01-01']* 7})
df['date'] = pd.to_datetime(df['date'])

df_fun = pse.sampled_to_batch(df, 9)
print(df_fun)

