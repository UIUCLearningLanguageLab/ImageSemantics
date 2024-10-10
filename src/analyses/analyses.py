from ..figures import figures
import numpy as np


def sort_matrix(data_matrix, column_labels):
    sorted_indices = np.argsort(data_matrix[0])
    sorted_matrix = data_matrix[:, sorted_indices]
    sorted_category_list = [column_labels[i] for i in sorted_indices]
    return sorted_matrix, sorted_category_list


def generate_ba_bar_graphs(cohyponym_list, df_name_list):
    category_ba_mean_dict_list = []
    for cohyponym in cohyponym_list:
        df = cohyponym.best_category_results_df
        category_ba_mean_dict = {}
        category_ba_stderr_dict = {}
        for row in df.itertuples(index=False):
            category = row.category
            ba = row.ba_mean
            stderr = row.ba_stderr
            category_ba_mean_dict[category] = ba
            category_ba_stderr_dict[category] = stderr
        category_ba_mean_dict_list.append(category_ba_mean_dict)

    num_dfs = len(cohyponym_list)
    num_categories = len(category_ba_mean_dict_list[0])
    category_list = list(category_ba_mean_dict_list[0].keys())
    ba_mean_matrix = np.zeros([num_dfs, num_categories])

    for i in range(num_dfs):
        for j in range(num_categories):
            category = category_list[j]
            if category in category_ba_mean_dict_list[i]:
                ba_mean_matrix[i, j] = category_ba_mean_dict_list[i][category]

    print(num_dfs, num_categories, ba_mean_matrix)

    sorted_matrix, sorted_category_list = sort_matrix(ba_mean_matrix, category_list)
    figures.plot_bar_graph(sorted_matrix, df_name_list, sorted_category_list, y_axis_label="Category Balanced Accuracy",
                           save_path="../analyses/category_balanced_accuracy.png")


def generate_category_frequency_bar_graphs(df_list, df_name_list):
    category_freq_dict_list = []

    for df in df_list:
        category_freq_dict = {}
        for row in df.itertuples(index=False):
            category = row.category
            count = row.count
            category_freq_dict[category] = count
        category_freq_dict_list.append(category_freq_dict)

    num_dfs = len(df_list)
    num_categories = len(category_freq_dict_list[0])
    category_list = list(category_freq_dict_list[0].keys())
    freq_matrix = np.zeros([num_dfs, num_categories])

    for i in range(num_dfs):
        for j in range(num_categories):
            category = category_list[j]
            if category in category_freq_dict_list[i]:
                freq_matrix[i, j] = category_freq_dict_list[i][category]

    sorted_matrix, sorted_category_list = sort_matrix(freq_matrix, category_list)
    figures.plot_bar_graph(sorted_matrix, df_name_list, sorted_category_list, y_axis_label="Category Frequency",
                           save_path="../analyses/category_frequency.png")

    # create the proportion
    denominator = freq_matrix[0, :]
    denominator_reshaped = denominator.reshape(1, -1)
    proportion_matrix = freq_matrix[1:, :] / denominator_reshaped
    sorted_matrix, sorted_category_list = sort_matrix(proportion_matrix, category_list)
    figures.plot_bar_graph(sorted_matrix, df_name_list, sorted_category_list,
                           y_axis_label="Frequency Proportion of Whole Image",
                           save_path="../analyses/category_proportion.png")
