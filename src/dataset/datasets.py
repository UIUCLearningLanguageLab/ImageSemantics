import os
import json
import random
import glob
import pandas as pd
import re
import datetime
import csv
import time
from PIL import Image
import numpy as np
import copy
import heapq


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
        self.filtered_instance_df = None

        self.num_categories = None
        self.num_subcategories = None
        self.num_images = None
        self.num_instances = None

        self.instance_comment_dict = None

        self.init_dataset()

    def __repr__(self):
        output_string = "Num_Categories: {}/{} Num_Images: {} Num Instances:{}".format(self.num_categories,
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
        self.filtered_instance_df = pd.DataFrame(data=[], columns=self.instance_header_list)

    @staticmethod
    def load_image_matrix(path):
        image_pil_file = Image.open(path).convert("RGB")
        image_matrix = np.asarray(copy.deepcopy(image_pil_file))
        return image_matrix

    def get_unique_colors_set(self, image_matrix,
                              critical_region_min_x,
                              critical_region_max_x,
                              critical_region_min_y,
                              critical_region_max_y):

        critical_region = image_matrix[
                          critical_region_min_y:critical_region_max_y, critical_region_min_x:critical_region_max_x]

        # Reshape the critical region to a 2D array where each row represents a pixel
        reshaped_region = critical_region.reshape(-1, critical_region.shape[2])

        # Convert RGB values to hexadecimal format using vectorized operations
        hex_colors = np.apply_along_axis(lambda x: '#{:02x}{:02x}{:02x}'.format(*x), 1, reshaped_region)

        # Convert to a set to get unique colors
        unique_colors_set = set(hex_colors)

        return unique_colors_set

    def get_filtered_instance_df(self, image_instance_df, unique_colors_set):

        # Assuming df is your DataFrame and unique_colors_set is your set of unique hex color values
        # Define a function that checks if any color in the color_list is in unique_colors_set
        def color_in_set(color_list):
            return any(color in unique_colors_set for color in color_list)

        # Apply this function to the 'color_list' column to create a boolean mask
        mask = image_instance_df['color_list'].apply(color_in_set)

        # Use the mask to filter the DataFrame
        filtered_image_instance_df = image_instance_df[mask]
        return filtered_image_instance_df

    def get_image_instance_df(self, image_row):
        participant, video, frame, dt, _, _ = image_row
        matched_rows = self.instance_df[
            (self.instance_df['participant'] == participant) &
            (self.instance_df['video'] == video) &
            (self.instance_df['frame'] == frame) &
            (self.instance_df['dt'] == dt)
            ]
        return matched_rows

    def filter_dataset_by_bounding_box(self):
        num_images = len(self.image_df)
        my_counter = 0
        filtered_df_list = []

        for row in self.image_df.itertuples(index=False):
            start_time = time.time()
            if my_counter >= num_images:
                break

            # load an image as a matrix
            path = row.image_path
            image_path = path + "___save.png"
            image_matrix = self.load_image_matrix(image_path)

            # set a critical region
            image_size = image_matrix.shape
            image_width = image_size[1]
            image_height = image_size[0]
            critical_region_min_x = int(round(image_width * .25))
            critical_region_max_x = int(round(image_width * .75))
            critical_region_min_y = int(round(image_height * .25))
            critical_region_max_y = int(round(image_height * .75))

            # get the unique colors in that image
            unique_colors_set = self.get_unique_colors_set(image_matrix,
                                                           critical_region_min_x,
                                                           critical_region_max_x,
                                                           critical_region_min_y,
                                                           critical_region_max_y)

            image_instance_df = self.get_image_instance_df(row)
            filtered_image_instance_df = self.get_filtered_instance_df(image_instance_df, unique_colors_set)
            filtered_df_list.append(filtered_image_instance_df)

            my_counter += 1
            took = time.time() - start_time
            if my_counter % 1 == 0:
                print(f"Finished {my_counter}/{len(self.image_df)} images ({took:0.2f})")

        self.instance_df = pd.concat(filtered_df_list, ignore_index=True)

        self.generate_image_df()
        self.generate_category_df()
        self.generate_subcategory_df()

    def filter_by_size(self, n):
        def rgb_to_hex(rgb):
            return '#' + ''.join(['{:02x}'.format(x) for x in rgb])

        for my_image in self.image_df.itertuples(index=True):
            path = my_image.image_path
            savedPath = path + "___save.png"
            image_pil_file = Image.open(savedPath).convert("RGB")
            image_matrix = np.asarray(copy.deepcopy(image_pil_file))

            # Reshape the matrix to a 2D array where each row is an RGB value
            pixels = image_matrix.reshape(-1, 3)

            # Convert each pixel to its hex representation
            hex_colors = [rgb_to_hex(pixel) for pixel in pixels]

            # Count the occurrences of each hex color
            color_counts = {}
            for color in hex_colors:
                if color in color_counts:
                    color_counts[color] += 1
                else:
                    color_counts[color] = 1

            biggest_instance_color = max(color_counts, key=color_counts.get)
            image_size = image_matrix.shape[0]*image_matrix.shape[1]
            biggest_percentage = color_counts[biggest_instance_color]/image_size
            print(path, biggest_instance_color, f"{biggest_percentage:0.3f}")
            image_instance_df = self.get_image_instance_df(my_image)
            largest_keys = heapq.nlargest(n, color_counts, key=color_counts.get)

    def filter_dataset_by_subject_touching(self):
        # for each unique image in self.image_df
        #   if that image contains "self" as an instance
        #       touching_self_instance_list = []
        #       get the hex color of "self" from self.instance_df for that image
        #       load the image as a matrix the way you did above
        #       make self_pixels, a list tuples of all the pixels that contain the self rgb color, e.g. [(12, 2), (12, 3), (12, 4), (13, 2), (13, 3)]
        #       for pixel in self_pixels:
        #           adjacent_pixel_list = [(pixel[0], pixel[1]-1), (pixel[0], pixel[1]+1), (pixel[0]-1, pixel[1]), (pixel[0]+1, pixel[1])]
        #           remove all values from adjacent_pixel_list that contain a negative value or a value greater than image_height-1 or image_width-1
        #           (adjacent pixels that arent really in the image)
        #           for adjacent_pixel in adjacent_pixel_list:
        #               get hex color of adjacent pixel
        #               if hex color is not color of self, add it to touching_self_instance_list
        #   remove rows from self.instance_df that match that image and do NOT have a value in their color_list that are in touching_self_instance_list
        pass

    def filter_dataset(self, bounding_box=False, infant_touching=False, big_object=False, num_images=0):
        if bounding_box is True:
            self.filter_dataset_by_bounding_box()
        if infant_touching is True:
            self.filter_dataset_by_subject_touching()
        if big_object is True:
            self.filter_by_size()

    def add_sa_dataset(self, path):
        self.path = path
        category_set = set()
        instance_list = []

        for participant in os.listdir(self.path + "/images/"):
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
        self.image_df = self.instance_df.groupby(['participant', 'video', 'frame', 'dt']).size().reset_index(name='num_instances')
        self.image_df['image_path'] = self.image_df.apply(
    lambda
        row: f"{self.path}/images/{row['participant']}/{row['video']}/{row['participant']}_{row['dt']}_{str(row['frame']).zfill(6)}.jpg",
    axis=1)
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
        json_files = glob.glob(f"{path}/instance_data/*.json")

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
        print(f"Loaded dataset with {self}")

    def save_dataset(self, split_by_category=False, file_name=None):

        # self.instance_df['last_modified'] = self.instance_df['last_modified'].dt.strftime('%Y-%m-%d %H:%M:%S')
        if split_by_category:
            for category in self.instance_df['category'].unique():
                # Filter the DataFrame for the current category
                filtered_df = self.instance_df[self.instance_df['category'] == category].copy()

                if file_name is None:
                    path = f"{self.path}/instance_data/{category}.json"
                else:
                    path = f"{self.path}/instance_data/{file_name}_{category}.json"
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
            if file_name is None:
                path = self.path + "/instance_data/" + 'all.json'
            else:
                path = f"{self.path}/instance_data/{file_name}_all.json"
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
        result = (
            self.subcategory_df.sort_values(by=['category', 'subcategory'])
            .apply(lambda row: f"{row['category']},{row['subcategory']},{row['count']}", axis=1)
            .tolist()
        )
        print()
        for thing in result:
            print(thing)
        print()

        f = open(self.path + "/subcategories.csv", "w")
        for thing in result:
            f.write(f"{thing}\n")
        f.close()

    def split_categories(self, num_split_categories):
        self.instance_df['subcategory'] = self.instance_df[
            'category'].apply(lambda x: f"{x}{random.randint(1, num_split_categories)}")
        self.generate_image_df()
        self.generate_category_df()
        self.generate_subcategory_df()

    def remove_subcategory_none_rows(self):
        self.subcategory_df = self.subcategory_df[self.subcategory_df['subcategory'] != 'None']
