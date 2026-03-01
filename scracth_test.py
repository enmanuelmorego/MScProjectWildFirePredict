import pp_sentinel as psent
import pandas as pd


#             - `2020_B002_20200101_20200101_sentinel_batch`

df = pd.DataFrame({'date': ['2025-01-01','2023-02-12','2025-01-01','2023-10-11','2025-01-01']})
df['date'] = pd.to_datetime(df['date'])
dict_expect = {"2023_B000_20250101_20250101_sentinel_batch": [pd.Timestamp('2023-01-01')] ,
               "2023_B001_20250102_20250102_sentinel_batch": [pd.Timestamp('2023-01-02')] }
dict_test = psent.sampled_to_batch(df, 2)
dict_test
print(dict_test)

for k, v in dict_test.items():
    print("*"*80)
    print(k)
    for ki, vi in v.items():
        print(f"\t{ki}:{vi}")


