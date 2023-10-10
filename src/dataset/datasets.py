import os
import json
import glob
import pandas as pd
import re
import datetime
import csv


class Dataset:

    def __init__(self, ) -> None:

        self.sa_dataset_path = None
        self.path = None
        self.split_by_categories = None
        self.custom_category_list = None

        self.instance_header_list = ['participant', 'video', 'frame', 'dt', 'instance_id', 'category', 'subcategory',
                                     'color_list', 'last_modified']

        self.category_df = None
        self.subcategory_df = None
        self.image_df = None
        self.instance_df = None

        self.num_categories = None
        self.num_subcategories = None
        self.num_images = None
        self.num_instances = None

        self.instance_comment_dict = None

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
        self.instance_comment_dict = {}

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
                                        color_list = []
                                        for part in instance["parts"]:
                                            color_list.append(part["color"])

                                        category = self.sanitize_category_names(instance["className"])
                                        category_set.add(category)
                                        instance_data = [participant,
                                                         int(video_name),
                                                         frame,
                                                         dt,
                                                         self.num_instances,
                                                         category,
                                                         "None",
                                                         color_list,
                                                         datetime.datetime.now().replace(microsecond=0)]
                                        instance_list.append(instance_data)
                                        self.num_instances += 1

        self.instance_df = pd.DataFrame(data=instance_list, columns=self.instance_header_list)
        self.instance_df = self.instance_df.sort_values(by=['participant', 'video', 'frame', 'instance_id'])

        self.generate_image_df()
        self.generate_category_df()
        self.generate_subcategory_df()

        self.instance_comment_dict = {}
        category_list = self.get_category_list()
        for category in category_list:
            self.instance_comment_dict[category] = []

    def generate_image_df(self):
        self.image_df = self.instance_df.groupby(['participant', 'video', 'frame']).size().reset_index(name='count')
        self.num_images = self.image_df.shape[0]

    def generate_category_df(self):
        self.category_df = self.instance_df.groupby('category').agg(
            category=('category', 'first'),
            count=('category', 'size')
        ).reset_index(drop=True)
        self.category_df = self.category_df[['category', 'count']]
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

        path += "/instance_data"

        json_files = glob.glob(f"{path}/*.json")

        # Read each JSON file into a DataFrame and store in a list
        dfs = [pd.read_json(file, lines=True, dtype={'dt': str}) for file in json_files]

        # Concatenate all DataFrames in the list into a single DataFrame
        self.instance_df = pd.concat(dfs, ignore_index=True)

        # Convert columns to desired data types
        dtypes = {
            'participant': str,
            'video': int,
            'frame': int,
            'dt': str,
            'instance_id': int,
            'category': str,
            'subcategory': str,
            'color_list': 'object',  # Lists are stored as objects in pandas
            'last_modified': str  # Convert Unix timestamp in milliseconds to datetime
        }

        for column, dtype in dtypes.items():
            self.instance_df[column] = self.instance_df[column].astype(dtype)

        self.num_instances = self.instance_df.shape[0]

        csv_files = glob.glob(f"{path}/*.csv")

        # Dictionary to store the filename and the corresponding data
        for file in csv_files:
            with open(file, 'r') as f:
                reader = csv.reader(f)
                data = list(reader)

                # Store the filename (without the path and extension) as the key and the data as the value
                filename = os.path.splitext(os.path.basename(file))[0]
                category = filename[:-9]
                self.instance_comment_dict[category] = data

        # Now, csv_data contains the filename as the key and the data from the CSV file as a list of lists

        self.generate_image_df()
        self.generate_category_df()
        self.generate_subcategory_df()

    def save_dataset(self, split_by_category=False):

        # self.instance_df['last_modified'] = self.instance_df['last_modified'].dt.strftime('%Y-%m-%d %H:%M:%S')

        if split_by_category:
            for category in self.instance_df['category'].unique():
                # Filter the DataFrame for the current category
                filtered_df = self.instance_df[self.instance_df['category'] == category].copy()

                path = self.path + "/instance_data/" + category + ".json"
                filtered_df.to_json(path, orient='records', lines=True)

                if category in self.instance_comment_dict:
                    category_comment_list = self.instance_comment_dict[category]
                    comment_path = self.path + "/instance_data/" + category + "_comments.csv"

                    with open(comment_path, "w", newline='') as csv_file:
                        writer = csv.writer(csv_file)
                        for row in category_comment_list:
                            # Remove commas from each string in the row
                            cleaned_row = [str(field).replace(",", "") for field in row]
                            writer.writerow(cleaned_row)

        else:
            path = self.path + "/instance_data/" + 'all.json'
            self.instance_df.to_json(path, orient='records', lines=True)

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

    def get_category_list(self, sort_list=True):

        category_list = self.category_df['category'].unique().tolist()

        if sort_list:
            category_list.sort()
        return category_list

    def get_subcategory_list(self, category, sort_list=True, none_start=True):
        subcategory_list = self.subcategory_df[self.subcategory_df['category'] == category]['subcategory'].unique().tolist()

        if sort_list:
            subcategory_list.sort()

        if none_start:
            if "None" in subcategory_list:
                subcategory_list.remove("None")
                subcategory_list.insert(0, "None")

        return subcategory_list

    def get_video_list(self, sort_list=True, add_all=True):
        unique_df = self.image_df.drop_duplicates(subset=['participant', 'video'])
        video_tuple_list = list(zip(unique_df['participant'], unique_df['video']))

        if sort_list:
            video_tuple_list.sort()

        string_list = [f"{tup[0]}-{tup[1]}" for tup in video_tuple_list]

        if add_all:
            string_list = ["ALL"] + string_list

        return string_list

    def get_image_path(self, instance_data_list):
        participant = instance_data_list[0]
        video = str(instance_data_list[1])
        frame = str(instance_data_list[2]).zfill(6)
        dt = instance_data_list[3]

        path = self.path + "/images/" + participant + "/" + video + "/"
        filename = path + participant + "_" + dt + "_" + frame

        return filename

    def print_subcategory_string(self):
        result = self.subcategory_df.apply(lambda row: f"{row['category']} {row['subcategory']} {row['count']}", axis=1).tolist()
        print()
        for thing in result:
            print(thing)
        print()
