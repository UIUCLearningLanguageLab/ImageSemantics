import copy
import os
import sys
import shutil
import numpy as np
import pandas as pd
image_semantics_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(image_semantics_dir)
from src.dataset import datasets
from src.models import matrices
from src.figures import figures
from src.tasks import cohyponyms


def main():
    np.set_printoptions(precision=3, suppress=True)
    pickle_path = '../data/DTW1_2023_04_10_191348.pkl'
    output_path = '../analyses/split_categories'
    if os.path.exists(output_path):
        shutil.rmtree(output_path)
    os.mkdir(output_path)
    os.mkdir(output_path + "/figures")

    svd_range = [3, 20]
    num_splits = 8
    num_thresholds = 51

    category_dataset = datasets.Dataset()
    category_dataset.load_dataset(pickle_path)
    category_dataset.output_descriptive_info(output_path)

    split_category_dataset = copy.deepcopy(category_dataset)
    subcategory_dataset = copy.deepcopy(category_dataset)
    split_category_dataset.create_random_subcategories(num_splits)

    # category_by_image_matrix = matrices.CategoryByImageMatrix(category_dataset,
    #                                                           use_categories=True,
    #                                                           use_subcategories=False)

    split_category_by_image_matrix = matrices.CategoryByImageMatrix(split_category_dataset,
                                                                    use_categories=False,
                                                                    use_subcategories=True)

    # subcategory_by_image_matrix = matrices.CategoryByImageMatrix(subcategory_dataset,
    #                                                              use_categories=False,
    #                                                              use_subcategories=True)
    #
    # dataset_list = [category_dataset, split_category_dataset, subcategory_dataset]
    # matrix_list = [category_by_image_matrix, split_category_by_image_matrix, subcategory_by_image_matrix]
    # matrix_name_list = ["categoryXimage", "splitcategoryXimage", "subcategoryXimage"]
    dataset_list = [split_category_dataset]
    matrix_list = [split_category_by_image_matrix]
    matrix_name_list = ["splitcategoryXimage"]

    for i in range(len(matrix_list)):

        figures.create_heatmap(matrix_list[i].matrix,
                               matrix_list[i].row_label_list, matrix_list[i].column_label_list,
                               output_path+"/figures/", matrix_name_list[i])


        matrix_list[i].normalize_matrix("ppmi")
        figures.create_heatmap(matrix_list[i].matrix,
                               matrix_list[i].row_label_list, matrix_list[i].column_label_list,
                               output_path+"/figures/", matrix_name_list[i]+"_ppmi")

        subcategory_category_dict = dataset_list[i].get_subcategory_category_dict()
        if "error image" in subcategory_category_dict:
            del subcategory_category_dict["error image"]

        ba_results_list = []
        for j in range(svd_range[0], svd_range[1]+1):

            matrix_copy = copy.deepcopy(matrix_list[i])
            matrix_copy.svd_matrix(j)

            figures.create_heatmap(matrix_copy.matrix,
                                   matrix_copy.row_label_list, matrix_copy.column_label_list,
                                   output_path + "/figures/", matrix_name_list[i] + "_ppmi_svd" + str(j))

            matrix_copy.compute_similarity_matrix("correlation")
            figures.create_heatmap(matrix_copy.sim_matrix,
                                   matrix_copy.row_label_list, matrix_copy.row_label_list,
                                   output_path + "/figures/",
                                   matrix_name_list[i] + "_ppmi_svd" + str(j) + "_corrsim")

            cohyps = cohyponyms.CohyponymTask(subcategory_category_dict,
                                              matrix_copy.sim_matrix,
                                              matrix_copy.row_index_dict,
                                              num_thresholds=num_thresholds, categories_from_file=False)

            ba_results_list.append(cohyps.best_category_ba_df)
            # best_category_ba_df.columns = ['category', 'best_overall_threshold', 'ba_mean', 'ba_std', 'n']

            df_sorted = cohyps.best_category_ba_df.sort_values(by='ba_mean')

            figures.create_bar_graph(df_sorted[["category", "ba_mean", 'ba_std']],
                                     output_path + "/figures/",
                                     matrix_name_list[i] + "_ppmi_svd" + str(j) + "_ba",
                                     [0.4, 1.0])

        combined_df = pd.concat(ba_results_list, keys=range(svd_range[0], svd_range[1]+1), names=['SVD_DIms', 'Index'])

        overall_ba_df = combined_df.groupby('SVD_DIms')['ba_mean'].agg(['mean', lambda x: np.std(x) / np.sqrt(len(x))])
        average_category_ba_df = overall_ba_df.reset_index().rename(columns={'mean': 'BA Mean', '<lambda_0>': 'BA STDERR'})

        figures.create_bar_graph(average_category_ba_df, output_path + "/figures/", matrix_name_list[i] + "_ppmi_overall_ba", [0.4, 1.0])


if __name__ == "__main__":
    main()
