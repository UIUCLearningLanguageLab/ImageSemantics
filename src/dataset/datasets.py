import os
import json
import glob
import pandas as pd
import re
import datetime


class Dataset:

    def __init__(self, ) -> None:

        self.sa_dataset_path = None
        self.path = None
        self.split_by_categories = None
        self.custom_category_list = None

        self.instance_header_list = ['participant', 'video', 'frame', 'dt', 'instance_id', 'category', 'subcategory',
                                     'color', 'last_modified']

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

    def add_sa_dataset(self, path):
        self.path = path
        category_set = set()
        instance_list = []

        for participant in os.listdir(self.path + "/images"):
            if participant[0] != ".":

                for video_name in os.listdir(self.path + "/images/" + participant):
                    if video_name[0] != ".":

                        for file_name in os.listdir(self.path + "/images/" + participant + "/" + video_name):

                            if file_name[-4:] == '.jpg':

                                image_name = file_name[:-4]
                                image_info = image_name.split('_')
                                dt = "_".join(image_info[1:5])

                                frame = int(image_name.split('_')[-1])
                                sa_json_path = self.path + "/images/" + participant + "/" + video_name + "/" + file_name + ".json"

                                with open(sa_json_path, 'r') as f:
                                    sa_json_data = json.load(f)

                                    for instance in sa_json_data['instances']:
                                        color = instance["parts"][0]["color"]
                                        category = self.sanitize_category_names(instance["className"])
                                        category_set.add(category)
                                        instance_data = [participant,
                                                         int(video_name),
                                                         frame,
                                                         dt,
                                                         self.num_instances,
                                                         category,
                                                         "None",
                                                         color,
                                                         datetime.datetime.now().replace(microsecond=0)]
                                        instance_list.append(instance_data)
                                        self.num_instances += 1

        self.instance_df = pd.DataFrame(data=instance_list, columns=self.instance_header_list)
        self.instance_df = self.instance_df.sort_values(by=['participant', 'video', 'frame', 'instance_id'])

        self.generate_image_df()
        self.generate_category_df()
        self.generate_subcategory_df()

        print(category_set)

    def generate_image_df(self):
        self.image_df = self.instance_df.groupby(['participant', 'video', 'frame']).size().reset_index(name='count')
        self.num_images = self.image_df.shape[0]

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

        self.num_subcategories = self.subcategory_df.shape[0]

    def load_dataset(self, path):

        self.path = path
        # Path to the directory with the CSV files
        all_files = glob.glob(path + "/csv/*.csv")

        # List to hold individual DataFrames
        df_list = []

        # Define the data types for specific columns
        dtypes = {
            'participant': str,
            'video': int,
            'frame': int,
            'dt': str,
            'instance_id': int,
            'category': str,
            'subcategory': str,
            'color': str
        }

        # Loop through all the CSV files and read them into DataFrames
        for filename in all_files:
            df = pd.read_csv(filename, dtype=dtypes, parse_dates=['last_modified'])
            df_list.append(df)

        # Concatenate all the individual DataFrames into a single DataFrame
        self.instance_df = pd.concat(df_list, axis=0, ignore_index=True)

        self.num_instances = self.instance_df.shape[0]

        self.generate_image_df()
        self.generate_category_df()
        self.generate_subcategory_df()

        print(self.instance_df)
        print(self.image_df)
        print(self.category_df)
        print(self.subcategory_df)

    def save_dataset(self, split_by_category=False, specified_category_list=None):
        print(self.instance_df)
        print(self.image_df)
        print(self.category_df)
        print(self.subcategory_df)

        if specified_category_list:
            self.custom_category_list = specified_category_list
            instance_df = self.instance_df[self.instance_df['category'].isin(specified_category_list)]
        else:
            instance_df = self.instance_df

        if split_by_category:
            self.split_by_categories = True
            for category in instance_df['category'].unique():
                # Filter the DataFrame for the current category
                filtered_df = instance_df[instance_df['category'] == category]

                # Save the filtered DataFrame to a CSV file
                filtered_df.to_csv(self.path + "/csv/" + category + ".csv", index=False)
        else:
            self.split_by_categories = False
            instance_df.to_csv(self.path + "/csv/" + 'all.csv', index=False)

    @staticmethod
    def sanitize_category_names(category_name):
        """Sanitize the filename by replacing invalid characters with underscores."""
        s = re.sub(r'[()<>:"/\\|?* ]', '_', category_name)
        s = re.sub(r'_{2,}', '_', s)
        s = s.strip("_")
        return s

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
