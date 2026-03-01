import src.pp_sentinel as pse
import pandas as pd


#             - `2020_B002_20200101_20200101_sentinel_batch`
df = pd.DataFrame({'date': ['2023-01-01','2023-01-01','2023-01-01',
                            '2023-01-02','2023-01-02','2023-01-02','2023-01-02','2023-01-02']})
df['date'] = pd.to_datetime(df['date'])

df_fun = pse.sampled_to_batch(df, 2)
print(df_fun.keys())
for k, v in df_fun.items():
    print("*"*80)
    print(k)
    for i in v:
        print(f"\t{i}")
