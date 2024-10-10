import numpy as np
import pandas as pd
import time


class Cohyponyms:

    def __init__(self, categories, num_thresholds=51, only_best_threshold=False, similarity_metric='correlation'):

        self.categories = categories
        self.num_thresholds = num_thresholds
        self.similarity_metric = similarity_metric

        self.similarity_matrix = None
        self.only_best_threshold = only_best_threshold

        self.best_threshold = None
        self.overall_target_mean = None
        self.overall_category_mean = None

        self.guess_matrix = None
        self.accuracy_matrix = None

        self.threshold_list = np.linspace(-1, 1, self.num_thresholds)

        self.took = None

        self.item_results_df = None

        self.run_cohyponym_task()

    def run_cohyponym_task(self):
        print("Running Cohypohym Task")
        start_time = time.time()

        if self.categories.instance_feature_matrix is not None:
            if self.categories.similarity_matrix is None:
                self.categories.create_similarity_matrix(self.similarity_metric)
            self.similarity_matrix = self.categories.similarity_matrix
        else:
            raise ValueError("Categories object has no instance feature matrix")

        thresholds_column = np.array(self.threshold_list)[:, np.newaxis, np.newaxis]

        rounded_similarity_matrix = np.around(self.similarity_matrix, decimals=6)

        self.guess_matrix = (rounded_similarity_matrix >= thresholds_column).astype(int)

        cohyponym_matrix_reshaped = self.categories.instance_instance_matrix[np.newaxis, :, :]

        self.correct_matrix = (self.guess_matrix == cohyponym_matrix_reshaped).astype(int)

        same_category_mask = self.categories.instance_instance_matrix == 1
        different_category_mask = self.categories.instance_instance_matrix == 0

        self.same_correct_matrix = np.where(same_category_mask, self.correct_matrix, 0)
        self.different_correct_matrix = np.where(different_category_mask, self.correct_matrix, 0)

        self.same_correct_sums = self.same_correct_matrix.sum(axis=(1, 2)) - self.categories.num_instances
        self.different_correct_sums = self.different_correct_matrix.sum(axis=(1, 2))

        self.same_correct_item_sums = self.same_correct_matrix.sum(axis=-1)
        self.different_correct_item_sums = self.different_correct_matrix.sum(axis=-1)

        same_count_sum = self.categories.instance_instance_matrix.sum()
        self.same_count_sums = same_count_sum - self.categories.num_instances
        self.different_count_sums = self.categories.num_instances**2 - same_count_sum

        self.same_accuracies = self.same_correct_sums/self.same_count_sums
        self.different_accuracies = self.different_correct_sums / self.different_count_sums

        self.balanced_accuracies = (self.same_accuracies + self.different_accuracies) / 2
        self.balanced_accuracy_mean = np.amax(self.balanced_accuracies)
        self.took = time.time() - start_time

        sim_mask = np.triu(np.ones_like(self.similarity_matrix), k=1).astype(bool)
        flattened_sims = self.similarity_matrix[sim_mask]

        cohyponyms_mask = np.triu(np.ones_like(self.categories.instance_instance_matrix), k=1).astype(bool)
        flattened_cohyponyms = self.categories.instance_instance_matrix[cohyponyms_mask]
        self.correlation = np.corrcoef(flattened_sims, flattened_cohyponyms)[0, 1]

        np.savetxt('different_correct_matrix.txt', self.different_correct_matrix[-1,:,:], fmt='%d', delimiter=' ')

        self.get_item_results_dfs()
        self.get_threshold_results_df()
        self.get_best_item_results_df()
        self.get_best_category_results_df()

    def get_item_results_dfs(self):
        columns = ['threshold', 'instance', 'category', 'same', 'different', 'hits', 'misses', 'fas', 'crs',
                   'sensitivity', 'specificity', 'cr_rate', 'ba']
        self.item_results_df = pd.DataFrame(columns=columns)
        data_list = []

        for i in range(self.num_thresholds):
            threshold = self.threshold_list[i]
            for j in range(self.categories.num_instances):
                instance = self.categories.instance_list[j]
                category = self.categories.instance_category_dict[instance]
                hits = self.same_correct_item_sums[i, j]
                crs = self.different_correct_item_sums[i, j]

                if self.categories.instance_instance_matrix[j, :].sum() == 0:
                    same = 0
                    hits = 0
                else:
                    same = self.categories.instance_instance_matrix[j, :].sum() - 1
                    hits = self.same_correct_item_sums[i, j] - 1

                different = self.categories.num_instances - same - 1

                fas = different - crs
                misses = same - hits

                sensitivity = hits / (hits + misses)
                specificity = hits / (hits + fas)
                cr_rate = crs / (crs + fas)
                ba = (sensitivity + cr_rate) / 2

                item_data = [threshold, instance, category, same, different, hits, misses, fas, crs, sensitivity, specificity, cr_rate, ba]
                data_list.append(item_data)

        self.item_results_df = pd.DataFrame(data_list, columns=columns)

    def get_threshold_results_df(self):
        agg_columns = ['sensitivity', 'specificity', 'cr_rate', 'ba']

        # Define custom function for stderr to avoid lambda function issues
        def stderr(x):
            return np.std(x, ddof=1) / np.sqrt(x.count())

        # Map each column in agg_columns to the desired aggregation functions
        aggregations = {col: ['count', 'mean', 'std', stderr] for col in agg_columns}

        # Perform the aggregation
        self.threshold_result_df = self.item_results_df.groupby('threshold').agg(aggregations).reset_index()

        # Handling MultiIndex columns after aggregation
        self.threshold_result_df.columns = ['_'.join(col).rstrip('_') for col in
                                            self.threshold_result_df.columns.values]

    def get_best_item_results_df(self):
        max_ba_acc_mean_index = self.threshold_result_df['ba_mean'].idxmax()
        self.best_threshold = self.threshold_result_df.loc[max_ba_acc_mean_index, 'threshold']
        self.best_item_results_df = self.item_results_df[self.item_results_df['threshold'] == self.best_threshold]

    def get_best_category_results_df(self):
        import numpy as np

        # Correct the column name if necessary
        agg_columns = ['sensitivity', 'specificity', 'cr_rate', 'ba']  # Assuming 'ba' was meant to be 'ba_acc'

        # Define the aggregation functions, including a custom one for stderr
        def stderr(x):
            return np.std(x, ddof=1) / np.sqrt(len(x))

        aggregations = {
            'count': 'count',
            'mean': 'mean',
            'stdev': 'std',
            'stderr': stderr  # Using the custom standard error function
        }

        # Map each column to the aggregation functions
        agg_dict = {col: ['count', 'mean', 'std', stderr] for col in agg_columns}

        # Perform the groupby and aggregation for each category
        self.best_category_results_df = self.best_item_results_df.groupby('category').agg(agg_dict).reset_index()

        # Flatten the MultiIndex for columns
        self.best_category_results_df.columns = ['_'.join(col).rstrip('_') for col in
                                                 self.best_category_results_df.columns.values]

