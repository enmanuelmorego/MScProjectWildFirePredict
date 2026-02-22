import pandas as pd
import preprocessing_general as pps
from pandas.testing import assert_frame_equal

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
                            False,True,