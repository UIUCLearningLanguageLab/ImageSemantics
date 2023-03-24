import os
import json
import jsonpickle
import pickle
from datetime import datetime
import shutil


class Dataset:

    def __init__(self) -> None:

        self.sa_dataset_path = None
        self.path = None

        self.num_categories = None
        self.category_name_list = None
        self.category_index_dict = None
        self.category_dict = None

        self.num_images = None
        self.image_name_list = None
        self.image_index_dict = None
        self.image_dict = None

        self.num_instances = None
        self.instance_list = None

    def __repr__(self):
        output_string = "Num_Classes: {} Num_Images: {} Num Instances:{}\n".format(self.num_categories,
                                                                                   self.num_images,
                                                                                   self.num_instances)
        return output_string

    @staticmethod
    def create_dataset_model_output_dir(output_dir_path, overwrite):
        # create the directory if it doesn't exist, or if you want to overwrite the existing one
        if os.path.exists(output_dir_path):
            if overwrite:
                shutil.rmtree(output_dir_path)
            else:
                raise FileExistsError(f"The directory {output_dir_path} already exists.")
        os.mkdir(output_dir_path)

    def output_descriptive_info(self, output_path, overwrite=False):

        self.create_dataset_model_output_dir(output_path, overwrite)

        with open(output_path + "/categories.csv", "w") as file:
            file.write("index,category,freq\n")
            for category_name in self.category_name_list:
                category_instance = self.category_dict[category_name]
                category_index = self.category_index_dict[category_name]
                file.write("{},{},{}\n".format(category_index, category_name, len(category_instance.instance_dict)))

        with open(output_path + "/images.csv", "w") as file:
            file.write("index,image,num_instances\n")
            for image_name in self.image_name_list:
                image_instance = self.image_dict[image_name]
                image_index = self.image_index_dict[image_name]
                file.write("{},{},{}\n".format(image_index, image_name, image_instance.num_instances))

        with open(output_path + "/subcategories.csv", "w") as file:
            file.write("category,subcategory,freq\n")
            for category_name in self.category_name_list:
                category_instance = self.category_dict[category_name]
                for subcategory_name, subcategory_instance in category_instance.subcategory_dict.items():
                    num_instances = len(subcategory_instance.instance_dict)
                    file.write("{},{},{}\n".format(category_name, subcategory_name, num_instances))

    def init_dataset(self):
        self.num_images = 0
        self.image_name_list = []
        self.image_index_dict = {}
        self.image_dict = {}
        self.num_instances = 0
        self.instance_list = []
        self.num_categories = 0
        self.category_name_list = []
        self.category_index_dict = {}
        self.category_dict = {}

    def load_sa_dataset(self, sa_dataset_path):

        self.init_dataset()

        self.sa_dataset_path = sa_dataset_path

        directory_list = os.listdir(sa_dataset_path)
        for subdirectory in directory_list:
            if subdirectory[0] != ".":
                subdirectory_path = sa_dataset_path + "/" + subdirectory
                file_list = os.listdir(subdirectory_path)
                for file_name in file_list:
                    if file_name[-4:] == '.jpg':
                        image_name = file_name[:-4]
                        new_image = Image()
                        new_image.load_from_sa_dataset(image_name, subdirectory_path, self)
                        self.image_name_list.append(image_name)
                        self.image_dict[image_name] = new_image
                        self.num_images += 1
        self.image_name_list.sort()
        for i in range(self.num_images):
            self.image_index_dict[self.image_name_list[i]] = i

    def load_dataset(self, path, image_adjustment=None):
        with open(path, 'rb') as f:
            loaded_obj = pickle.load(f)
            self.__dict__.update(loaded_obj.__dict__)
        self.path = path

        if image_adjustment is not None:
            for image in self.image_dict.values():
                image.path = "../" + image.path

    def save_dataset(self, path=None, include_json=False):

        if path is None:
            path_list = self.path.split("_")
            path = path_list[0]

        now = datetime.now()
        date_string = now.strftime("%Y_%m_%d_%H%M%S")
        pkl_path = path + "_" + date_string + ".pkl"
        json_path = path + "_" + date_string + ".json"

        with open(pkl_path, 'wb') as f:
            pickle.dump(self, f)

        if include_json:
            with open(json_path, 'w') as f:
                f.write(jsonpickle.encode(self, indent=4))

    def add_subcategory(self, category, subcategory_name):
        self.category_dict[category].subcategory_dict[subcategory_name] = Category(subcategory_name, self.category_dict[category].color)


