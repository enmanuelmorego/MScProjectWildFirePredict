import pandas as pd 

def train_test_temporal_split(df_in: pd.DataFrame, sort_col:str = 'date', train_size: float = 0.7) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Splits data into train and test sets based on temporal/date order 
    User specifies size of training set using the proportion value

    The function splits based on date. For example, if the user selects 70% split, and the 70% mark is 2020-01-01 but there are muiltiple observations on that date,
    the function will include all observations on that date in the training set. This means that the split might not achieve the exact proportion. 
    
    This is a concsious design choice to avoid data leakage between train and test sets.

    Args:
        df_in (pd.DataFrame): Input dataframe to be split
        sort_col (str, optional): Column to sort the data by. Defaults to 'date'.
        train_size (float, optional): Proportion of the dataset to include in the train split. Defaults to 0.7

    Raises:
        ValueError: If train_size is not between 0 and 1

    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: A tuple containing the train and test dataframes
    """
    if train_size >= 1 or train_size <=0:
        raise ValueError("ERROR Train size must be >0 and <1 as this represents a proportion")
    # Sort dataframe
    df = df_in.sort_values(by = [sort_col])
    # Find the index to split based on `train_size` proportion
    split_idx = int(len(df) * train_size)
    # Find split date based on the index
    split_date = df.iloc[split_idx][sort_col]
    # Split the dataframe into train and test based on the split date
    df_train = df[df[sort_col] <= split_date]
    df_test  = df[df[sort_col] > split_date]
    # Notify user of actual proportions
    actual_train_size = len(df_train) / len(df)
    actual_test_size  = len(df_test) / len(df)
    print(f"\nℹ️  INFO Train/Test split based on {sort_col}\n"
          f"Requested train size : {train_size:.4f}\n"
          f"Actual train size    : {actual_train_size:.4f}\n"
          f"Actual test size     : {actual_test_size:.4f}")
    # return the train and test dataframes
    return df_train, df_test