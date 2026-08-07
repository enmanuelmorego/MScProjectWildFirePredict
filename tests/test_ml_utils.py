import ml_models.ml_utils as mu
import pandas as pd

def test_train_validate_test_temporal_split_basic_case():
    # Create a sample dataframe with dates and composite keys
    df = pd.DataFrame({'date': pd.date_range(start='2023-01-01', periods=10, freq='D'),
                       'composite_key': [f'00{i}{i+1}' for i in range(10)]})

    # Perform the train/validate/test split
    df_train, df_validation, df_test = mu.train_validate_test_temporal_split(df, sort_col='date', train_size=0.6, val_size=0.2, test_size=0.2)

    # Check the lengths of the resulting dataframes
    assert len(df_train) == 6  # 60% of 10
    assert len(df_validation) == 2  # 20% of 10
    assert len(df_test) == 2  # 20% of 10

    # Check that the dates are in the correct order
    assert df_train['date'].max() < df_validation['date'].min()
    assert df_validation['date'].max() < df_test['date'].min()

def test_train_validate_test_temporal_split_duplicated_dates():
    df = pd.DataFrame({"composite_key": [f'00{i}{i+1}' for i in range(10)],
                        "date": pd.to_datetime(["2020-01-01",  
                                                "2020-01-02",  
                                                "2020-01-03",  
                                                "2020-01-04",  
                                                "2020-01-05",
                                                "2020-01-06",
                                                "2020-01-06",  # Duplicate date
                                                "2020-01-08",
                                                "2020-01-10",
                                                "2020-01-10"])
                                                })
    # Perform the train/validate/test split
    df_train, df_validation, df_test = mu.train_validate_test_temporal_split(df, sort_col='date', train_size=0.6, val_size=0.2, test_size=0.2)

    assert len(df_train) == 5 # 50% as the boundary value gets inluded in validation set
    assert len(df_validation) == 3 # 30% of 10
    assert len(df_test) == 2 # 20% of 10