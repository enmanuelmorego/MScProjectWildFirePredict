import pandas as pd
import utils as u

def test_split_df_by_year_same_columns():
  df_test     = pd.DataFrame({'date': pd.to_datetime(['2025-01-01', '2026-01-01', '2027-01-01', '2027-01-01']),
                              'name': ['A','B','C','D']})
  dict_test   = u.split_df_by_year(df_test)
  cols_expect = ['date', 'name']

  for _, v in dict_test.items():
    assert list(v.columns) == cols_expect

def test_split_df_by_year_correct_yearsplit():
  df_test     = pd.DataFrame({'date': pd.to_datetime(['2025-01-01', '2026-01-01', '2027-01-01', '2027-01-01']),
                              'name': ['A','B','C','D']})
  dict_test   = u.split_df_by_year(df_test)
  keys_expect = ['2025', '2026', '2027']
  dict_keys   = sorted([k for k, _ in dict_test.items()])
  assert dict_keys == keys_expect

def test_split_df_by_year_correct_df_dimensions():
  df_test     = pd.DataFrame({'date': pd.to_datetime(['2025-01-01', '2026-01-01', '2027-01-01', '2027-01-01']),
                              'name': ['A','B','C','D']})
  dict_test   = u.split_df_by_year(df_test)
  shape_expect = {'2025': (1,2),'2026': (1,2), '2027': (2,2)}
  for k, v in dict_test.items():
    assert v.shape == shape_expect.get(k)