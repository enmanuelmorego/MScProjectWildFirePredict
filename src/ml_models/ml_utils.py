import pandas as pd 
import numpy as np
import os
import re

from sklearn.base import BaseEstimator
from sklearn.model_selection import TimeSeriesSplit, RandomizedSearchCV, BaseCrossValidator
from sklearn.metrics import classification_report
from sklearn.metrics import (f1_score, roc_auc_score, precision_score, recall_score,
                             confusion_matrix, classification_report, precision_recall_curve)
from sklearn.base import clone
from typing import Any

class DateTimeSeriesSplit(BaseCrossValidator):
    """Custom cross-validation splitter class that splits the data based on dates rather than indices. 
    
    This class inherits from `scikit-learn`'s `BaseCrossValidator` class - It finds the unique dates in the dataset, and generates each fold split based on unique dates.
    It extracts the observations for the CrossValidation process if the X values falls in the given date period
    for training and validation periods. This ensures that the same dates are kept within the same folds

    Args:
        dates (pd.Series): Dates corresponding to each of the datapoints in the X object
        n_splits (int, optional): Number of cross-validation folds. Defaults to 5.

    Raises:
        ValueError: If the number of observations in `dates` does not
            match the data passed to `split()`.
        ValueError: If there are not enough unique dates for the
            requested number of splits.
    """    


    def __init__(self, dates: pd.Series, n_splits: int = 5):
        self.dates = pd.to_datetime(dates).reset_index(drop=True)
        self.n_splits = n_splits

    def split(self, X, y=None, groups=None):
        """Generate chronological train/validation indices."""

        if len(X) != len(self.dates): #type: ignore
            raise ValueError("X and dates must have the same number of observations")
        # Get unique dates to extract indeces of data points from
        unique_dates = np.sort(self.dates.unique())

        if len(unique_dates) <= self.n_splits:
            raise ValueError("There are not enough unique dates for the requested number of splits")

        # Create n_splits expanding training/validation blocks with a final validaiton block to 
        # validate all 5 blocks against
        date_blocks = np.array_split(unique_dates, self.n_splits + 1)

        # Create data for each of the training/validation folds
        for fold in range(self.n_splits):
            # Get the training dates for the fold 
            train_dates = np.concatenate(date_blocks[:fold + 1])
            # Get the validation set of dates
            validation_dates = date_blocks[fold + 1]
            # Extract the indices of the observations to use that fall within the unique
            # specified dates in train and validation sets
            train_idx      = np.flatnonzero(self.dates.isin(train_dates).to_numpy())
            validation_idx = np.flatnonzero(self.dates.isin(validation_dates).to_numpy())
            # Yield indeces for crossvalidation
            yield train_idx, validation_idx

    def get_n_splits(self, X=None, y=None, groups=None):
        return self.n_splits


def train_validate_test_temporal_split(df_in: pd.DataFrame, 
                                       sort_col:str = 'date', 
                                       train_size: float = 0.6, 
                                       val_size: float = 0.2, 
                                       test_size: float = 0.2) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Splits data into train, validation, and test sets based on temporal/date order 
    User specifies size of training set using the proportion value

    The function splits based on date. For example, if the user selects 60% split, and the 60% mark is 2020-01-01 but there are muiltiple observations on that date,
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
    df_train = df[df[sort_col] < split_train_date]
    df_validation = df[(df[sort_col] >= split_train_date) & (df[sort_col] < split_val_date)]
    df_test  = df[df[sort_col] >= split_val_date]

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

