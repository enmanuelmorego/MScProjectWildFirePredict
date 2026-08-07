import utils.validation_checks as vc
import pandas as pd 
import pytest

# ==========================================
# TEST validate_resnet_feature_extractor()
# ==========================================
def test_validate_resnet_feature_extractor_no_duplicates():
    df_test = pd.DataFrame({'composite_key': ['001', '002','003'],
                            'feat_01': [0,1,2],
                            'feat_02': [0,110,10]})
    assert vc.validate_resnet_feature_extractor(df_test) is None

def test_validate_resnet_feature_extractor_real_duplicates():
    df_test = pd.DataFrame({'composite_key': ['001','001','001', '002','003'],
                            'feat_01': [0,0,0,3 ,2],
                            'feat_02': [0,0,0,8,110]})
    assert vc.validate_resnet_feature_extractor(df_test) is None

def test_validate_resnet_feature_extractor_different_duplicates():
    df_test = pd.DataFrame({'composite_key': ['001','001','001', '002','003'],
                            'feat_01': [0,11,13,3 ,2],
                            'feat_02': [0,11,13,8,110]})
    with pytest.raises(ValueError):
        vc.validate_resnet_feature_extractor(df_test)

def test_validate_resnet_feature_extractor_one_duplicate_differs():
    df_test = pd.DataFrame({"composite_key": ["001", "001", "001"],
                             "feat_01": [5, 5, 99],
                             "feat_02": [8, 8, 8]})

    with pytest.raises(ValueError):
        vc.validate_resnet_feature_extractor(df_test)

def test_validate_resnet_feature_extractor_multiple_duplicate_groups():
    df_test = pd.DataFrame({"composite_key": ["001", "001", "002", "002"],
                            "feat_01": [1, 1, 5, 6],
                            "feat_02": [2, 2, 8, 8]})

    with pytest.raises(ValueError):
        vc.validate_resnet_feature_extractor(df_test)

def test_validate_resnet_feature_extractor_unsorted_duplicates():
    df_test = pd.DataFrame({"composite_key": ["002", "001", "002", "001"],
                            "feat_01": [3, 1, 3, 1],
                            "feat_02": [4, 2, 4, 2]})

    assert vc.validate_resnet_feature_extractor(df_test) is None

# ==========================================
# TEST validate_composite_keys_mapping()
# ==========================================
def test_validate_composite_keys_mapping_all_valid_empty_missed():
    df_feat = pd.DataFrame({'composite_key': ['00120200501', 
                                              '512202050101',
                                              '512202050101',],
                            'feat_01': [0,11,1],
                            'feat_02': [0,11,1]})
    df_sampled = pd.DataFrame({'composite_key': ['00120200501', 
                                              '512202050101',
                                              '512202050101',],
                            'feat_01': [0,11,1],
                            'feat_02': [0,11,1]})
    df_missed = pd.DataFrame({'composite_key': [],
                              'some_var': []})
    assert vc.validate_composite_keys_mapping(df_feat, df_sampled, df_missed) == None

def test_validate_composite_keys_mapping_all_valid_with_missed():
    # Feature extraction contains 2 composite keys only
    df_feat = pd.DataFrame({'composite_key': ['00120200501', 
                                              '512202061201',],
                            'feat_01': [0,11],
                            'feat_02': [0,11]})
    # Sampled data expects 3 coposite keys 
    df_sampled = pd.DataFrame({'composite_key': ['00120200501', 
                                              '512202050101',
                                              '512202061201',],
                            'feat_01': [0,11,1],
                            'feat_02': [0,11,1]})
    # 1 composiote key was not found in Sentinel 2
    df_missed = pd.DataFrame({'composite_key': ['512202050101'],
                              'some_var': [1]})
    assert vc.validate_composite_keys_mapping(df_feat, df_sampled, df_missed) == None

def test_validate_composite_keys_mapping_non_valid_empty_missed():
    df_feat = pd.DataFrame({'composite_key': ['00120200501', 
                                              '512202050101',
                                              'notsampled',],
                            'feat_01': [0,11,1],
                            'feat_02': [0,11,1]})
    df_sampled = pd.DataFrame({'composite_key': ['00120200501', 
                                              '512202050101',
                                              '512202050101',],
                            'feat_01': [0,11,1],
                            'feat_02': [0,11,1]})
    df_missed = pd.DataFrame({'composite_key': [],
                              'some_var': []})
    with pytest.raises(ValueError):
        vc.validate_composite_keys_mapping(df_feat, df_sampled, df_missed)

def test_validate_composite_keys_mapping_size_missmatch_empty_missed():
    df_feat = pd.DataFrame({'composite_key': ['00120200501', 
                                              '512202050101'],
                            'feat_01': [0,11],
                            'feat_02': [0,11]})
    df_sampled = pd.DataFrame({'composite_key': ['00120200501', 
                                              '512202050101',
                                              '512202061201',],
                            'feat_01': [0,11,1],
                            'feat_02': [0,11,1]})
    df_missed = pd.DataFrame({'composite_key': [],
                              'some_var': []})
    with pytest.raises(ValueError):
        vc.validate_composite_keys_mapping(df_feat, df_sampled, df_missed)

