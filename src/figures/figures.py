import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


def create_heatmap(matrix, row_labels, column_labels):

    # Create a data frame with the SVD matrix'
    num_components = matrix.shape[1]
    df = pd.DataFrame(data=matrix, index=row_labels, columns=column_labels)

    # Create a heatmap plot with clustering and dendograms
    sns.clustermap(df, cmap='coolwarm', standard_scale=None, metric='euclidean',
                   method='ward', figsize=(10, 10), cbar_pos=None, dendrogram_ratio=(.1, .2),
                   row_cluster=True, col_cluster=True)

    # Show the plot
    plt.show()
