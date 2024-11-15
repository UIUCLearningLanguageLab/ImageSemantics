import os
import sys
import numpy as np
import pandas as pd
image_semantics_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(image_semantics_dir)
from src.dataset import datasets
from src.analyses import analyses
from src.models import matrices
from src.figures import figures
from src.tasks import categories, cohyponyms2


def main():

    np.set_printoptions(precision=3, suppress=True)
    dataset_name_list = ['Original']
    dataset_path_list = ['../data']
    # dataset_name_list = ['Original']
    # dataset_path_list = ['../data']
    output_path = "../analyses/"
    num_datasets = len(dataset_name_list)
    similarity_metric = "correlation"
    num_subcategories = 4
    num_svd_dimensions = 12
    num_thresholds = 51

    category_df_list = []
    cohyponym_task_df_list = []

    for i in range(num_datasets):
        print(f"\nProcessing Dataset {dataset_name_list[i]}")
        new_dataset = datasets.Dataset()
        new_dataset.load_dataset(dataset_path_list[i])
        if num_subcategories:
            new_dataset.split_categories(num_subcategories)

        category_df_list.append(new_dataset.category_df)
        new_dataset.remove_subcategory_none_rows()

        '''
        dataset has 4 df
        instance_df, which has every instance in the whole dataset, its category, subcategory, color, etc.
        category_df, where the sum frequency of each category
        image_df
        subcategory_df has each subcaetegory, its freq and its category
            food1, food, 21312
            food2, food, 21343
        '''

        new_matrix = matrices.CategoryByImageMatrix(new_dataset)
        '''
        matrix is passed the dataset, and it will be of size num_subcategorizes by num images
        '''

        figures.create_heatmap(new_matrix.matrix, new_matrix.row_label_list, new_matrix.column_label_list,
                               output_path+dataset_name_list[i]+"_raw_matrix")
        new_matrix.normalize_matrix("ppmi")
        figures.create_heatmap(new_matrix.matrix, new_matrix.row_label_list, new_matrix.column_label_list,
                               output_path+dataset_name_list[i]+"_ppmi_matrix")
        new_matrix.svd_matrix(num_svd_dimensions)
        figures.create_heatmap(new_matrix.matrix, new_matrix.row_label_list, new_matrix.column_label_list,
                               output_path+dataset_name_list[i]+"_svd_matrix")
        new_matrix.compute_similarity_matrix(similarity_metric)
        figures.create_heatmap(new_matrix.sim_matrix, new_matrix.row_label_list, new_matrix.row_label_list,
                               output_path+dataset_name_list[i]+"_sim_matrix")

        figures.plot_dendogram(new_matrix.sim_matrix, new_matrix.row_label_list,
                               output_path+dataset_name_list[i]+"_sim")

        instance_category_dict = pd.Series(new_dataset.subcategory_df['category'].values,
                                           index=new_dataset.subcategory_df['subcategory']).to_dict()

        the_categories = categories.Categories(instance_category_dict)
        the_categories.set_instance_feature_matrix(new_matrix.matrix, new_matrix.row_index_dict)
        the_cohyponym_task = cohyponyms2.Cohyponyms(the_categories, similarity_metric=similarity_metric, num_thresholds=num_thresholds)
        cohyponym_task_df_list.append(the_cohyponym_task)

        print(the_cohyponym_task.item_results_df)
        print(the_cohyponym_task.threshold_result_df)
        print(the_cohyponym_task.best_item_results_df)
        print(the_cohyponym_task.best_category_results_df)
        print(the_cohyponym_task.balanced_accuracy_mean)

    # analyses.generate_category_frequency_bar_graphs(category_df_list, dataset_name_list)
    # analyses.generate_ba_bar_graphs(cohyponym_task_df_list, dataset_name_list)


if __name__ == "__main__":
    main()
