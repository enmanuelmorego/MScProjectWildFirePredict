import matplotlib.pyplot as plt
import seaborn as sns

def plot_model_perf_by_folds(df_by_folds):
    _, axes = plt.subplots(2, 2,
                            figsize=(14, 10),
                            sharex=True,
                            sharey = True)

    # Split models into the two model families
    rf = df_by_folds[df_by_folds["model"].str.startswith("Random Forest")]
    lr = df_by_folds[df_by_folds["model"].str.startswith("Logistic Regression")]

    # Plot configurations:
    # row 0 = Random Forest
    # row 1 = Logistic Regression
    # col 0 = F1
    # col 1 = Recall

    plots = [(rf, "f1", axes[0, 0]),
            (lr, "f1", axes[0, 1]),
            
            (rf, "recall", axes[1, 0]),
            (lr, "recall", axes[1, 1])]
    titles = ["Random Forest",
            "Logistic Regression",
            "Random Forest",
            "Logistic Regression"]

    for (data, metric, ax), title in zip(plots, titles):

        sns.lineplot(data=data,
                    x="fold",
                    y=metric,
                    hue="model",
                    marker="o",
                    ax=ax)

        ax.set_title(title)
        ax.set_xlabel("Temporal fold")
        ax.set_ylabel(metric.replace("_", " ").title())
        ax.set_xticks(sorted(data["fold"].unique()))

        ax.legend(title="Model", fontsize=8)

    plt.tight_layout()
    plt.show()