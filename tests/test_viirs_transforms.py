import pandas as pd 
import geopandas as gpd
import transforms.viirs_transforms as vt

from pandas.testing import assert_frame_equal


def test_merge_viirs_merges_df_correctly():
    d1 = pd.DataFrame(
        {'longitude':   [1,            2,             3,           4,            5],
          'latitude':    [10,           11             ,12,         13,           14],
          'acq_date':    ['2024-01-01', '2024-02-02', '2024-03-03', '2024-04-04', '2024-05-05'],
          'another':     [0.1,          0.2,           0.3,         0.4,           0.5]})
    d2 = pd.DataFrame(
        {'longitude':   [1,            3,            9,            4,            5],
          'latitude':    [10,           11,           12,           20,           14],
          'acq_date':    ['2024-01-01', '2024-02-02', '2025-03-03', '2024-04-04', '2024-05-05'],
          'another':     [0.1,          0.2,           0.3,          0.4,          0.101]})
    df_expect = pd.DataFrame(
        {'longitude':   [1,            2,             3,           4,            5,             3,           9,            4          ],
          'latitude':    [10,           11             ,12,         13,           14,            11,          12,           20         ],
          'acq_date':    ['2024-01-01', '2024-02-02', '2024-03-03', '2024-04-04', '2024-05-05',  '2024-02-02','2025-03-03', '2024-04-04'],
          'another':     [0.1,          0.2,           0.3,         0.4,           0.5,          0.2,          0.3,          0.4       ]})
    
    test_viirs_data = {'snpp': d1,
                       'noaa': d2}
    dict_test = vt.merge_viirs(test_viirs_data)
    assert_frame_equal(df_expect, dict_test.get('df',''))

def test_merge_viirs_ignores_noaa():
    d1 = pd.DataFrame(
        {'longitude':   [1,            2,             3,           4,            5],
          'latitude':    [10,           11             ,12,         13,           14],
          'acq_date':    ['2024-01-01', '2024-02-02', '2024-03-03', '2024-04-04', '2024-05-05'],
          'another':     [0.1,          0.2,           0.3,         0.4,           0.5]})
    d2 = pd.DataFrame(
        {'longitude':   [1,            3,            9,            4,            5],
          'latitude':    [10,           11,           12,           20,           14],
          'acq_date':    ['2024-01-01', '2024-02-02', '2025-03-03', '2024-04-04', '2024-05-05'],
          'another':     [0.1,          0.2,           0.3,          0.4,          0.101]})
    
    test_viirs_data = {'snpp': d1,
                       'noaa': d2}
    dict_test = vt.merge_viirs(test_viirs_data, False)
    assert_frame_equal(test_viirs_data['snpp'], dict_test['df'])
    
def test_merge_viirs_data_report():
    d1 = pd.DataFrame(
        {'longitude':   [1,            2,             3,           4,            5],
          'latitude':    [10,           11             ,12,         13,           14],
          'acq_date':    ['2024-01-01', '2024-02-02', '2024-03-03', '2024-04-04', '2024-05-05'],
          'another':     [0.1,          0.2,           0.3,         0.4,           0.5]})
    d2 = pd.DataFrame(
        {'longitude':   [1,            3,            9,            4,            5],
          'latitude':    [10,           11,           12,           20,           14],
          'acq_date':    ['2024-01-01', '2024-02-02', '2025-03-03', '2024-04-04', '2024-05-05'],
          'another':     [0.1,          0.2,           0.3,          0.4,          0.101]})

    test_viirs_data = {'snpp': d1,
                       'noaa': d2}
    dict_test = vt.merge_viirs(test_viirs_data)
    dict_data_report = dict_test['data_report']
    assert dict_data_report['total_rows_snpp'] == 5 # type: ignore
    assert dict_data_report['total_rows_noaa'] == 3 # type: ignore