def get_best_model_folds(loaded_models: dict, cleaned_names: dict) -> pd.DataFrame:
    """Extract results of all the folds for the best selected model from hyperparameter tunning process

    Args:
        loaded_models (dict): Dictionary containing fitted RandomizedSearchCV objects
        cleaned_names (dict): Dictionary contaning the cleaned names of the Ml models to be used in the report

    Returns:
        pd.DataFrame: Fold-level performance metrics for the best hyperparameter configuration of each model

    Example:
        >>> fold_results = get_best_model_folds(loaded_models)
        >>> fold_results.head()
                     model  fold     f1  precision  recall  roc_auc
        0  logistic_reg_fwi     1  0.39       0.34    0.46     0.69
        1  logistic_reg_fwi     2  0.43       0.37    0.51     0.72
        2  logistic_reg_fwi     3  0.41       0.36    0.48     0.70
        3  logistic_reg_fwi     4  0.45       0.39    0.53     0.74
        4  logistic_reg_fwi     5  0.42       0.37    0.50     0.71
    """

    results = []

    for model_name, search in loaded_models.items():

        idx          = search.best_index_
        cleaned_name = cleaned_names.get(model_name, model_name)

        for fold in range(search.n_splits_):
            results.append({"model": cleaned_name,
                            "fold": fold + 1,
                            "f1": search.cv_results_[f"split{fold}_test_f1"][idx],
                            "precision": search.cv_results_[f"split{fold}_test_precision"][idx],
                            "recall": search.cv_results_[f"split{fold}_test_recall"][idx],
                            "roc_auc": search.cv_results_[f"split{fold}_test_roc_auc"][idx],})

    return pd.DataFrame(results).round(3).sort_values('model')

def evaluate_models(best_models: dict[str, RandomizedSearchCV], 
                    predictor_data: dict[str, pd.DataFrame], 
                    y: pd.Series) -> list[dict[str, Any]]:
    """Function to evalue models based on unseen data and using the models from a given dictionary

    Args:
        best_models (dict[str, RandomizedSearchCV]): Dictionary containing the models to use
        predictor_data (dict[str, pd.DataFrame]): Dictionary containing the predictor datasets. This could be test or validation
        y (pd.Series): Binary target labels

    Returns:
        list[dict]: List containing the evaluation results for each model
    """    
    # Initialise empty list for results 
    results = []

    for model_name, search in best_models.items():
        # Extract prediction dataset name from the model name 
        data_name = re.sub(r"random_forest_|logistic_reg_", "", model_name)

        # Extract predictor data
        X          = predictor_data[data_name]
        # Extract model
        best_model = search.best_estimator_

        # Test model
        y_pred = best_model.predict(X) #type: ignore
        y_prob = best_model.predict_proba(X)[:, 1] #type: ignore

        precision_curve, recall_curve, threshold = (precision_recall_curve(y, y_prob))

        results.append({"model": model_name,
                        "f1": f1_score(y, y_pred),
                        "precision": precision_score(y, y_pred),
                        "recall": recall_score(y, y_pred),
                        "roc_auc": roc_auc_score(y, y_prob),
                        "confusion_matrix": confusion_matrix(y, y_pred),
                        "classification_report": classification_report(y, y_pred, output_dict=True),
                        "precision_curve": precision_curve,
                        "recall_curve": recall_curve,
                        "threshold": threshold})
    return results

def summarise_model_results(results_list: list[dict[str, Any]], 
                            cleaned_names: dict,
                            sort_by_str: str = "F1") -> pd.DataFrame:
    # Initialise emtpy list to store results
    summary = []
    # Loop over results list
    for result in results_list:
        # Generate cleaned model name
        model_name_cleaned = cleaned_names.get(result['model'], result['model'])
        # Get TP, FP, TN, FN
        tn, fp, fn, tp = result["confusion_matrix"].ravel()
       
        summary.append({"Model": model_name_cleaned,
                        "TP": tp,
                        "FP": fp,
                        "TN": tn,
                        "FN": fn,
                        "F1": result["f1"],
                        "Precision": result["precision"],
                        "Recall": result["recall"],
                        "ROC_AUC": result["roc_auc"]})
    df_out = pd.DataFrame(summary).sort_values(sort_by_str, ascending=False).round(3)
    return df_out