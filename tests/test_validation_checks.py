import utils.validation_checks as vc
import pandas as pd 
import pytest

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