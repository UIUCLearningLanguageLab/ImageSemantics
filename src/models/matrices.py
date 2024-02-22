import numpy as np
import copy
import random


class EmbeddingMatrix:

    def __init__(self, dataset):
        self.dataset = copy.deepcopy(dataset)
        self.matrix = None
        self.sim_matrix = None

        self.row_label_list = None
        self.row_index_dict = None
        self.num_rows = None

        self.column_label_list = None
        self.column_index_dict = None
        self.num_columns = None

    def row_normalize(self):
        row_sums = self.matrix.sum(axis=1, keepdims=True)
        normalized_matrix = self.matrix / row_sums
        self.matrix = normalized_matrix

    def ppmi_normalize(self):
        eps = 1e-10
        self.matrix[self.matrix == 0] = eps

        # calculate row, column, and grand total sums
        row_totals = self.matrix.sum(axis=1)
        col_totals = self.matrix.sum(axis=0)
        total_sum = self.matrix.sum()

        # calculate probabilities
        row_probs = row_totals / total_sum
        col_probs = col_totals / total_sum

        # calculate PMI values
        pmi = np.log2((self.matrix+eps) / (row_probs[:, None] * col_probs[None, :] + eps))
        pmi[np.isnan(pmi)] = 0  # set NaN values to 0
        pmi[pmi < 0] = 0  # set negative values to 0
        self.matrix = pmi

    def normalize_matrix(self, method="None"):
        print("Normalizing Matrix Using Method={}".format(method))
        if method == "rows":
            self.row_normalize()
        if method == "ppmi":
            self.ppmi_normalize()

    def compute_similarity_matrix(self, method="cosine"):
        print("Computing Similarity Matrix Using Method={}".format(method))
        if method == "correlation":
            self.sim_matrix = np.corrcoef(self.matrix)

    def svd_matrix(self, d, weighted=False):
        print("Reducing Method Using SVD to {} Dimensions".format(d))
        u, s, v = np.linalg.svd(self.matrix, full_matrices=False)
        if not weighted:
            self.matrix = u[:, :d]
        else:
            self.matrix = np.dot(u[:, :d], np.diag(s[:d]))

        self.num_columns = d
        s_normalized = s / np.sum(s)
        s_top_d = s_normalized[:d]
        self.column_label_list = [f"SV{i+1}_{val:.5f}" for i, val in enumerate(s_top_d)]
        self.column_index_dict = {item: index for index, item in enumerate(self.column_label_list)}


class CategoryByImageMatrix(EmbeddingMatrix):

    def __init__(self, dataset, use_categories=True, use_subcategories=False, num_split_categories=0):
        super().__init__(dataset)
        self.use_categories = use_categories
        self.use_subcategories = use_subcategories
        self.num_split_categories = num_split_categories

        self.create_matrix()

    def create_matrix(self):

        if self.use_categories:
            if self.num_split_categories > 0:
                self.dataset.instance_df[
                    'subcategory'] = self.dataset.instance_df[
                    'category'].apply(lambda x: f"{x}{random.randint(1, self.num_split_categories)}")

            else:
                self.dataset.instance_df['subcategory'] = self.dataset.instance_df['category']

        else:
            if self.use_subcategories:
                # check to make sure the subcategories are values other than None
                has_non_none_value_string = (self.dataset.instance_df['subcategory'] != "None").any()

                if not has_non_none_value_string:
                    raise Exception("ERROR: all subcategories are set to None")

        self.dataset.instance_df['pvf'] = self.dataset.instance_df['participant'].astype(str) + "_" + self.dataset.instance_df['video'].astype(str) + "_" + \
                             self.dataset.instance_df['frame'].astype(str)
        self.dataset.image_df['pvf'] = self.dataset.image_df['participant'].astype(str) + "_" + self.dataset.image_df['video'].astype(str) + "_" + self.dataset.image_df[
            'frame'].astype(str)

        # # Step 2: Aggregate instance_df by the unique identifier and category
        agg_instance_df = self.dataset.instance_df.groupby(['pvf', 'subcategory']).size().reset_index(name='count')

        # # Step 3: Pivot the aggregated data
        pivot_df = agg_instance_df.pivot(index='subcategory', columns='pvf', values='count')

        # # Step 4: Fill missing values with 0
        pivot_df = pivot_df.fillna(0)

        # # Step 5: Convert to NumPy matrix
        self.matrix = pivot_df.to_numpy()

        self.row_label_list = pivot_df.index.tolist()
        self.column_label_list = pivot_df.columns.tolist()

