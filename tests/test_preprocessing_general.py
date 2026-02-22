import pandas as pd
import preprocessing_general as pps
# -------------------------
# SAMPLING FIRE DATAPOINTS
# -------------------------  

def test_sample_fire_values_select_fire_only():
    df_test = {"grid_id": [1,1,1,1,2,2,2,2],
               "date": pd.to_datetime(["2020-01-12",     
                                       "2020-02-10",     
                                       "2020-03-01",     
                                       "2020-02-04",     

                                       "2020-01-18",    
                                       "2019-12-28",       
                                       "2020-02-15",
                                       "2020-03-04"]),
               "fire_lbl": [True, False, True, True,
                            False,True,  False,False]}
    df_test = pd.DataFrame(df_test)
    df = pps.sample_fire_values(df_test, 7)
    assert df.shape[0] == 32

def test_sample_fire_values_overlapping_windows():
    df_test = {"grid_id": [1,1,2,2],
               "date": pd.to_datetime(["2020-01-12",     
                                       "2020-02-11",    # Expect full 7 days + label as grid id is different from next equal date (8)     
                                       "2020-02-11",     
                                       "2020-02-15"]),  # For grid id 2 we expect total 7 days from label (8) from 11-02, and 2 days + label from 15-02 (3)
                                                        # 8 + 3 + 8 = 19
               "fire_lbl": [False, True, True, True]}
    df_test = pd.DataFrame(df_test)
    df = pps.sample_fire_values(df_test, 7)
    assert df.shape[0] == 19