import os
import sys
import numpy as np
image_semantics_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(image_semantics_dir)
from src.dataset import datasets
from src.models import matrices
from src.figures import figures


def main():


    np.set_printoptions(precision=3, suppress=True)
    json_path = '../data/'
    the_dataset = datasets.Dataset()
    the_dataset.load_dataset(json_path)

    the_dataset.filter_dataset()

    category_by_image_matrix = matrices.CategoryByImageMatrix(the_dataset,
                                                              use_categories=True,
                                                              use_subcategories=False,
                                                              num_split_categories=4)
    figures.create_heatmap(category_by_image_matrix.matrix,
                           category_by_image_matrix.row_label_list,
                           category_by_image_matrix.column_label_list,
                           "../analyses/iyer/",
                           "raw_matrix_heatmap.png")

    category_by_image_matrix.normalize_matrix("ppmi")
    figures.create_heatmap(category_by_image_matrix.matrix,
                           category_by_image_matrix.row_label_list,
                           category_by_image_matrix.column_label_list,
                           "../analyses/iyer/",
                           "ppmi_matrix_heatmap.png"
                           )

    category_by_image_matrix.svd_matrix(12)
    figures.create_heatmap(category_by_image_matrix.matrix,
                           category_by_image_matrix.row_label_list,
                           category_by_image_matrix.column_label_list,
                           "../analyses/iyer/",
                           "svd_matrix_heatmap.png",
                           col_cluster=True)

    category_by_image_matrix.compute_similarity_matrix("correlation")
    figures.create_heatmap(category_by_image_matrix.sim_matrix,
                           category_by_image_matrix.row_label_list,
                           category_by_image_matrix.row_label_list,
                           "../analyses/iyer/",
                           "sim_matrix_heatmap.png",
                           col_cluster=True
                           )

    print(category_by_image_matrix.row_label_list)
    categorization.mpl_classifier()


if __name__ == "__main__":
    main()
