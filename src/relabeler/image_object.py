from PIL import Image, ImageTk
import numpy as np
import copy


class ImageObject:

    def __init__(self, dataset_path, instance_data_list):

        self.dataset_path = dataset_path
        self.instance_data_list = instance_data_list

        self.participant = None
        self.video = None
        self.frame = None
        self.dt = None
        self.instance_id = None
        self.category = None
        self.subcategory = None
        self.hex_color_list = None
        self.last_modified = None

        self.path = None

        self.raw_pil_image = None
        self.instances_pil_image = None
        self.raw_image_matrix = None
        self.instance_pil_image = None

        self.init_image()

    def init_image(self):
        self.participant = self.instance_data_list[0]
        self.video = self.instance_data_list[1]
        self.frame = self.instance_data_list[2]
        self.dt = self.instance_data_list[3]
        self.instance_id = self.instance_data_list[4]
        self.category = self.instance_data_list[5]
        self.subcategory = self.instance_data_list[6]
        self.hex_color_list = self.instance_data_list[7]
        self.last_modified = self.instance_data_list[8]

        self.path = self.get_image_path()
        self.raw_pil_image = self.create_pil_image(self.path + ".jpg")
        self.instances_pil_image = self.create_pil_image(self.path + ".jpg___save.png")

    def get_image_path(self):
        path = self.dataset_path + "/images/" + self.participant + "/" + str(self.video) + "/" + self.participant + "_" + self.dt + "_" + str(self.frame).zfill(6)
        return path

    @staticmethod
    def create_pil_image(path):
        pil_image = Image.open(path).convert('RGB')
        return pil_image

    @staticmethod
    def create_tk_image(input_image):
        tk_image = ImageTk.PhotoImage(input_image)
        return tk_image

    @staticmethod
    def resize_image(input_pil_image, dimensions):
        resized_image = input_pil_image.resize((dimensions[0], dimensions[1]), Image.Resampling.LANCZOS)
        return resized_image

    @staticmethod
    def get_image_matrix(pil_image):
        image_matrix = np.asarray(copy.deepcopy(pil_image))
        return image_matrix

    def get_recolored_image(self):

        raw_image_matrix = copy.deepcopy(self.get_image_matrix(self.raw_pil_image))
        instances_image_matrix = copy.deepcopy(self.get_image_matrix(self.instances_pil_image))

        target_color_array_list = []

        for current_instance_hex_rgb in self.hex_color_list:
            r, g, b = [int(current_instance_hex_rgb[i:i + 2], 16) for i in (1, 3, 5)]
            target_color = np.array([r, g, b])
            target_color_array_list.append(target_color)

        combined_mask = np.zeros_like(instances_image_matrix[..., 0], dtype=bool)

        for target_color in target_color_array_list:
            mask = np.all(instances_image_matrix == target_color, axis=2)
            combined_mask = np.logical_or(combined_mask, mask)

        raw_image_matrix[combined_mask] = np.array([255, 0, 0])
        target_image = Image.fromarray(np.uint8(raw_image_matrix))

        return target_image

    @staticmethod
    def show_image(tk_image, location):
        location.configure(image=tk_image)
        location.image = tk_image
