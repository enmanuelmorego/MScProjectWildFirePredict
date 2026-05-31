import sampling.sampling_functions as sf
import pandas as pd

# -----------------------------------
# TEST extract_temporal_sample()
# -----------------------------------
def test_valid_sample_extract_temporal_sample():
    df_fire = pd.DataFrame({"grid_id": [1, 1, 1, 1, 2, 2, 3],
                        "date": pd.to_datetime(["2020-06-15",  
                                                "2020-06-20",  
                                                "2020-07-01",  
                                                "2020-12-15",  
                                                "2020-06-15",
                                                "2020-12-15",
                                                "2020-12-15"]),
                        "composite_key": ["1_20200615",
                                          "1_20200620",
                                          "1_20200701",
                                          "1_20201215",
                                          "2_20200615",
                                          "2_20201215",
                                          "3_20201215"]})
    
    samples_dict = {'fire_lbl_comp_key'       : [],
                    'temporal_sample_comp_key': [],
                    'spatial_sample_comp_key' : [],
                    'used_comp_keys'          : set()}
    
    sample = sf.extract_temporal_sample(df_all_in=df_fire,
                                       current_grid_id_in=1,
                                       current_date_in=pd.Timestamp("2020-12-15"),
                                       used_comp_keys_in = samples_dict['used_comp_keys'])
    assert sample in {"1_20200615", "1_20200620"}

def test_exclude_if_used_extract_temporal_sample():
    df_fire = pd.DataFrame({"grid_id": [1, 1, 1, 1, 2, 2, 3],
                            "date": pd.to_datetime(["2020-06-15",  
                                                    "2020-06-20",  
                                                    "2020-07-01",  
                                                    "2020-12-15",  
                                                    "2020-06-15",
                                                    "2020-12-15",
                                                    "2020-12-15"]),
                            "composite_key": ["1_20200615",
                                              "1_20200620",
                                              "1_20200701",
                                              "1_20201215",
                                              "2_20200615",
                                              "2_20201215",
                                              "3_20201215"]})
               
    samples_dict = {'fire_lbl_comp_key'       : [],
                    'temporal_sample_comp_key': [],
                    'spatial_sample_comp_key' : [],
                    'used_comp_keys'          : {"A_20200620"}}
             
    sample = sf.extract_temporal_sample(df_all_in=df_fire,
                                    current_grid_id_in=1,
                                    current_date_in=pd.Timestamp("2020-12-15"),
                                    used_comp_keys_in = samples_dict['used_comp_keys'])
    assert sample == "1_20200615"

def test_no_sample_found_extract_temporal_sample():
    df_fire = pd.DataFrame({"grid_id": [1, 1, 1, 1, 2, 2, 3],
                            "date": pd.to_datetime(["2020-06-15",  
                                                    "2020-06-20",  
                                                    "2020-07-01",  
                                                    "2020-12-15",  
                                                    "2020-06-15",
                                                    "2020-12-15",
                                                    "2020-12-15"]),
                            "composite_key": ["1_20200615",
                                              "1_20200620",
                                              "1_20200701",
                                              "1_20201215",
                                              "2_20200615",
                                              "2_20201215",
                                              "3_20201215"]})
               
    samples_dict = {'fire_lbl_comp_key'       : [],
                    'temporal_sample_comp_key': [],
                    'spatial_sample_comp_key' : [],
                    'used_comp_keys'          : set()}
             
    sample = sf.extract_temporal_sample(df_all_in=df_fire,
                                        current_grid_id_in=2,
                                        current_date_in=pd.Timestamp("2020-06-15"),
                                        used_comp_keys_in = samples_dict['used_comp_keys'])
    assert sample == None

def test_window_expand_extract_temporal_sample():
    df_fire = pd.DataFrame({"grid_id": [1, 1, 1, 1, 2, 2, 3],
                            "date": pd.to_datetime(["2020-06-15",  
                                                    "2020-06-20",  
                                                    "2020-07-01",  
                                                    "2020-12-15",  
                                                    "2020-06-15",
                                                    "2019-11-20",
                                                    "2020-12-15"]),
                            "composite_key": ["1_20200615",
                                              "1_20200620",
                                              "1_20200701",
                                              "1_20201215",
                                              "2_20200615",
                                              "2_20191120",
                                              "3_20201215"]})
               
    samples_dict = {'fire_lbl_comp_key'       : [],
                    'temporal_sample_comp_key': [],
                    'spatial_sample_comp_key' : [],
                    'used_comp_keys'          : set()}
             
    sample_short = sf.extract_temporal_sample(df_all_in=df_fire,
                                              current_grid_id_in=2,
                                              current_date_in=pd.Timestamp("2020-06-15"),
                                              used_comp_keys_in = samples_dict['used_comp_keys'],
                                              span_limit_days = 10)
    sample_long = sf.extract_temporal_sample(df_all_in=df_fire,
                                              current_grid_id_in=2,
                                              current_date_in=pd.Timestamp("2020-06-15"),
                                              used_comp_keys_in = samples_dict['used_comp_keys'])
    assert sample_short == None
    assert sample_long  == "2_20191120"