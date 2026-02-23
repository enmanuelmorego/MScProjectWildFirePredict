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
                            False,True,  False,False]}
    df_test = pd.DataFrame(df_test)
    df_test['composite_key'] = (df_test['grid_id'].astype(str) + 
                                df_test['date'].dt.strftime("%Y%m%d"))
    df = pps.sample_fire_values(df_test, 7)
    assert df.shape[0] == 32

def test_sample_fire_values_select_correct_composite_key_allocation():
    df_test = {"grid_id": [1,1],
               "date": pd.to_datetime(["2020-01-12",     
                                       "2020-02-10"]),
               "fire_lbl": [True, False]}
    df_test = pd.DataFrame(df_test)
    df_test['composite_key'] = (df_test['grid_id'].astype(str) + 
                                df_test['date'].dt.strftime("%Y%m%d"))
    expect_composite_keys = pd.DataFrame({'composite_key': ['120200105','120200106','120200107','120200108',
                                                            '120200109','120200110','120200111','120200112']})
    df = pps.sample_fire_values(df_test, 7)
    for i, r in df.iterrows():
        assert r['composite_key'] ==  expect_composite_keys['composite_key'].iloc[i]

def test_sample_fire_values_overlapping_windows():
    df_test = {"grid_id": [1,1,2,2],
               "date": pd.to_datetime(["2020-01-12",     
                                       "2020-02-11",    # Expect full 7 days + label as grid id is different from next equal date (8)     
                                       "2020-02-11",     
                                       "2020-02-15"]),  # For grid id 2 we expect total 7 days from label (8) from 11-02, and 3 days + label from 15-02 (4)
                                                        # 8 + 3 + 8 = 19
               "fire_lbl": [False, True, True, True]}
    df_test = pd.DataFrame(df_test)
    df_test['composite_key'] = (df_test['grid_id'].astype(str) + 
                                df_test['date'].dt.strftime("%Y%m%d"))
    df = pps.sample_fire_values(df_test, 7)
    assert df.shape[0] == 20
    assert df['date'].min() == pd.Timestamp('2020-02-04')
    assert df['date'].max() == pd.Timestamp('2020-02-15')

def test_sample_fire_values_non_overlapping_windows():
    df_test = {"grid_id": [1,1,2,2],
               "date": pd.to_datetime(["2020-01-12",     
                                       "2020-02-11",    # Expect full 7 days + label as grid id is different from next equal date (8)     
                                       "2020-04-11",     
                                       "2020-02-15"]),  # For grid id 2 we expect total 7 days from label (8) from 11-02, and 3 days + label from 15-02 (4)
                                                        # 8 + 3 + 8 = 19
               "fire_lbl": [False, True, True, False]}
    df_test = pd.DataFrame(df_test)
    df_test['composite_key'] = (df_test['grid_id'].astype(str) + 
                                df_test['date'].dt.strftime("%Y%m%d"))    
    df = pps.sample_fire_values(df_test, 7)
    assert df.shape[0] == 16
    assert df['date'].min() == pd.Timestamp('2020-02-04')
    assert df['date'].max() == pd.Timestamp('2020-04-11')
    assert pd.Timestamp('2020-03-15') not in df['date']

def test_sample_nofire_candidates_valid_candidates():
    df_test = {"grid_id": [1,2,1,2,   1,2,1,2],
               "date": pd.to_datetime(["2020-01-12",     
                                       "2020-02-10",     
                                       "2020-03-01",     
                                       "2020-02-04",     

                                       "2020-01-18",    # Include  
                                       "2019-12-28",    # Exclude     
                                       "2020-02-15",    # Include
                                       "2020-03-16"]),  # Exclude  
               "fire_lbl": [True, True, True, True,
                            False,False,False,False]}
    df_test = pd.DataFrame(df_test)
    df_test['composite_key'] = (df_test['grid_id'].astype(str) + 
                                df_test['date'].dt.strftime("%Y%m%d")) 
    empty_df = df_test.iloc[[]]

    dict_expect = {"120200112": df_test.iloc[[4]],     
                   "220200210": empty_df,     
                   "120200301": df_test.iloc[[6]],     
                   "220200204": empty_df}
    dict_test = pps.sample_nofire_candidates(df_test, 30)
    for k, v in dict_test.items():
        assert_frame_equal(dict_test.get(k), dict_expect.get(k))

def test_sample_nofire_candidates_nofire_candidates():
    df_test = {"grid_id": [1,2,1,2,   1,2,1,2],
               "date": pd.to_datetime(["2020-01-12",     
                                       "2020-02-10",     
                                       "2020-03-01",     
                                       "2020-02-04",     

                                       "2020-01-18",    # Include  
                                       "2019-12-28",    # Exclude     
                                       "2020-02-15",    # Include
                                       "2020-03-16"]),  # Exclude  
               "fire_lbl": [False] * 8}
    df_test = pd.DataFrame(df_test)
    df_test['composite_key'] = (df_test['grid_id'].astype(str) + 
                                df_test['date'].dt.strftime("%Y%m%d")) 
    dict_test = pps.sample_nofire_candidates(df_test, 30)
    dict_expect = {}
    assert dict_test == dict_expect

