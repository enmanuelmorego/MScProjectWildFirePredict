import matplotlib.pyplot as plt
import seaborn as sns

def plot_model_perf_by_folds(df_by_folds, 
                             metric: str, 
                             model_family:str,
                             save_plot = True,
):
    data = df_by_folds[df_by_folds["model"].str.startswith(model_family)]

    fig, ax = plt.subplots(figsize=(10, 6))

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

    ax.set_ylim(0, 0.7)

    plt.tight_layout()

    if save_plot:
        plt.savefig(f"outputs/plots/{model_family}_{metric}_folds.png",
                    dpi=300,
                    bbox_inches="tight")

    plt.show()