import pandas as pd
import pp_sentinel as psent
import pytest

# -------------------------------------
# TEST split_batch_greater_than_limit
# -------------------------------------
def test_split_batch_greater_than_limit_even_number_split():

    group_size = 20
    batch_size = 5
    batch_num  = 11
    date       = pd.to_datetime('2025-01-02')
    # Set expectations
    batch_num_expect = 15
    dict_expect = {"2025_B011_20250102_20250102_sentinel_batch": {'date': [date], 'split_group': [0,4]  },
                   "2025_B012_20250102_20250102_sentinel_batch": {'date': [date], 'split_group': [5,9]  },
                   "2025_B013_20250102_20250102_sentinel_batch": {'date': [date], 'split_group': [10,14]},
                   "2025_B014_20250102_20250102_sentinel_batch": {'date': [date], 'split_group': [15,19]}}
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
    dict_expect = {"2025_B000_20250102_20250102_sentinel_batch": {'date': [date], 'split_group': [0,4]  },
                   "2025_B001_20250102_20250102_sentinel_batch": {'date': [date], 'split_group': [5,9]  },
                   "2025_B002_20250102_20250102_sentinel_batch": {'date': [date], 'split_group': [10,14]},
                   "2025_B003_20250102_20250102_sentinel_batch": {'date': [date], 'split_group': [15,18]}}
    dict_out, new_batch = psent.split_batch_greater_than_limit(date, group_size, batch_size, batch_num)
    assert new_batch    == batch_num_expect
    assert dict_out     == dict_expect

# -------------------------------------
# TEST sampled_to_batch
# -------------------------------------
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

def test_sampled_to_batch_above_limit_batches():
    df = pd.DataFrame({'date': ['2023-01-01','2023-01-01','2023-01-01','2023-01-01','2023-01-01','2023-01-01','2023-01-01',
                                '2023-02-01','2023-02-01','2023-02-01',
                                '2023-03-01','2023-02-01','2023-02-02','2023-02-02']})
    df['date']  = pd.to_datetime(df['date'])
    dict_expect = {"2023_B000_20230101_20230101_sentinel_batch": {'date': [pd.Timestamp('2023-01-01')],'split_group': [0, 3]},
                   "2023_B001_20230101_20230101_sentinel_batch": {'date': [pd.Timestamp('2023-01-01')],'split_group': [4, 6]},
                   "2023_B002_20230201_20230201_sentinel_batch": {'date': [pd.Timestamp('2023-02-01')],'split_group': None},
                   "2023_B003_20230202_20230301_sentinel_batch": {'date': [pd.Timestamp('2023-02-02'),pd.Timestamp('2023-03-01')],'split_group': None}}
                   
                   
    dict_test = psent.sampled_to_batch(df, 4)
    assert dict_expect == dict_test

def test_sampled_to_batch_unsorted_input():
    df = pd.DataFrame({'date': ['2025-01-01','2023-02-12','2025-01-01','2023-10-11','2025-01-01']})
    df['date']  = pd.to_datetime(df['date'])
    dict_expect = {"2023_B000_20230212_20231011_sentinel_batch": {'date': [pd.Timestamp('2023-02-12'),pd.Timestamp('2023-10-11')],'split_group': None},
                   "2025_B001_20250101_20250101_sentinel_batch": {'date': [pd.Timestamp('2025-01-01')],'split_group': [0, 1]},
                   "2025_B002_20250101_20250101_sentinel_batch": {'date': [pd.Timestamp('2025-01-01')],'split_group': [2,2]}}
                   
                   
    dict_test = psent.sampled_to_batch(df, 2)
    assert dict_expect == dict_test

def test_sampled_to_batch_raise_valuerror():
    df = pd.DataFrame({'date': ['2025-01-01','2023-02-12','2025-01-01','2023-10-11','2025-01-01']})
    df['date']  = pd.to_datetime(df['date'])
    with pytest.raises(ValueError):  
        dict_test = psent.sampled_to_batch(df, 900)

# -------------------------------------
# TEST sampled_to_batch_dfs
# -------------------------------------