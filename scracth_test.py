import pp_sentinel as psent
import pandas as pd

df = pd.DataFrame({'date': ['2025-01-01','2023-02-12','2025-01-01','2023-10-11','2025-01-01']})
df['date']  = pd.to_datetime(df['date'])
dict_expect = {"2023_B000_20230212_20231011_sentinel_batch": {'date': [pd.Timestamp('2023-02-12'),pd.Timestamp('2023-10-11')],'split_group': None},
                "2025_B001_20250101_20250101_sentinel_batch": {'date': [pd.Timestamp('2025-01-01')],'split_group': [0, 2]},
                "2025_B002_20250101_20250101_sentinel_batch": {'date': [pd.Timestamp('2025-01-01')],'split_group': [2,4]}}
                
                
dict_test = psent.sampled_to_batch(df, 2)
print(dict_test)
#             - `2020_B002_20200101_20200101_sentinel_batch`

# df = pd.DataFrame({'date': ['2023-01-01','2023-01-01','2023-01-01',
#                                 '2023-02-01','2023-02-01','2023-02-01','2023-02-01',
#                                 '2023-03-01','2023-02-02','2023-02-02'],
#                     'id_val': [1,2,3,4,5,6,7,8,9,10]})
# df['date'] = pd.to_datetime(df['date'])

# dict_test = psent.sampled_to_batch(df, 2)
# dict_test
# print(dict_test)

# for k, v in dict_test.items():
#     print("*"*80)
#     print(k)
#     for ki, vi in v.items():
#         print(f"\t{ki}:{vi}")

# dict_sampled = psent.sampled_to_batch_dfs(dict_test, df)
# for k, v in dict_sampled.items():
#     print("." *80)
#     print(k)
#     print(v.head())


