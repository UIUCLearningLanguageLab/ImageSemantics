import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


def create_heatmap(matrix, row_labels, column_labels, path, name):

    figure_height = 16
    figure_width = 16
    df = pd.DataFrame(data=matrix, index=row_labels, columns=column_labels)

    g = sns.clustermap(df, cmap='coolwarm', standard_scale=None, metric='euclidean',
                       method='single', figsize=(figure_width, figure_height), cbar_pos=None, dendrogram_ratio=(.01, .01),
                       row_cluster=True, col_cluster=True)

    plt.savefig(path + name + '_heatmap_dendogram.png')
    plt.clf()


def create_bar_graph(df, path, name, ylim=None):

    fig, ax = plt.subplots(figsize=(12, 12))

    plt.bar(df.iloc[:, 0].astype(str), df.iloc[:, 1], yerr=df.iloc[:, 2], capsize=5, edgecolor='black')

    ax.set_xticks(range(len(df)))
    ax.set_xticklabels(df.iloc[:, 0], rotation=90, fontsize=14)

    ax.set_title(f"{df.columns[0]} by {df.columns[1]}", fontsize=16)
    ax.set_xlabel(f"{df.columns[0]}", fontsize=14)  # add x-axis label
    ax.set_ylabel(f"{df.columns[1]}", fontsize=14)
    if ylim is not None:
        plt.ylim(ylim)
    plt.tight_layout()  # Automatically adjusts the spacing between subplots

    plt.savefig(path + name + '_bars.png', dpi=300, bbox_inches='tight')
    plt.clf()