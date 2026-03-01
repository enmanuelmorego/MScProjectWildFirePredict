import pp_sentinel as psent
import pandas as pd

df = pd.DataFrame({'date': pd.to_datetime(['2023-05-15','2023-05-15',
                                            '2023-05-05','2023-05-05','2023-05-06','2023-05-06']),
                    'id':                  ['a','b',
                                            'c','d','e','f']})

batch_dict = psent.sampled_to_batch(df, 4)
test_dict  = psent.sampled_to_batch_dfs(batch_dict, df)
print(list(test_dict["2023_B000_20230505_20230506_sentinel_batch"]['date']) )
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


