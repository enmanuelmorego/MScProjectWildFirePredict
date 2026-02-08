import pandas as pd
from pandas.testing import assert_frame_equal
import load_data as ld
from datetime import datetime, date
from pathlib import Path


'''
pipenv run pytest
'''

# -------------------------
# VIIRS DATA LOAD PROCESS
# -------------------------
# -----
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

# -----
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
# -----
def test_check_drive_sentinel_empty_list():
    files_list = []
    df = pd.DataFrame({"date": ["2025-01-01", "2025-01-05"]})

    out_expect = {"available_files": [],
                  "required_days": [date(2025, 1, 1), date(2025, 1, 2),
                                    date(2025, 1, 3),date(2025, 1, 4),
                                    date(2025, 1, 5),],}

    out = ld.check_drive_sentinel(df, files_list)
    assert out == out_expect

def test_check_drive_sentinel_all_non_overlapping_files():
    files_list = ['20190101-20190115_.csv', '20190101-20190115_.csv','20190101-20190115_.csv' ]
    df = pd.DataFrame({"date": ["2025-01-01", "2025-01-05"]})

    out_expect = {"available_files": [],
                  "required_days": [date(2025, 1, 1), date(2025, 1, 2),
                                    date(2025, 1, 3),date(2025, 1, 4),
                                    date(2025, 1, 5),],}

    out = ld.check_drive_sentinel(df, files_list)
    assert out == out_expect

def test_check_drive_sentinel_partial_overlapping_files():
    files_list = ['20250101-20250115_.csv', '20250120-20250125_.csv']
    df = pd.DataFrame({"date": ["2025-01-01", "2025-02-01"]})

    out_expect = {"available_files": ['20250101-20250115_.csv', '20250120-20250125_.csv'],
                  "required_days":   [date(2025, 1, 16), date(2025, 1, 17),
                                      date(2025, 1, 18), date(2025, 1, 19),
                                      date(2025, 1, 26), date(2025, 1, 27),
                                      date(2025, 1, 28), date(2025, 1, 29),
                                      date(2025, 1, 30), date(2025, 1, 31),
                                      date(2025, 2, 1)],}

    out = ld.check_drive_sentinel(df, files_list)
    assert out == out_expect

def test_check_drive_sentinel_all_overlapping_files():
    files_list = ['20250101-20250120_.csv', '20250121-20250130_.csv']
    df = pd.DataFrame({"date": ["2025-01-01", "2025-01-30"]})

    out_expect = {"available_files": files_list,
                  "required_days":   []}

    out = ld.check_drive_sentinel(df, files_list)
    assert out == out_expect

def test_check_drive_sentinel_early_overlap_start():
    files_list = ['20250101-20250115_.csv', '20250120-20250125_.csv']
    df = pd.DataFrame({"date": ["2025-01-10", "2025-02-01"]})

    out_expect = {"available_files": ['20250101-20250115_.csv', '20250120-20250125_.csv'],
                  "required_days":   [date(2025, 1, 16), date(2025, 1, 17),
                                      date(2025, 1, 18), date(2025, 1, 19),
                                      date(2025, 1, 26), date(2025, 1, 27),
                                      date(2025, 1, 28), date(2025, 1, 29),
                                      date(2025, 1, 30), date(2025, 1, 31),
                                      date(2025, 2, 1)],}

    out = ld.check_drive_sentinel(df, files_list)
    assert out == out_expect

# -----
def test_batch_create_sentinel():
    df = pd.DataFrame({"date": ["2025-01-01", "2025-01-04", "2025-01-02", "2025-01-03",
                                "2025-01-01", "2025-01-05", "2025-01-06", "2025-01-07",
                                "2025-01-08", "2025-01-09", "2025-01-09"],
                       "name": ["a", "a.1", "b", "c", "d",
                                "e", "f", "g", "h", "i", "i.1"]})

    required = pd.date_range(start="2025-01-01",
                             end="2025-01-09",
                             freq="D").date.tolist()

    out = ld.batch_create_sentinel(df, required, batch_size=2)

    # Correct number of batches
    assert len(out) == 5 

    # Check batch-by-batch dates
    expected_batches = {"batch_1": {date(2025, 1, 1), date(2025, 1, 2)},
                        "batch_2": {date(2025, 1, 3), date(2025, 1, 4)},
                        "batch_3": {date(2025, 1, 5), date(2025, 1, 6)},
                        "batch_4": {date(2025, 1, 7), date(2025, 1, 8)},
                        "batch_5": {date(2025, 1, 9)}}

    for batch_name, expected_dates in expected_batches.items():
        batch_df = out[batch_name]

        # ensure only expected dates are present
        assert set(batch_df["date"]) == expected_dates

# -------------------------
# FIRE WEATHER INDEX
# -------------------------  
def test_check_drive_fwi_correct_years():
    dates = pd.to_datetime(['2019-01-01', '2020-02-02','2017-02-02', '2019-12-10','2018-01-01', '2027-01-01'])
    df_test = pd.DataFrame({'date': dates})
    f = ['2018FWI.csv', 
         '2020FWI.csv',

         '2020FWI.grib',
         '2021FWI.grib',
         '2019FWI.grib']
    
    out = ld.check_drive_fwi(df_test, f)
    expect = {'available_csv' : ['2018FWI.csv', '2020FWI.csv'], 
              'available_grib': ['2019FWI.grib'],
              'required_years': {'2017', '2027'}}
    assert out == expect

def test_check_drive_fwi_nomatching_years():
    dates = pd.to_datetime(['2019-01-01', '2020-02-02','2017-02-02', '2019-12-10'])
    df_test = pd.DataFrame({'date': dates})
    f = ['2015FWI.csv', 
         '2010FWI.csv',
         '2015FWI.grib',
         '2012FWI.grib']
    out = ld.check_drive_fwi(df_test, f)
    expect = {'available_csv' : [], 
              'available_grib': [],
              'required_years': {'2017', '2019', '2020'}}
    assert out == expect

def test_check_drive_fwi_full_match():
    dates = pd.to_datetime(['2017-02-02', 
                            '2019-01-01', '2019-12-10',
                            '2020-02-02', 
                            '2021-01-01'])
    df_test = pd.DataFrame({'date': dates})
    f = ['1990FWI.csv',
         '2017FWI.csv',
         '2018FWI.csv',
         '2019FWI.csv',
         '2019FWI.grib',
         '2020FWI.csv',
         '2020FWI.grib',
         '2021FWI.grib']
    
    out = ld.check_drive_fwi(df_test, f)
    expect = {'available_csv': ['2017FWI.csv',
                                '2019FWI.csv', 
                                '2020FWI.csv'], 
          