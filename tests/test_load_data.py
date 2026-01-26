import pandas as pd
from pandas.testing import assert_frame_equal
import load_data as ld

'''
pipenv run pytest
'''

# -------------------------
# VIIRS DATA LOAD PROCESS
# -------------------------
def test_merge_viirs_merges_df_correctly():
    d1 = {'longitude':   [1,            2,             3,           4,            5],
          'latitude':    [10,           11             ,12,         13,           14],
          'acq_date':    ['2024-01-01', '2024-02-02', '2024-03-03', '2024-04-04', '2024-05-05'],
          'another':     [0.1,          0.2,           0.3,         0.4,           0.5]}
    d2 = {'longitude':   [1,            3,            9,            4,            5],
          'latitude':    [10,           11,           12,           20,           14],
          'acq_date':    ['2024-01-01', '2024-02-02', '2025-03-03', '2024-04-04', '2024-05-05'],
          'another':     [0.1,          0.2,           0.3,          0.4,          0.101]}
    de = {'longitude':   [1,            2,             3,           4,            5,             3,           9,            4          ],
          'latitude':    [10,           11             ,12,         13,           14,            11,          12,           20         ],
          'acq_date':    ['2024-01-01', '2024-02-02', '2024-03-03', '2024-04-04', '2024-05-05',  '2024-02-02','2025-03-03', '2024-04-04'],
          'another':     [0.1,          0.2,           0.3,         0.4,           0.5,          0.2,          0.3,          0.4       ]}
    
    test_viirs_data = {'snpp': pd.DataFrame(d1),
                       'noaa': pd.DataFrame(d2)}
    df_test = ld.merge_viirs(test_viirs_data)
    df_expect = pd.DataFrame(de)
    assert_frame_equal(df_expect, df_test.get('df'))
    
