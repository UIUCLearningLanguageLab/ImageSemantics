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

    def init_rows(self):
        # print("BEGINNING")
        # print(len(self.dataset.category_name_list), len(self.dataset.category_index_dict), len(self.dataset.category_dict), self.dataset.num_categories)

        if not self.use_subcategories and self.use_categories and self.num_split_categories > 0:
            self.split_categories(self.num_split_categories)

        #print(len(self.row_label_list), len(self.row_index_dict), self.num_rows)
        # print("AFTER SPLITTING CATEGORIES")
        # print(len(self.dataset.category_name_list), len(self.dataset.category_index_dict), len(self.dataset.category_dict), self.dataset.num_categories)

        if self.use_categories:
            unique_categories = sorted(list(set([instance.category for instance in self.dataset.instance_list])))
        else:
            unique_categories = []
        if self.use_subcategories:
            unique_subcategories = sorted(list(set([instance.subcategory for instance in self.dataset.instance_list])))
        else:
            unique_subcategories = []

        # print("Unique cateoories and subcategories")
        # print(len(unique_categories), len(unique_subcategories))

        self.row_label_list = unique_categories + unique_subcategories
        self.row_index_dict = {item: index for index, item in enumerate(self.row_label_list)}
        self.num_rows = len(self.row_label_list)

    def init_columns(self):
        self.column_label_list = sorted(list(set([instance.image.name for instance in self.dataset.instance_list])))
        self.column_index_dict = {item: index for index, item in enumerate(self.column_label_list)}
        self.num_columns = len(self.column_label_list)

    def remove_zero_rows_and_columns(self):
        new_column_label_list = []
        new_column_index_dict = {}
        new_num_columns = 0

        new_row_label_list = []
        new_row_index_dict = {}
        new_num_rows = 0

        nonzero_rows = np.count_nonzero(np.sum(self.matrix, axis=1))
        nonzero_columns = np.count_nonzero(np.sum(self.matrix, axis=0))
        new_matrix1 = np.zeros([self.num_rows, nonzero_columns], int)

        for i in range(self.num_columns):
            if self.matrix[:, i].sum() > 0:
                new_column_label_list.append(self.column_label_list[i])
                new_column_index_dict[self.column_label_list[i]] = new_num_columns
                new_matrix1[:, new_num_columns] = self.matrix[:, i]
                new_num_columns += 1

        new_matrix2 = np.zeros([nonzero_rows, nonzero_columns], int)
        for i in range(self.num_rows):
            if new_matrix1[i, :].sum() > 0:
                new_row_label_list.append(self.row_label_list[i])
                new_row_index_dict[self.row_label_list[i]] = new_num_rows
                new_matrix2[new_num_rows, :] = new_matrix1[i, :]
                new_num_rows += 1

        self.matrix = new_matrix2

        self.row_label_list = new_row_label_list
        self.row_index_dict = new_row_index_dict
        self.num_rows = new_num_rows

        self.column_label_list = new_column_label_list
        self.column_index_dict = new_column_index_dict
        self.num_columns = new_num_columns

    def split_categories(self, num_groups):
        num_categories = 0
        category_name_list = []
        category_index_dict = {}
        category_dict = {}
        for category_name in self.dataset.category_name_list:

            category = self.dataset.category_dict[category_name]
            # Calculate the number of elements per group
            num_elements = len(category.instance_dict)
            elements_per_group = num_elements // num_groups

            # Shuffle the keys of the instance_dict
            keys = list(category.instance_dict.keys())
            random.shuffle(keys)
            # print(category_name)

            for i in range(num_groups):
                # Create a new Category instance with the same name
                new_category = copy.deepcopy(category)
                new_category.name = category.name + str(i+1)
                new_category.subcategory_dict = {}
                new_category.instance_dict = {}

                # Add a subset of the instance_dict to the new category
                start = i * elements_per_group
                end = start + elements_per_group
                for key in keys[start:end]:
                    new_category.instance_dict[key] = category.instance_dict[key]

                category_name_list.append(new_category.name)
                category_index_dict[new_category.name] = num_categories
                category_dict[new_category.name] = new_category
                num_categories += 1

                # TODO the problem is with this, the changing of the instances is still leaving some of the original unsplit categories
                for instance_id in new_category.instance_dict:
                    new_category.instance_dict[instance_id] = category.instance_dict[instance_id]
                    new_category.instance_dict[instance_id].category = new_category.name

                # print(len(category_name_list))
                # print(category_name_list)

        self.dataset.num_categories = num_categories
        self.dataset.category_dict = category_dict
        self.dataset.category_index_dict = category_index_dict
        self.dataset.category_name_list = category_name_list

    def create_matrix(self):

        self.init_rows()
        self.init_columns()
        print("Creating {} Category x {} Image Matrix".format(self.num_rows, self.num_columns))
        self.matrix = np.zeros([self.num_rows, self.num_columns], int)

        for instance in self.dataset.instance_list:
            column_index = self.column_index_dict[instance.image.name]

            if self.use_subcategories and self.use_categories:
                if instance.subcategory == "None":
                    row_label = instance.category
                else:
                    row_label = instance.subcategory
            elif self.use_subcategories and not self.use_categories:
                if instance.subcategory == "None":
                    row_label = None
                else:
                    row_label = instance.subcategory

            elif not self.use_subcategories and self.use_categories:
                row_label = instance.category

            else:
                raise Exception("ERROR: You must use either categories or subcategories as rows")

            if row_label is not None:
                row_index = self.row_index_dict[row_label]
                self.matrix[row_index, column_index] += 1

        # print("After removing zero rows")
        self.remove_zero_rows_and_columns()


