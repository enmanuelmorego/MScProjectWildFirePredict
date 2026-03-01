import pandas as pd
import pp_sentinel as psent
from pandas.testing import assert_frame_equal

def test_split_batch_greater_than_limit_even_number_split():

    group_size = 20
    batch_size = 5
    batch_num  = 11
    date       = pd.to_datetime('2025-01-02')
    # Set expectations
    batch_num_expect = 15
    dict_expect = {"2025_B011_20250102_20250102_sentinel_batch": {'date': [date], 'split_group': 5},
                   "2025_B012_20250102_20250102_sentinel_batch": {'date': [date], 'split_group': 5},
                   "2025_B013_20250102_20250102_sentinel_batch": {'date': [date], 'split_group': 5},
                   "2025_B014_20250102_20250102_sentinel_batch": {'date': [date], 'split_group': 5}}
    dict_out, new_batch = psent.split_batch_greater_than_limit(date, group_size, batch_size, batch_num)
    assert new_batch    == batch_num_expect
    assert dict_out     == dict_expect

def test_split_batch_greater_than_limit_odd_number_split():

    group_size = 19
    batch_size = 5
    batch_num  = 0
    date       = pd.to_datetime('2025-01-02')
    # Set expectations
    batch_num_expect = 4
    dict_expect = {"2025_B000_20250102_20250102_sentinel_batch": {'date': [date], 'split_group': 5},
                   "2025_B001_20250102_20250102_sentinel_batch": {'date': [date], 'split_group': 5},
                   "2025_B002_20250102_20250102_sentinel_batch": {'date': [date], 'split_group': 5},
                   "2025_B003_20250102_20250102_sentinel_batch": {'date': [date], 'split_group': 4}}
    dict_out, new_batch = psent.split_batch_greater_than_limit(date, group_size, batch_size, batch_num)
    assert new_batch    == batch_num_expect
    assert dict_out     == dict_expect

def test_sampled_to_batch_within_limit_batches_singledate():
    df = pd.DataFrame({'date': ['2023-01-01','2023-01-01','2023-01-01',
                                '2023-01-02','2023-01-02','2023-01-02']})
    df['date']  = pd.to_datetime(df['date'])
    dict_expect = {"2023_B000_20230101_20230101_sentinel_batch": {'date': [pd.Timestamp('2023-01-01')],'split_group': None},
                   "2023_B001_20230102_20230102_sentinel_batch": {'date': [pd.Timestamp('2023-01-02')],'split_group': None}}
    dict_test = psent.sampled_to_batch(df, 3)
    assert dict_expect == dict_test

def test_sampled_to_batch_within_limit_batches_multidate():
    df = pd.DataFrame({'date': ['2023-01-01','2023-01-01','2023-01-02',
                                '2023-01-03','2023-01-04','2023-01-04',
                                '2023-01-30',
                                '2023-02-01','2023-02-01','2023-02-01']})
    df['date']  = pd.to_datetime(df['date'])
    dict_expect = {"2023_B000_20230101_20230102_sentinel_batch": {'date': [pd.Timestamp('2023-01-01'),pd.Timestamp('2023-01-02')],'split_group': None},
                   "2023_B001_20230103_20230104_sentinel_batch": {'date': [pd.Timestamp('2023-01-03'),pd.Timestamp('2023-01-04')],'split_group': None},
                   "2023_B002_20230130_20230130_sentinel_batch": {'date': [pd.Timestamp('2023-01-30')],'split_group': None},
                   "2023_B003_20230201_20230201_sentinel_batch": {'date': [pd.Timestamp('2023-02-01')],'split_group': None}
                   }
                   
    dict_test = psent.sampled_to_batch(df, 3)
    assert dict_expect == dict_test