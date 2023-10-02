import os
import json
import pickle
import pandas as pd
import re
import traceback


class Dataset:

    def __init__(self, ) -> None:

        self.sa_dataset_path = None
        self.path = None
        self.dataset_name = None

        self.instance_header_list = ['id', 'category', 'subcategory', 'color', 'image_id', 'version']
        self.image_header_list = ['id', 'video_name', 'participant', 'dt', 'frame', 'height', 'width', 'num_instances']

        self.category_df = None
        self.subcategory_df = None
        self.image_df = None
        self.instance_df = None

        self.num_categories = None
        self.num_subcategories = None
        self.num_images = None
        self.num_instances = None

        self.init_dataset()

    def __repr__(self):
        output_string = "Num_Categories: {}/{} Num_Images: {} Num Instances:{}\n".format(self.num_categories,
                                                                                         self.num_subcategories,
                                                                                         self.num_images,
                                                                                         self.num_instances)
        return output_string

    def init_dataset(self):
        self.num_categories = 0
        self.num_subcategories = 0
        self.num_images = 0
        self.num_instances = 0

    def add_sa_dataset(self, dataset_name, sa_dataset_path):
        self.dataset_name = dataset_name
        self.sa_dataset_path = sa_dataset_path

        image_list = []
        instance_list = []

        for subdirectory in os.listdir(sa_dataset_path):
            if subdirectory[0] != ".":

                info = subdirectory.split("_")
                video_name = info[0]
                participant = info[1]
                dt = info[2] + "_" + info[3] + "_" + info[4] + "_" + info[5]
                subdirectory_path = sa_dataset_path + "/" + subdirectory

                file_list = os.listdir(subdirectory_path)

                for file_name in file_list:
                    if file_name[-4:] == '.jpg':

                        image_name = file_name[:-4]
                        frame = image_name.split('_')[-1]
                        sa_json_path = subdirectory_path + "/" + image_name + ".jpg.json"

                        with open(sa_json_path, 'r') as f:
                            sa_json_data = json.load(f)
                            height = sa_json_data['metadata']['height']
                            width = sa_json_data['metadata']['width']

                            num_instances_in_image = 0
                            for instance in sa_json_data['instances']:
                                instance_data = [self.num_instances,
                                                 instance["className"],
                                                 "None",
                                                 instance["parts"][0]["color"],
                                                 self.num_images,
                                                 0]
                                instance_list.append(instance_data)
                                self.num_instances += 1
                                num_instances_in_image += 1

                            image_data = [self.num_images, video_name, participant, dt, frame, height, width, num_instances_in_image]
                            image_list.append(image_data)

                        self.num_images += 1

        self.instance_df = pd.DataFrame(data=instance_list, columns=self.instance_header_list)
        self.image_df = pd.DataFrame(data=image_list, columns=self.image_header_list)

        self.generate_category_df()

    def generate_category_df(self):
        self.category_df = self.instance_df.groupby('category').agg(
            category=('category', 'first'),
            color=('color', 'first'),
            count=('category', 'size')
        ).reset_index(drop=True)
        self.category_df = self.category_df[['category', 'color', 'count']]
        self.num_categories = self.category_df.shape[0]

    def generate_subcategory_df(self):
        if self.subcategory_df is not None:
            empty_subcategory_df = self.subcategory_df[self.subcategory_df['count'] == 0]
        else:
            empty_subcategory_df = None

        # regenerate subcategory_df from instance_df
        self.subcategory_df = self.instance_df.groupby(['subcategory', 'category']).size().reset_index(name='count')

        # Add back rows from empty_subcategory_df
        if empty_subcategory_df is not None:
            self.subcategory_df = pd.concat([self.subcategory_df, empty_subcategory_df], ignore_index=True)

        # get a list of all the categories in category_df that are in subcategory_df but without the subcategory None
        missing_categories = self.category_df[~self.category_df['category'].isin(
            self.subcategory_df[self.subcategory_df['subcategory'] == 'None']['category'])]
        none_subcategory_df = pd.DataFrame({
            'subcategory': ['None'] * len(missing_categories),
            'category': missing_categories['category'],
            'count': [0] * len(missing_categories)  # Setting count to 0 for these rows
        })

        # Concatenate with subcategory_df and remove duplicates
        self.subcategory_df = pd.concat([self.subcategory_df, none_subcategory_df]).drop_duplicates(
            subset=['subcategory', 'category']).reset_index(drop=True)
        self.subcategory_df['count'] = self.subcategory_df['count'].astype(int)

    def load_dataset(self, path, dataset_name):
        with open(path+dataset_name, 'rb') as f:
            loaded_obj = pickle.load(f)
            self.__dict__.update(loaded_obj.__dict__)
        self.path = path
        self.dataset_name = dataset_name[:-4]
        self.generate_category_df()
        self.generate_subcategory_df()

    def save_dataset(self, path=None, split_by_category=False):
        if path is None:
            path = self.path

        if split_by_category:
            full_instance_df = self.instance_df.copy()
            unique_categories = self.instance_df['category'].unique().tolist()
            dataset_name = self.dataset_name
            for category in unique_categories:
                self.instance_df = full_instance_df[full_instance_df['category'] == category]
                self.generate_category_df()
                self.generate_subcategory_df()

                cleaned_category_name = re.sub(r'[\\/*?:"<> |]', '-', category)
                self.dataset_name = dataset_name + "_" + cleaned_category_name
                with open(path + self.dataset_name + ".pkl", 'wb') as f:
                    pickle.dump(self, f)
            self.instance_df = full_instance_df
            self.generate_category_df()
            self.generate_subcategory_df()
            self.dataset_name = dataset_name

        else:
            print(self.path, self.dataset_name)
            with open(self.path + self.dataset_name + ".pkl", 'wb') as f:
                pickle.dump(self, f)

    def add_subcategory(self, category, subcategory_name):
        entry_exists = any((self.subcategory_df['category'] == category) & (self.subcategory_df['subcategory'] == subcategory_name))
        # If the entry doesn't exist, add it
        if not entry_exists:
            self.subcategory_df.loc[self.subcategory_df.shape[0]] = [subcategory_name, category, 0]

    def remove_subcategory(self, category, subcategory):
        filtered_rows = self.subcategory_df[(self.subcategory_df['subcategory'] == subcategory) & (self.subcategory_df['category'] == category)]
        if not filtered_rows.empty:
            self.subcategory_df.drop(filtered_rows.index, inplace=True)

    def get_category_list(self):
        category_list = self.category_df['category'].unique().tolist()
        return category_list

    def get_subcategory_list(self, category):
        subcategory_list = self.subcategory_df[self.subcategory_df['category'] == category]['subcategory'].unique().tolist()
        return subcategory_list
