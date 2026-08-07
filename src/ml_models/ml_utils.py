import pandas as pd 
import numpy as np

from sklearn.base import BaseEstimator
from sklearn.model_selection import TimeSeriesSplit, RandomizedSearchCV
from sklearn.metrics import classification_report
from sklearn.metrics import f1_score, roc_auc_score
from sklearn.base import clone


def train_validate_test_temporal_split(df_in: pd.DataFrame, 
                                       sort_col:str = 'date', 
                                       train_size: float = 0.6, 
                                       val_size: float = 0.2, 
                                       test_size: float = 0.2) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Splits data into train, validation, and test sets based on temporal/date order 
    User specifies size of training set using the proportion value

    The function splits based on date. For example, if the user selects 70% split, and the 70% mark is 2020-01-01 but there are muiltiple observations on that date,
    the function will include all observations on that date in the training set. This means that the split might not achieve the exact proportion. 
    
    This is a concsious design choice to avoid data leakage between train and test sets.

    Args:
        df_in (pd.DataFrame): Input dataframe to be split
        sort_col (str, optional): Column to sort the data by. Defaults to 'date'.
        train_size (float, optional): Proportion of the dataset to include in the train split. Defaults to 0.6
        val_size (float, optional): Proportion of the dataset to include in the validation split. Defaults to 0.2
        test_size (float, optional): Proportion of the dataset to include in the test split. Defaults to 0.2

    Raises:
        ValueError: If any of the size parameters are not between 0 and 1, or if they do not sum to 1

    Returns:
        tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: A tuple containing the train, validation, and test dataframes
    """
    if train_size >= 1 or train_size <=0:
        raise ValueError("ERROR Train size must be >0 and <1 as this represents a proportion")
    if val_size >= 1 or val_size <=0:
        raise ValueError("ERROR Validation size must be >0 and <1 as this represents a proportion")
    if test_size >= 1 or test_size <=0:
        raise ValueError("ERROR Test size must be >0 and <1 as this represents a proportion")
    if not abs(train_size + val_size + test_size) == 1.00:
        raise ValueError("ERROR The sum of train_size, val_size, and test_size must equal 1")

    # Sort dataframe
    df = df_in.sort_values(by = [sort_col])

    # Find the index to split based on `train_size` proportion
    split_train_idx = int(len(df) * train_size)
    split_val_idx   = int(len(df) * (train_size + val_size))
    # Find split date based on the index
    split_train_date = df.iloc[split_train_idx][sort_col]
    split_val_date   = df.iloc[split_val_idx][sort_col]

    # Split the dataframe into train and test based on the split date
    df_train = df[df[sort_col] <= split_train_date]
    df_validation = df[(df[sort_col] > split_train_date) & (df[sort_col] <= split_val_date)]
    df_test  = df[df[sort_col] > split_val_date]

    # Notify user of actual proportions
    actual_train_size = len(df_train) / len(df)
    actual_val_size   = len(df_validation) / len(df)
    actual_test_size  = len(df_test) / len(df)
    print(f"\nℹ️  INFO Train/Test split based on {sort_col}\n"
          f"Requested train size : {train_size:.4f}\n"
          f"Requested validation size : {val_size:.4f}\n"
          f"Requested test size : {test_size:.4f}\n"
          f"Actual train size    : {actual_train_size:.4f}\n"
          f"Actual validation size : {actual_val_size:.4f}\n"
          f"Actual test size     : {actual_test_size:.4f}")
    # return the train and test dataframes
    return df_train, df_validation, df_test

def random_search_cv(model: BaseEstimator,
                     X: pd.DataFrame,
                     y: pd.Series,
                     param_distributions: dict,
                     scoring: dict,
                     n_iter :int,
                     n_splits: int,
                     random_state:int = 42) -> RandomizedSearchCV:
    """Performs `Random Search CV` to find the best possible combination for hyperparameters for the model
    It uses `TimeSeriesSplit` to ensure that there is no temporal leakage 

    Args:
        model (BaseEstimator): Classification model - Random Forest, Logicstic Regression, etc
        X (pd.DataFrame): Predictor variable(s)
        y (pd.Series): Target label
        param_distributions (dict): Dictionary containing the possible hyperparameters to test, and for `RandomizedSearchVC` to sample from
        scoring (dict): Dictionary containing the scoring metrics to be used
        n_iter (int, optional): Number of hyperparameter combinations to test. For example, if there were `param_distributions = {'n_estimators': [100, 200, 500], 'max_depth': [10, 20, None], 'bootstrap': [True, False]}` there would be 3 x 3 x 2 = 18 parameter combinations to try. Setting `n_iter` = 5 would tell `RandomizedSearchCV` to only select 5 of the possible 18 random combination of these hyperparameters  
        n_splits (int, optional): Number of folds for TimeSeriesCrossValidation. Defaults to 8.
        random_state (int, optional): Sets the random seed to a specific value for reproducibility. Defaults to 42.

    Returns:
        RandomizedSearchCV: A RandomizedSearchCV object containing the results of the best performing model. Commonly used attributes are
        {best_estimator_ : Best fitted model,
         best_params_    : Dictionary containing the optimal
                           hyperparameter combination,
         best_score_     : Best cross-validation score,
         cv_results_     : Dictionary containing the results for all
                           hyperparameter combinations evaluated}
    """    
    # Initialise TimeSeriesSplit object to ensure there is no temporal leakage
    tscv = TimeSeriesSplit(n_splits = n_splits)
    # Perform the RandomizedSearch to find best HyperParameter combination
    search_hyperparams = RandomizedSearchCV(estimator = model,
                                            param_distributions = param_distributions,
                                            n_iter = n_iter,
                                            scoring = scoring,
                                            cv = tscv,
                                            random_state = random_state,
                                            n_jobs = 1,
                                            refit = 'f1',
                                            verbose = True)
    
    search_hyperparams.fit(X, y)
    return search_hyperparams

def model_crossvalidation(model: BaseEstimator,
                           X: pd.DataFrame, 
                           y: pd.Series, 
                           model_name: str, 
                           n_splits: int = 8, 
                           verbose: bool = False) -> dict:
    """Performs crossvalidation on training data for a given ML model.
    A fresh cloned model is supplied to each crossvalidation fold. 
    The function computes the F1-Score, ROC AUC score, and classification report for every fold along with the 
    mean performance across all folds

    Args:
        model (BaseEstimator): Classification model - Random Forest, Logicstic Regression, etc
        X (pd.DataFrame): Predictor variables
        y (pd.DataFrame): Target labels
        model_name (str): Name to identify the trained model
        n_splits (int, optional): Number of folds for TimeSeriesCrosValidation. Defaults to 8.
        verbose (bool, optional): Boolean flag to choose whether to print details per fold or not. Defaults to False.

    Returns:
        dict: Dictionary containing the F1 and ROC AUC score for each fold and the overal mean F1-score along with ROC AUC score
    """    
    # Initialise objects
    tscv = TimeSeriesSplit(n_splits = n_splits)
    f1_scores = []
    auc_scores = []
    reports = []
    model_scores = {model_name: {}}

    for i, (train_index, test_index) in enumerate(tscv.split(X)):
        print(f"Model name: {model_name}. Fold {i}", end = "\r")
        # Split data based on cv fold
        X_train_cv = X.iloc[train_index]
        y_train_cv = y.iloc[train_index]

        X_test_cv = X.iloc[test_index]
        y_test_cv = y.iloc[test_index]

        # Create a fresh model for this fold
        model_cv = clone(model)
        # Train model
        model_cv.fit(X_train_cv, y_train_cv)
        # Generate predictions
        y_pred = model_cv.predict(X_test_cv)
        # Extract the probabilities of the fire class
        y_prob = model_cv.predict_proba(X_test_cv)[:, 1]

        # Evaluate
        f1score = f1_score(y_test_cv, y_pred)
        f1_scores.append(f1score)
        model_scores[model_name][f"F1 Score fold {i}"] = f1score

        auc_score = roc_auc_score(y_test_cv, y_prob)
        auc_scores.append(auc_score)
        model_scores[model_name][f"AUC Score fold {i}"] = auc_score


        report = classification_report(y_test_cv, y_pred, output_dict=True)
        reports.append(pd.DataFrame(report).T)
        if verbose:
            print(f"Fold {i}: \n\t{f1score:.3f}\n\t{auc_score:.3f}")
            print(classification_report(y_test_cv, y_pred))
            print(".....................................")
    f1_mean_score = np.mean(f1_scores)
    auc_mean_score = np.mean(auc_scores) 

    avg_report = (pd.concat(reports).groupby(level=0).mean())
    print(f"\n========== Model: {model_name} ==========\nMean F1 Score: {f1_mean_score:.3f}\nMean AUC Score: {auc_mean_score:.3f}\nTotal folds: {n_splits}\nAverage Class Report\n{avg_report}")
    model_scores[model_name]["F1 Mean Score"]  = f1_mean_score
    model_scores[model_name]["AUC Mean Score"] = auc_mean_score
    model_scores[model_name]["Average Classification Report"] = avg_report

    return model_scores
