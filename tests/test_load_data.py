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
    dict_test = ld.merge_viirs(test_viirs_data)
    assert_frame_equal(df_expect, dict_test.get('df'))

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
    dict_test = ld.merge_viirs(test_viirs_data, False)
    assert_frame_equal(test_viirs_data.get('snpp'), dict_test.get('df'))
    
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
    dict_test = ld.merge_viirs(test_viirs_data)
    dict_data_report = dict_test.get('data_report')
    assert dict_data_report.get('total_rows_snpp') == 5
    assert dict_data_report.get('total_rows_noaa') == 3

def test_filter_viirs_keeps_only_high_quality_vegetation():
    df = pd.DataFrame({"type":       [0,   1,   0,   0],
                       "confidence": ["h", "h", "l", "n"],
                       "value":      [10,  20,  30,  40]})
                                    # ok - x  - x - ok
    result = ld.filter_viirs(df)

    expected = pd.DataFrame({"type": [0, 0],
                             "confidence": ["h", "n"],
                             "value": [10, 40]})

    pd.testing.assert_frame_equal(
        result.reset_index(drop=True),
        expected)

def test_filter_viirs_returns_empty_when_no_rows_match():
    df = pd.DataFrame({"type":       [1, 1],
                       "confidence": ["l", "l"]})
    result = ld.filter_viirs(df)
    assert result.empty

def test_filter_viirs_case_insensitive():
    df = pd.DataFrame({"type":       [0,   1,   0,   0],
                       "confidence": ["H", "h", "l", "N "],
                       "value":      [10,  20,  30,  40]})
                                    # ok - x  - x - ok
    result = ld.filter_viirs(df)

    expected = pd.DataFrame({"type": [0, 0],
                             "confidence": ["h", "n"],
                             "value": [10, 40]})

    pd.testing.assert_frame_equal(result.reset_index(drop=True),
                                  expected)


# -------------------------
# GOOGLE EE SENTINEL-2
# -------------------------  
def test_sentinel_check_drive_empty_list():
    pass