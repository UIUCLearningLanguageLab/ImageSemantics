import os
import sys
image_semantics_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(image_semantics_dir)
from image_semantics.src.dataset import datasets
from image_semantics.src.models import matrices
from image_semantics.src.figures import figures
import numpy as np


def main():
    np.set_printoptions(precision=3, suppress=True)
    pickle_path = '../data/DTW1_2023_03_16_154635.pkl'

    the_dataset = datasets.Dataset()
    the_dataset.load_dataset(pickle_path)

    category_by_image_matrix = matrices.CategoryByImageMatrix(the_dataset,
                                                              use_categories=True,
                                                              use_subcategories=False,
                                                              num_split_categories=2)
    # figures.create_heatmap(category_by_image_matrix.matrix,
    #                        category_by_image_matrix.row_label_list,
    #                        category_by_image_matrix.column_label_list)

    category_by_image_matrix.normalize_matrix("ppmi")
    # figures.create_heatmap(category_by_image_matrix.matrix,
    #                        category_by_image_matrix.row_label_list,
    #                        category_by_image_matrix.column_label_list)

    category_by_image_matrix.svd_matrix(12)
    # figures.create_heatmap(category_by_image_matrix.matrix,
    #                        category_by_image_matrix.row_label_list,
    #                        category_by_image_matrix.column_label_list)

    category_by_image_matrix.compute_similarity_matrix("correlation")
    figures.create_heatmap(category_by_image_matrix.sim_matrix,
                           category_by_image_matrix.row_label_list,
                           category_by_image_matrix.row_label_list)

    #print(category_by_image_matrix.row_label_list)
    #categorization.mpl_classifier()


if __name__ == "__main__":
    main()
