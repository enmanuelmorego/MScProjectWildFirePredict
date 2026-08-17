import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd 

def plot_model_perf_by_folds(df_by_folds: pd.DataFrame, 
                             metric: str, 
                             model_family:str,
                             save_plot = True,
):
    """Creates line chart containing the performance valeus (F1) for each of the crossvalidation folds 

    Args:
        df_by_folds (pd.DataFrame): DataFrame containing the results and metrics for each of the folds for the models 
        metric (str): Metric to extract and use in plot
        model_family (str): Whether it is Logistic Regression or Random forest as one model is ploted at the time for better readability
        save_plot (bool, optional): Boolean flag to determine whether the plot will be saved to disk or not. Defaults to True.
    """    
    data = df_by_folds[df_by_folds["model"].str.startswith(model_family)]

    _, ax = plt.subplots(figsize=(10, 6))

    sns.lineplot(data=data,
                 x="fold",
                 y=metric,
                 hue="model",
                 marker="o",
                 linewidth=2,
                 ax=ax)

    ax.set_title(f"{model_family} — "
                 f"{metric.replace('_', ' ').title()} Across Temporal Folds")

    ax.set_xlabel("Temporal fold")
    ax.set_ylabel(metric.replace("_", " ").title())
    ax.set_xticks(sorted(data["fold"].unique()))

    ax.set_ylim(0, 1)

    plt.tight_layout()

    if save_plot:
        plt.savefig(f"outputs/plots/{model_family}_{metric}_folds.png",
                    dpi=300,
                    bbox_inches="tight")

    plt.show()

