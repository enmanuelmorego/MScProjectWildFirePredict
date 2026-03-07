import pandas as pd
import utils as u

def test_split_df_by_year_same_columns():
  df_test     = pd.DataFrame({'date': pd.to_datetime(['2025-01-01', '2026-01-01', '2027-01-01', '2027-01-01']),
                              'name': ['A','B','C','D']})
  dict_test   = u.split_df_by_year(df_test)
  cols_expect = ['date', 'name']

  for _, v in dict_test.items():
    assert list(v.columns) == cols_expect