def test_validate_composite_keys_mapping_non_valid_with_wrong_missed():
    """This is testing two things in the same place. Consider splitting the test to ensure we know whats
    failing/passing if failure were to happenb"""
    df_feat = pd.DataFrame({'composite_key': ['00120200501', 
                                              '512202050101',
                                              'notsampled',],
                            'feat_01': [0,11,1],
                            'feat_02': [0,11,1]})
    df_sampled = pd.DataFrame({'composite_key': ['00120200501', 
                                              '512202050101',
                                              '512202060101',],
                            'feat_01': [0,11,1],
                            'feat_02': [0,11,1]})
    df_missed = pd.DataFrame({'composite_key': ['512202050101'],
                              'some_var': [1]})
    with pytest.raises(ValueError):
        vc.validate_composite_keys_mapping(df_feat, df_sampled, df_missed)

# ==========================================
# TEST valid_composite_key()
# ==========================================
def test_valid_composite_key_valid_date_single_digit_compoosite_key():
    assert vc.valid_composite_key('120261009') == True

def test_valid_composite_key_valid_date_mutiple_digits_compoosite_key():
    assert vc.valid_composite_key('1020261009') == True
    assert vc.valid_composite_key('001020261009') == True
    assert vc.valid_composite_key('99920261009') == True

def test_valid_composite_key_nonvalid_date_single():
    assert vc.valid_composite_key('1202261009') == False
    assert vc.valid_composite_key('120260230') == False
    assert vc.valid_composite_key('120261301') == False

def test_valid_composite_key_nondidigts():
    assert vc.valid_composite_key('1a20261009') == False
    assert vc.valid_composite_key('1_2026/10/09') == False
    assert vc.valid_composite_key('1_2026_10_09') == False
    assert vc.valid_composite_key('1 20261009') == False

def test_valid_composite_key_wrong_datatype():
        assert vc.valid_composite_key(120261009) == False   # type: ignore[arg-type]

# ==========================================
# TEST validate_date_leakage()
# ==========================================
def test_validate_date_leakage_no_leakage():
    df_train = pd.DataFrame({'date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03'])})
    df_validation = pd.DataFrame({'date': pd.to_datetime(['2023-01-04', '2023-01-05'])})
    df_test = pd.DataFrame({'date': pd.to_datetime(['2023-01-06', '2023-01-07'])})

    assert vc.validate_date_leakage(df_train, df_validation, df_test, date_col='date') is None

def test_validate_date_leakage_with_leakage():
    df_train = pd.DataFrame({'date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03'])})
    df_validation = pd.DataFrame({'date': pd.to_datetime(['2023-01-03', '2023-01-04'])})
    df_test = pd.DataFrame({'date': pd.to_datetime(['2023-01-05', '2023-01-06'])})

    with pytest.raises(ValueError):
        vc.validate_date_leakage(df_train, df_validation, df_test, date_col='date')

# ==========================================
# TEST validate_composite_keys_intersections()
# ==========================================
def test_validate_composite_keys_intersections_no_intersection():
    df_1 = pd.DataFrame({'composite_key': ['001', '002', '003']})
    df_2 = pd.DataFrame({'composite_key': ['004', '005', '006']})
    df_3 = pd.DataFrame({'composite_key': ['007', '008', '009']})

    assert vc.validate_composite_keys_intersections(df_1, df_2, df_3, col='composite_key') is None

def test_validate_composite_keys_intersections_with_intersection_train_val():
    df_1 = pd.DataFrame({'composite_key': ['001', '002', '003']})
    df_2 = pd.DataFrame({'composite_key': ['003', '004', '005']})
    df_3 = pd.DataFrame({'composite_key': ['006', '007', '008']})

    with pytest.raises(ValueError):
        vc.validate_composite_keys_intersections(df_1, df_2, df_3, col='composite_key')

def test_validate_composite_keys_intersections_with_intersection_train_test():
    df_1 = pd.DataFrame({'composite_key': ['001', '002', '003']})
    df_2 = pd.DataFrame({'composite_key': ['004', '005', '006']})
    df_3 = pd.DataFrame({'composite_key': ['003', '007', '008']})

    with pytest.raises(ValueError):
        vc.validate_composite_keys_intersections(df_1, df_2, df_3, col='composite_key')

def test_validate_composite_keys_intersections_with_intersection_val_test():
    df_1 = pd.DataFrame({'composite_key': ['001', '002', '003']})
    df_2 = pd.DataFrame({'composite_key': ['004', '005', '006']})
    df_3 = pd.DataFrame({'composite_key': ['006', '007', '008']})

    with pytest.raises(ValueError):
        vc.validate_composite_keys_intersections(df_1, df_2, df_3, col='composite_key')