class Image:

    def __init__(self) -> None:
        self.name = None
        self.path = None
        self.height = None
        self.width = None
        self.jpg_file_name = None
        self.json_file_name = None
        self.category_mask_file_name = None
        self.unique_mask_file_name = None

        self.instance_list = None
        self.num_instances = None

    def __repr__(self):
        output_string = "Image: {}\n".format(self.name)
        output_string += "    Dimensions: ({},{})\n".format(self.width, self.height)
        output_string += "    Num Instances: {}\n".format(self.num_instances)

        return output_string

    def load_from_sa_dataset(self, name, sa_path, dataset):
        self.name = name
        self.path = sa_path

        self.jpg_file_name = name + ".jpg"
        self.json_file_name = name + ".jpg___pixel.json"
        self.category_mask_file_name = name + ".jpg___fuse.png"
        self.unique_mask_file_name = name + ".jpg___save.png"

        sa_json_path = self.path + "/" + self.json_file_name
        with open(sa_json_path, 'r') as f:
            sa_json_data = json.load(f)

        self.num_instances = 0
        self.instance_list = []

        self.height = sa_json_data['metadata']['height']
        self.width = sa_json_data['metadata']['width']

        for instance in sa_json_data['instances']:

            instance_index = dataset.num_instances
            category_name = instance["className"]
            unique_color = instance["parts"][0]["color"]
            new_instance = Instance(instance_index, category_name, unique_color, self)

            self.instance_list.append(new_instance)
            self.num_instances += 1

            dataset.instance_list.append(new_instance)
            dataset.num_instances += 1

            if category_name not in dataset.category_dict:
                new_category = Category(category_name, unique_color)
                dataset.category_name_list.append(category_name)
                dataset.category_index_dict[category_name] = dataset.num_categories
                dataset.category_dict[category_name] = new_category
                dataset.num_categories += 1
            dataset.category_dict[category_name].instance_dict[instance_index] = new_instance


class Instance:

    def __init__(self, instance_id, category, color, image):
        self.id_number = instance_id
        self.category = category
        self.subcategory = "None"
        self.color = color
        self.image = image

    def __repr__(self):
        output_string = "Instance {}\n".format(self.id_number)
        output_string += "    Category: {}\n".format(self.category)
        output_string += "    Subcategory: {}\n".format(self.subcategory)
        output_string += "    Color: {}\n".format(self.color)
        output_string += "    Image Name: {}\n".format(self.image.name)
        return output_string

    def __eq__(self, other):
        if isinstance(other, Instance):
            return self.__dict__ == other.__dict__
        return False

    def __lt__(self, other):
        return self.id_number < other.id_number

    def __gt__(self, other):
        return self.id_number < other.id_number


class Category:

    def __init__(self, name, color) -> None:
        self.name = name
        self.color = color
        self.subcategory_dict = {}
        self.instance_dict = {}

    def __eq__(self, other):
        if not isinstance(other, Category):
            return False
        differing_attributes = []
        for attr in vars(self):
            if getattr(self, attr) != getattr(other, attr):
                differing_attributes.append(attr)
        return differing_attributes

    def __repr__(self) -> str:
        return "Category:{}, Color:{}, Num Instances:{}".format(self.name, self.color, len(self.instance_dict))
