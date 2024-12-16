import tkinter as tk
from tkinter import messagebox
from ImageSemantics.src.relabeler import image_object
from ImageSemantics.src.relabeler.by_category_view import instance_window


class ImagePreviewFrame:

    def __init__(self, app, category_frame):
        self.app = app
        self.category_frame = category_frame
        self.dimensions = None
        self.image_preview_dimensions = None

        self.image_preview_frame = None
        self.max_image_labels = None
        self.header_label = None

        self.preview_label_list = None
        self.preview_position_list = None
        self.preview_frame_list = None
        self.preview_image_list = None
        self.current_selections_list = None

        self.preview_category = None
        self.preview_subcategory = None
        self.preview_index = None
        self.old_preview_index = None

        self.create_image_preview_frame()
        self.create_header_label()
        self.create_preview_image_labels()

    def create_image_preview_frame(self):
        self.dimensions = (config.Config.main_window_dimensions[0] - self.app.full_image_frame.dimensions[0],
                           self.app.main_window_dimensions[1] - self.category_frame.interface_height)

        self.image_preview_frame = tk.Frame(self.app.image_frame,
                                            width=width,
                                            height=height,
                                            bg="black")
        self.image_preview_frame.pack(side=tk.LEFT)

        self.max_image_labels = config.Config.num_image_previews[0] * config.Config.num_image_previews[1]


    def get_header_string(self):
        num_instances = self.get_preview_instance_count()
        header_string = f"{self.preview_category}-{self.preview_subcategory}-{self.app.current_video}: {num_instances}"
        return header_string

    def create_header_label(self):
        header_string = self.get_header_string()
        self.header_label = tk.Label(self.image_preview_frame, text=header_string, bg="black", fg="white",
                                     font=("TkDefaultFont", 16))
        self.header_label.place(x=10, y=5)

    def create_preview_image_labels(self):

        image_start_x = 15
        image_start_y = 30
        image_spacing = 9
        frame_border_size = 3

        original_size = config.Config.full_image_dimensions
        s = config.Config.image_preview_size

        self.image_preview_dimensions = (int(original_size[0]*s), int(original_size[1]*s))

        self.preview_label_list = []
        self.preview_position_list = []
        self.preview_frame_list = []

        x = image_start_x
        label_counter = 0

        for i in range(config.Config.num_image_previews[1]):
            y = image_start_y
            for j in range(config.Config.num_image_previews[0]):
                position = (x, y)
                new_frame = tk.Frame(self.image_preview_frame,
                                     height=self.image_preview_dimensions[1]+frame_border_size,
                                     width=self.image_preview_dimensions[0]+frame_border_size,
                                     bg="gray22")
                new_frame.pack_propagate(False)
                new_frame.place(x=position[0], y=position[1])
                new_label = tk.Label(new_frame, bg="gray22")
                new_label.pack(fill=tk.BOTH, expand=1)
                new_label.bind('<Enter>', lambda event, arg=label_counter: self.enter_image(event, arg))
                new_label.bind('<Leave>', lambda event, arg=label_counter: self.leave_image(event, arg))
                new_label.bind('<Button-1>', lambda event, arg=label_counter: self.select_image(event, arg))
                new_label.bind('<Button-2>', lambda event, arg=label_counter: self.open_instance_comment_window(event,
                                                                                                                arg))

                self.preview_position_list.append(position)
                self.preview_label_list.append(new_label)
                self.preview_frame_list.append(new_frame)
                y += self.image_preview_dimensions[1] + image_spacing
                label_counter += 1
            x += self.image_preview_dimensions[0] + image_spacing
        return x

    def get_preview_instance_count(self):
        if self.app.current_video == "ALL":
            filtered_df = self.app.dataset.instance_df[
                (self.app.dataset.instance_df['category'] == self.preview_category) & (
                        self.app.dataset.instance_df['subcategory'] == self.preview_subcategory)]
        else:
            video_info = self.app.current_video.split("-")
            participant = video_info[0]
            video = video_info[1]
            filtered_df = self.app.dataset.instance_df[
                (self.app.dataset.instance_df['category'] == self.preview_category) & (
                        self.app.dataset.instance_df['subcategory'] == self.preview_subcategory) & (
                        self.app.dataset.instance_df['participant'] == participant) & (
                        self.app.dataset.instance_df['video'] == int(video))]

        return len(filtered_df)

    def get_preview_instance_list(self):
        if self.app.current_video == "ALL":
            filtered_df = self.app.dataset.instance_df[
                (self.app.dataset.instance_df['category'] == self.preview_category) & (
                        self.app.dataset.instance_df['subcategory'] == self.preview_subcategory)]
        else:
            video_info = self.app.current_video.split("-")
            participant = video_info[0]
            video = video_info[1]
            filtered_df = self.app.dataset.instance_df[
                (self.app.dataset.instance_df['category'] == self.preview_category) & (
                    self.app.dataset.instance_df['subcategory'] == self.preview_subcategory) & (
                    self.app.dataset.instance_df['participant'] == participant) & (
                    self.app.dataset.instance_df['video'] == int(video))]

        instance_list = filtered_df.values.tolist()

        return instance_list

    def update_preview_frame(self, increment_index=True):
        self.show_previews(increment_index)
        self.update_header()

    def update_header(self):
        header_string = self.get_header_string()
        print(f"Update header: {header_string}")
        self.header_label.config(text=header_string)

    def show_previews(self, increment_index):

        self.preview_image_list = []
        self.current_selections_list = []

        if self.app.current_category != self.preview_category:
            self.preview_index = 0

        if self.app.current_subcategory != self.preview_subcategory:
            self.preview_index = 0

        if not increment_index:
            self.preview_index = self.old_preview_index

        self.preview_category = self.app.current_category
        self.preview_subcategory = self.app.current_subcategory

        instance_list = self.get_preview_instance_list()
        num_instances = len(instance_list)

        if num_instances >= self.max_image_labels:
            num_images_to_show = self.max_image_labels
        else:
            num_images_to_show = len(instance_list)

        for i in range(self.max_image_labels):
            self.preview_frame_list[i].configure(bg="gray21")
            self.preview_label_list[i].configure(bg="gray21")
            self.preview_label_list[i].configure(image="")
            self.preview_label_list[i].image = ""

        self.old_preview_index = self.preview_index
        if num_images_to_show:
            for i in range(num_images_to_show):
                self.current_selections_list.append(False)

                instance_data_list = instance_list[self.preview_index]
                new_image = image_object.ImageObject(self.app.dataset.path, instance_data_list)
                preview_pil_image = new_image.resize_image(new_image.raw_pil_image, self.image_preview_dimensions)
                preview_tk_image = new_image.create_tk_image(preview_pil_image)

                self.preview_image_list.append(new_image)
                self.preview_label_list[i].configure(image=preview_tk_image)
                self.preview_label_list[i].image = preview_tk_image

                self.preview_index += 1
                if self.preview_index == len(instance_list):
                    self.preview_index = 0

        else:
            tk.messagebox.showinfo(message="There are no images in {}:{} to show.".format(self.preview_category,
                                                                                          self.preview_subcategory))

    def enter_image(self, event, label_counter):
        if self.preview_image_list is not None:
            if label_counter < len(self.preview_image_list):
                current_instance_image = self.preview_image_list[label_counter]
                self.app.full_image_frame.show_images(current_instance_image)
                self.app.root.update()

    def leave_image(self, event, arg):
        self.app.full_image_frame.hide_images()

    def select_image(self, event, label_counter):
        if self.current_selections_list is not None:
            if label_counter < len(self.current_selections_list):
                if self.current_selections_list[label_counter]:
                    self.preview_frame_list[label_counter].configure(bg="gray21")
                    self.preview_label_list[label_counter].configure(bg="gray21")
                    self.current_selections_list[label_counter] = False
                else:
                    self.preview_frame_list[label_counter].configure(bg="yellow")
                    self.preview_label_list[label_counter].configure(bg="yellow")
                    self.current_selections_list[label_counter] = True

    def open_instance_comment_window(self, event, label_counter):
        if label_counter < len(self.app.image_preview_frame.preview_image_list):
            image = self.app.image_preview_frame.preview_image_list[label_counter]
            new_instance_window = instance_window.InstanceWindow(self.app, image)
