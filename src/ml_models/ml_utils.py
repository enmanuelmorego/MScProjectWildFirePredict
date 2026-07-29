import pandas as pd 
import numpy as np

from sklearn.base import BaseEstimator
from sklearn.model_selection import TimeSeriesSplit, RandomizedSearchCV
from sklearn.metrics import classification_report
from sklearn.metrics import f1_score, roc_auc_score
from sklearn.base import clone


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

def random_search_cv(model: BaseEstimator,
                     X: pd.DataFrame,
                     y: pd.Series,
                     param_distributions: dict,
                     n_iter = 50,
                     n_splits = 8,
                     scoring = "F1",
                     random_state = 42) -> dict:

    tscv = TimeSeriesSplit(n_splits = n_splits)
    search_hyperparams = RandomizedSearchCV(estimator = model,
                                            param_distributions = param_distributions,
                                            n_iter = n_iter,
                                            scoring = scoring,
                                            cv = tscv,
                                            random_state = random_state,
                                            n_jobs = 1,
                                            refit = True,
                                            verbose = True)
    search_hyperparams.fit(X, y)
    return {"best_model": search_hyperparams.best_estimator_,
            "best_params": search_hyperparams.best_params_,
            "best_score": search_hyperparams.best_score_,
            "cv_results": search_hyperparams.cv_results_}

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
        n_splits (int, optional): Number of folds for cross-validation. Defaults to 8.
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
