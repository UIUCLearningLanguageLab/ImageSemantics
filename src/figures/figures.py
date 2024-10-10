import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import squareform


def plot_dendogram(sim_matrix, labels, output_path):
    distance_matrix = 1 - sim_matrix
    distance_matrix = (distance_matrix + distance_matrix.T) / 2
    np.fill_diagonal(distance_matrix, 0)
    # print(distance_matrix)

    condensed_distance_matrix = squareform(distance_matrix)
    Z = linkage(condensed_distance_matrix, 'average')
    plt.figure(figsize=(14, 7))
    dendrogram(Z, labels=labels, leaf_rotation=90, leaf_font_size=8)
    plt.title('Hierarchical Clustering Dendrogram')
    plt.xlabel('Sample index')
    plt.ylabel('Distance')
    plt.savefig(output_path + '_dendogram.png', dpi=300, bbox_inches='tight')

def create_heatmap(matrix, row_labels, column_labels, output_path, row_cluster=False, col_cluster=False):

    figure_height = 40
    figure_width = 20

    df = pd.DataFrame(data=matrix, index=row_labels, columns=column_labels)

    g = sns.clustermap(df, cmap='coolwarm', standard_scale=None, metric='euclidean',
                       method='single', figsize=(figure_width, figure_height), cbar_pos=None, dendrogram_ratio=(.01, .01),
                       row_cluster=row_cluster, col_cluster=col_cluster)
    plt.setp(g.ax_heatmap.get_yticklabels(), fontsize=8)

    plt.savefig(output_path + '_heatmap_dendogram.png', dpi=300, bbox_inches='tight')
    plt.clf()


def plot_bar_graph(data_matrix, row_labels, column_labels, title="", y_axis_label="y", save_path=None):
    barWidth = 0.3
    # Setting up the positions for the bars
    positions = np.arange(len(column_labels))

    fig, ax = plt.subplots()

    for i, row in enumerate(data_matrix):
        # Calculate position for each dataset
        r = [x + (barWidth * i) for x in positions]
        ax.bar(r, row, color=plt.cm.tab10(i), width=barWidth, edgecolor='grey', label=row_labels[i])

    # Adding labels and title
    ax.set_xlabel('Categories', fontweight='bold')
    ax.set_ylabel(y_axis_label, fontweight='bold')
    ax.set_title(title)

    # Setting the x-ticks to be in the middle of the grouped bars
    ax.set_xticks([r + barWidth for r in range(len(column_labels))])
    ax.set_xticklabels(column_labels)
    plt.xticks(rotation=90)
    ax.legend()
    plt.tight_layout()

    # Adding a legend
    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)