# class InstanceByInstanceMatrix:
#
#     def __init__(self, dataset, cooc_type):
#         self.dataset = dataset
#
#         self.cooc_type = cooc_type
#         # binary in same image,
#         # adjacent in image
#         # distance within image
#
#         self.num_categories = copy.deepcopy(dataset.num_categories)
#         self.category_name_list = copy.deepcopy(dataset.category_name_list)
#         self.category_index_dict = copy.deepcopy(dataset.category_index_dict)
#         self.category_dict = copy.deepcopy(dataset.category_dict)
#
#         self.num_images = copy.deepcopy(dataset.num_images)
#         self.image_name_list = copy.deepcopy(dataset.image_name_list)
#         self.image_index_dict = copy.deepcopy(dataset.image_index_dict)
#         self.image_dict = copy.deepcopy(dataset.image_dict)
#
#         self.num_instances = copy.deepcopy(dataset.num_instances)
#         self.instance_id_list = copy.deepcopy(dataset.instance_id_list)
#         self.instance_index_dict = copy.deepcopy(dataset.instance_index_dict)
#         self.instance_dict = copy.deepcopy(dataset.instance_dict)
#
#         self.category_by_category_matrix = None
#
#         self.create_matrix()
#
#     def create_matrix(self):
#
#         self.category_by_category_matrix = np.zeros([self.num_categories, self.num_categories])

    '''
        get list of instances in image

        instance_scaled_cooc_matrix
        instance_binary_cooc_matrix

        load save version of image
        for i in range(image_height)
            for j in range(image_width)
                get pixel color1 from image
                look up instance ID and class ID

                for x in range(-1,2)
                    for y in range(-1,2):
                        if not (x==0 and y==0):
                            if 0 <= i+x < image_width:
                                if 0 <= j+y < image_height:
                                    get pixel color2 from image
                                    if color2 != color1:
                                        get instance ID and class ID of new pixel
                                        increment scaled_cooc_matrix
                                        if binary_cooc_matrix == 0
                                            increment binary_cooc_matrix


        convert instance cooc matrices into class cooc matrices

    '''
