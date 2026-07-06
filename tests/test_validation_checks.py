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