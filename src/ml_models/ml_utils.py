import pandas as pd 

def train_test_temporal_split(df_in: pd.DataFrame, sort_col:str = 'date', train_size: float = 0.7) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Splits data into train and test sets based on temporal/date order 
    User specifies size of training set using the proportion value

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
    
    df = df_in.sort_values(by = [sort_col])
    
    split_idx = int(len(df) * train_size)

    train_df = df.iloc[:split_idx]
    test_df  = df.iloc[split_idx:]

    return train_df, test_df