def test_sample_nofire_values_valid_inputs():
    df = pd.DataFrame({"grid_id": [1, 1],
                       "date": pd.to_datetime(["2020-01-10", "2020-01-25"]),
                       "fire_lbl": [True, False]})
    df["composite_key"] = df["grid_id"].astype(str) + df["date"].dt.strftime("%Y%m%d")

    # Fire protected set
    fire_df = pps.sample_fire_values(df, window_size=2)
    sampled_set = set(fire_df["composite_key"])

    candidate_dict = pps.sample_nofire_candidates(df, 30)

    result = pps.sample_nofire_values(no_fire_per_fire_obs=1,
                                      candidate_dict=candidate_dict,
                                      window_size=2,
                                      sampled_set=sampled_set)

    assert result["no_fire_df"].shape[0] == 3 
    assert result["sampling_report"]["no_fire_composite_key"][0] is not None

def test_sample_nofire_values_novalid_nofire_sample():
    df = pd.DataFrame({"grid_id": [1, 1],
                       "date": pd.to_datetime(["2020-01-10", "2020-01-11"]),
                       "fire_lbl": [True, False]})
    df["composite_key"] = df["grid_id"].astype(str) + df["date"].dt.strftime("%Y%m%d")

    # Fire protected set
    fire_df = pps.sample_fire_values(df, window_size=2)
    sampled_set = set(fire_df["composite_key"])

    candidate_dict = pps.sample_nofire_candidates(df, 30)

    result = pps.sample_nofire_values(no_fire_per_fire_obs=1,
                                      candidate_dict=candidate_dict,
                                      window_size=2,
                                      sampled_set=sampled_set)

    assert result["no_fire_df"].empty
    assert result["sampling_report"]["no_fire_composite_key"][0] is None

def test_sample_nofire_values_limit_ratio():
    df = pd.DataFrame({"grid_id": [1, 1, 1, 1, 1],
                       "date": pd.to_datetime(["2020-01-10", "2020-01-01","2020-01-25","2020-01-30","2020-02-05"]),
                       "fire_lbl": [True, False,False,False,False]})
    df["composite_key"] = df["grid_id"].astype(str) + df["date"].dt.strftime("%Y%m%d")

    # Fire protected set
    fire_df = pps.sample_fire_values(df, window_size=4)
    sampled_set = set(fire_df["composite_key"])

    candidate_dict = pps.sample_nofire_candidates(df, 30)

    result = pps.sample_nofire_values(no_fire_per_fire_obs=2,
                                      candidate_dict=candidate_dict,
                                      window_size=4,
                                      sampled_set=sampled_set)

    assert result["no_fire_df"].shape[0] == 10
    assert result["no_fire_df"]["date"].min() == pd.Timestamp('2019-12-28')
    assert result["no_fire_df"]["date"].max() == pd.Timestamp('2020-01-25')

    assert result["sampling_report"]["no_fire_composite_key"] == ['120200101', '120200125']

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
                              
    df_expect = pd.DataFrame({'date_dv': pd.to_datetime(['2020-01-09','2020-01-22','2020-01-28']),
                              'grid_id_dv': [1,1,2],
                              'fire_lbl_dv': [False]* 3 })
    
    df_test = pps.sample_nofire_obs(df_main, df_fire, 5, 2)
    assert_frame_equal(df_expect, df_test)

def test_sample_nofire_obs_nofire_total_samples():
    df_fire   = pd.DataFrame({'date_dv': pd.to_datetime(['2020-01-22','2020-03-20']),
                                'grid_id_dv': [1,1]})

    df_main   = pd.DataFrame({'date': pd.date_range(start = '2020-01-19', end = '2020-01-27'),
                                'grid_id': [1]*9,
                                'fire_lbl': [False]*9})
    df_main["composite_key"] = df_main["grid_id"].astype(str) + df_main["date"].dt.strftime("%Y%m%d")
    
    df_test_small = pps.sample_nofire_obs(df_main, df_fire, 5, 2)
    df_test_large = pps.sample_nofire_obs(df_main, df_fire, 5, 5)

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
    df_expect = pd.DataFrame({'date_dv': pd.to_datetime(['2020-01-09']),
                              'grid_id_dv': [1],
                              'fire_lbl_dv': [False]})
    
    df_test = pps.sample_nofire_obs(df_main, df_fire, 5, 2)
    assert_frame_equal(df_expect, df_test)