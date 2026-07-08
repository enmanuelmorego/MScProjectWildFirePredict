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
# TEST validate_composite_keys()
# ==========================================
def test_validate_composite_keys_all_valid_empty_missed():
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
    assert vc.validate_composite_keys(df_feat, df_sampled, df_missed) == True

def test_validate_composite_keys_all_valid_with_missed():
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
    assert vc.validate_composite_keys(df_feat, df_sampled, df_missed) == True