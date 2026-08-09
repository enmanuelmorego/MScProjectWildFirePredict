import os 

from joblib import load

def get_best_models(models_dir: str = "data/MLModels") -> dict:
    """After hyperparameter tuning is complete and the best model saved to disk, this function
    searches from the best models which are saved to disk and loads them as a dictionary 

    Loads all files with suffix .joblib from `models_dir` 
    Args:
        models_dir (str, optional): Base path of where the models are stored. Defaults to "data/MLModels".

    Returns:
        dict: Dictionary containing all of the available models in `models_dir`

    Example:
        >>> best_models = get_best_models()
        >>> best_models
        {"rf_fwi_best": RandomForestClassifier(...),
         "rf_sentinel_best": RandomForestClassifier(...),
         "rf_hybrid_best": RandomForestClassifier(...),
         "lr_fwi_best": LogisticRegression(...),
         "lr_sentinel_best": LogisticRegression(...),
         "lr_hybrid_best": LogisticRegression(...)
        }
    """
    # Load trained models 
    loaded_models = {}
    for file_name in os.listdir("data/MLModels"):
        if file_name.endswith(".joblib"):
            model_name = file_name.replace(".joblib", "")
            loaded_models[model_name] = load(os.path.join(models_dir, file_name))
    return loaded_models