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
    dict_expect = {"2025_B011_20250102_20250102_sentinel_batch": [date]*5,
                   "2025_B012_20250102_20250102_sentinel_batch": [date]*5,
                   "2025_B013_20250102_20250102_sentinel_batch": [date]*5,
                   "2025_B014_20250102_20250102_sentinel_batch": [date]*5}
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
    dict_expect = {"2025_B000_20250102_20250102_sentinel_batch": [date]*5,
                   "2025_B001_20250102_20250102_sentinel_batch": [date]*5,
                   "2025_B002_20250102_20250102_sentinel_batch": [date]*5,
                   "2025_B003_20250102_20250102_sentinel_batch": [date]*4}
    dict_out, new_batch = psent.split_batch_greater_than_limit(date, group_size, batch_size, batch_num)
    assert new_batch    == batch_num_expect
    assert dict_out     == dict_expect