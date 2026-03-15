import pandas as pd
import geopandas as gpd
import preprocessing_general as pps
from pandas.testing import assert_frame_equal

# -------------------------
# SAMPLING FIRE DATAPOINTS
# -------------------------  

def test_sample_nofire_obs_modelcase():
    df_fire   = pd.DataFrame({'date_dv': pd.to_datetime(['2020-01-10','2020-01-20','2020-02-01']),
                              'grid_id_dv': [1,1,2]})
    
    df_main   = pd.DataFrame({'date': pd.to_datetime(['2020-01-09',    # 1 day before
                                                      '2020-01-22',    # 2 days ahead
                                                      '2020-01-28',    # 2 days before
                                                      '2020-06-10',    # Date outside all fire dates window
                                                      '2020-01-17',    # Valid date but non matching grid id 
                                                      '2020-01-18']),  # Valid date but fire label
                              'grid_id': [1,1,2,1,9,1],
                              'composite_key': ['120200109', '120200122','220200128','120200610','920200117','120200118'],
                              'fire_lbl': [False, False,False,False,False,True]})
    df_main = gpd.GeoDataFrame(df_main)
                              
    df_expect = pd.DataFrame({'date_dv': pd.to_datetime(['2020-01-09','2020-01-22','2020-01-28']),
                              'grid_id_dv': [1,1,2],
                              'fire_lbl_dv': [False]* 3 })
    
    df_test = pps.sample_nofire_obs(df_main, df_fire, 5, 2, 42)
    assert_frame_equal(df_expect, df_test)

def test_sample_nofire_obs_nofire_total_samples():
    df_fire   = pd.DataFrame({'date_dv': pd.to_datetime(['2020-01-22','2020-03-20']),
                                'grid_id_dv': [1,1]})

    df_main   = pd.DataFrame({'date': pd.date_range(start = '2020-01-19', end = '2020-01-27'),
                                'grid_id': [1]*9,
                                'fire_lbl': [False]*9})
    df_main["composite_key"] = df_main["grid_id"].astype(str) + df_main["date"].dt.strftime("%Y%m%d")
    df_main = gpd.GeoDataFrame(df_main)
    df_test_small = pps.sample_nofire_obs(df_main, df_fire, 5, 2, 42)
    df_test_large = pps.sample_nofire_obs(df_main, df_fire, 5, 5, 42)

    assert df_test_small.shape[0] == 2
    assert df_test_large.shape[0] == 5


def test_sample_nofire_obs_overlapping_date_expect1():
    df_fire   = pd.DataFrame({'date_dv': pd.to_datetime(['2020-01-10','2020-01-12','2020-02-01']),
                              'grid_id_dv': [1,1,2]})
    df_main   = pd.DataFrame({'date': pd.to_datetime(['2020-01-09',
                                                      '2020-01-01']),
                              'grid_id': [1,1],
                              'composite_key': ['120200109', '120200101'],
                              'fire_lbl': [False, False]})
    df_main = gpd.GeoDataFrame(df_main)
    df_expect = pd.DataFrame({'date_dv': pd.to_datetime(['2020-01-09']),
                              'grid_id_dv': [1],
                              'fire_lbl_dv': [False]})
    
    df_test = pps.sample_nofire_obs(df_main, df_fire, 5, 2, 42)
    assert_frame_equal(df_expect, df_test)