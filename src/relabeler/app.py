import tkinter as tk
import math
import copy
import numpy as np
from tkinter import messagebox
from PIL import Image, ImageTk
from ImageSemantics.src.relabeler import config


class RelabelerApp:

    def __init__(self, dataset):
        self.dataset = dataset
        self.root = tk.Tk()
        self.interface_frame = None
        self.current_category_interface_frame = None
        self.current_video_interface_frame = None
        self.relabel_interface_frame = None
        self.add_remove_subcategory_interface_frame = None
        self.misc_interface_frame = None
        self.image_frame = None
        self.interface_subframe_list = None

        self.set_current_category_option = None
        self.set_current_video_option = None
        self.set_current_subcategory_option = None
        self.set_relabel_category_option = None
        self.set_relabel_subcategory_option = None
        self.subcategory_entry = None
        self.image_name_label = None
        self.top_image_label = None
        self.bottom_image_label = None

        self.main_window_dimensions = config.Config.main_window_dimensions
        self.small_image_dimensions = config.Config.small_image_dimensions
        self.large_image_scale = config.Config.large_image_scale
        self.interface_frame_width = config.Config.interface_frame_width
        self.big_image_y_spacing = config.Config.big_image_y_spacing
        self.num_image_rows = config.Config.num_image_rows
        self.num_image_columns = config.Config.num_image_columns

        self.left_frame_width = math.ceil(self.small_image_dimensions[0] * self.large_image_scale) + 20

        self.fill_color_option = None
        self.color_option_dict = {'red': np.array([255, 0, 0]),
                                  'green': np.array([0, 255, 0]),
                                  'blue': np.array([0, 0, 255]),
                                  'white': np.array([255, 255, 255]),
                                  'yellow': np.array([255, 255, 0])}
        self.color_option_list = list(self.color_option_dict.keys())
        self.current_fill_color = self.color_option_list[0]
        self.current_fill_color_rgb = self.color_option_dict[self.current_fill_color]

        self.category_list = None
        self.current_category = None
        self.current_category_var = None
        self.current_subcategory_list = None
        self.current_subcategory = None
        self.current_subcategory_var = None

        self.video_list = None
        self.current_video = None
        self.current_video_var = None

        self.relabel_category = None
        self.relabel_category_var = None
        self.relabel_subcategory_list = None
        self.relabel_subcategory = None
        self.relabel_subcategory_var = None

        self.add_remove_subcategory_category = None
        self.add_remove_subcategory_category_var = None

        self.num_image_rows = config.Config.num_image_rows
        self.num_image_columns = config.Config.num_image_columns
        self.max_image_labels = self.num_image_rows * self.num_image_columns

        self.preview_label_list = None
        self.preview_position_list = None
        self.preview_frame_list = None
        self.preview_image_list = None
        self.current_selections_list = None

        self.preview_category = None
        self.preview_subcategory = None
        self.preview_index = None
        self.old_preview_index = None

        self.unsaved_changes_made = False

        self.print_subcategory_string()

        self.init_application()
        self.create_main_window()
        self.create_interface_frame()
        self.create_image_frame()

    def init_application(self):
        self.category_list = self.get_category_list()
        self.current_category = self.relabel_category = self.category_list[0]

        subcategory_list = self.get_subcategory_list(self.current_category)

        self.current_subcategory_list = subcategory_list
        self.current_subcategory = self.current_subcategory_list[0]

        self.relabel_subcategory_list = subcategory_list
        self.relabel_subcategory = self.relabel_subcategory_list[0]

        self.current_video = "ALL"

    def create_main_window(self):
        self.root.configure(background='black')
        self.root.geometry("{}x{}".format(self.main_window_dimensions[0],
                                          self.main_window_dimensions[1]))
        self.root.title("Image Relabeler")
        self.root.protocol("WM_DELETE_WINDOW", self.quit)

    def create_preview_images(self):
        image_start_x = 5
        image_start_y = 40
        image_spacing = 8
        frame_border_size = 3

        self.preview_label_list = []
        self.preview_position_list = []
        self.preview_frame_list = []

        x = image_start_x
        label_counter = 0

        for i in range(self.num_image_columns):
            y = image_start_y
            for j in range(self.num_image_rows):
                position = (x, y)
                new_frame = tk.Frame(self.image_frame,
                                     height=self.small_image_dimensions[1]+frame_border_size,
                                     width=self.small_image_dimensions[0]+frame_border_size,
                                     bg="gray22")
                new_frame.pack_propagate(False)
                new_frame.place(x=position[0], y=position[1])
                new_label = tk.Label(new_frame, bg="gray22")
                new_label.pack(fill=tk.BOTH, expand=1)
                new_label.bind('<Enter>', lambda event, arg=label_counter: self.enter_image(event, arg))
                new_label.bind('<Leave>', lambda event, arg=label_counter: self.leave_image(event, arg))
                new_label.bind('<Button-1>', lambda event, arg=label_counter: self.select_image(event, arg))

                self.preview_position_list.append(position)
                self.preview_label_list.append(new_label)
                self.preview_frame_list.append(new_frame)
                y += self.small_image_dimensions[1] + image_spacing
                label_counter += 1
            x += self.small_image_dimensions[0] + image_spacing
        return x

    def create_big_images(self, x):
        image_start_y = 40

        self.image_name_label = tk.Label(self.image_frame, text="", bg="black", fg="white", font="Helvetica 20")
        self.image_name_label.place(x=x, y=5)

        image_frame_height = math.ceil(self.small_image_dimensions[1]*self.large_image_scale)
        image_frame_width = math.ceil(self.small_image_dimensions[0]*self.large_image_scale)

        top_image_frame = tk.Frame(self.image_frame,
                                   height=image_frame_height,
                                   width=image_frame_width,
                                   bg="gray22", borderwidth=0, padx=0, pady=0)

        bottom_image_frame = tk.Frame(self.image_frame,
                                      height=image_frame_height,
                                      width=image_frame_width,
                                      bg="gray22", borderwidth=0, padx=0, pady=0)

        top_image_frame.place(x=x, y=image_start_y)
        # WARNING
        bottom_image_frame.place(x=x, y=image_start_y+image_frame_height+self.big_image_y_spacing)
        top_image_frame.pack_propagate(False)
        bottom_image_frame.pack_propagate(False)

        self.top_image_label = tk.Label(top_image_frame, bg="gray22", name="top_image_label",
                                        height=image_frame_height, width=image_frame_width)
        self.top_image_label.pack(side=tk.LEFT, anchor=tk.NW)

        self.bottom_image_label = tk.Label(bottom_image_frame, bg="gray22", name="bottom_image_label",
                                           height=image_frame_height, width=image_frame_width)
        self.bottom_image_label.pack(side=tk.LEFT, anchor=tk.NW)

    def create_image_frame(self):
        self.image_frame = tk.Frame(self.root,
                                    height=self.main_window_dimensions[1],
                                    width=self.main_window_dimensions[0]-self.interface_frame_width,
                                    bg="black")
        self.image_frame.pack(side=tk.LEFT)

        x = self.create_preview_images()
        self.create_big_images(x)

    def create_interface_frame(self):
        if self.interface_frame is None:
            self.interface_frame = tk.Frame(self.root,
                                            height=self.main_window_dimensions[1],
                                            width=self.interface_frame_width,
                                            bg="grey20")
            self.interface_frame.pack(side=tk.LEFT)

        if self.current_category_interface_frame is not None:
            self.current_category_interface_frame.destroy()
        if self.current_video_interface_frame is not None:
            self.current_video_interface_frame.destroy()
        if self.relabel_interface_frame is not None:
            self.relabel_interface_frame.destroy()
        if self.add_remove_subcategory_interface_frame is not None:
            self.add_remove_subcategory_interface_frame.destroy()
        if self.misc_interface_frame is not None:
            self.misc_interface_frame.destroy()

        category_interface_height = 125
        video_interface_height = 200
        relabel_interface_height = 125
        add_remove_interface_height = 300
        misc_interface_height = self.main_window_dimensions[1] - category_interface_height - video_interface_height - relabel_interface_height - add_remove_interface_height

        self.create_current_category_interface(category_interface_height)
        self.create_current_video_interface(video_interface_height)
        self.create_relabel_interface(relabel_interface_height)
        self.create_add_remove_subcategory_interface(add_remove_interface_height)
        self.create_misc_interface(misc_interface_height)

    def create_current_category_interface(self, frame_height):

        self.current_category_interface_frame = tk.Frame(self.interface_frame,
                                                         width=self.interface_frame_width,
                                                         height=frame_height,
                                                         bg="grey20")
        self.current_category_interface_frame.pack()

        tk.Label(self.current_category_interface_frame, text="Current Category", bg="grey20", fg="white").place(x=10, y=0)
        self.current_category_var = tk.StringVar()
        self.current_category_var.set(self.current_category)
        self.set_current_category_option = tk.OptionMenu(self.current_category_interface_frame,
                                                         self.current_category_var,
                                                         *self.category_list,
                                                         command=self.set_current_category)
        self.set_current_category_option.config(width=10)
        self.set_current_category_option.place(x=10, y=25)

        self.current_subcategory_var = tk.StringVar()
        self.current_subcategory_var.set(self.current_subcategory)

        self.current_subcategory_list = self.get_subcategory_list(self.current_category)

        self.set_current_subcategory_option = tk.OptionMenu(self.current_category_interface_frame,
                                                            self.current_subcategory_var,
                                                            *self.current_subcategory_list,
                                                            command=self.set_current_subcategory)
        self.set_current_subcategory_option.config(width=10)
        self.set_current_subcategory_option.place(x=10, y=51)
        tk.Button(self.current_category_interface_frame, name="show_images_button", text="Show Images",
                  command=self.show_previews, width=10).place(x=10, y=81)

    def create_current_video_interface(self, frame_height):
        self.current_video_interface_frame = tk.Frame(self.interface_frame,
                                                      width=self.interface_frame_width,
                                                      height=frame_height,
                                                      bg="grey20")
        self.current_video_interface_frame.pack()

        tk.Label(self.current_video_interface_frame, text="Current Video", bg="grey20", fg="white").place(
            x=10, y=0)

        self.video_list = self.get_video_list()
        self.current_video_var = tk.StringVar()
        self.current_video_var.set(self.video_list[0])
        self.set_current_video_option = tk.OptionMenu(self.current_video_interface_frame,
                                                      self.current_video_var,
                                                      *self.video_list,
                                                      command=self.set_current_video)
        self.set_current_video_option.config(width=10)
        self.set_current_video_option.place(x=10, y=25)

    def create_add_remove_subcategory_interface(self, frame_height):

        self.add_remove_subcategory_interface_frame = tk.Frame(self.interface_frame,
                                                               width=self.interface_frame_width,
                                                               height=frame_height,
                                                               bg="grey20")
        self.add_remove_subcategory_interface_frame.pack()

        tk.Label(self.add_remove_subcategory_interface_frame, text="+/- Subcategory", bg="grey20", fg="white").place(x=10, y=0)
        self.add_remove_subcategory_category = self.category_list[0]
        self.add_remove_subcategory_category_var = tk.StringVar()
        self.add_remove_subcategory_category_var.set(self.category_list[0])
        self.set_relabel_category_option = tk.OptionMenu(self.add_remove_subcategory_interface_frame,
                                                         self.add_remove_subcategory_category_var,
                                                         *self.category_list,
                                                         command=self.set_change_subcategory_category)
        self.set_relabel_category_option.config(width=10)
        self.set_relabel_category_option.place(x=10, y=25)

        self.subcategory_entry = tk.Entry(self.add_remove_subcategory_interface_frame,
                                          name="subcategory_entry", bg="grey25", fg="white", width=15)
        self.subcategory_entry.place(x=10, y=55)

        tk.Button(self.add_remove_subcategory_interface_frame, name="add_subcategory_button", text="Add Subcategory",
                  command=self.add_subcategory, width=12).place(x=10, y=81)
        tk.Button(self.add_remove_subcategory_interface_frame,
                  name="remove_subcategory_button",
                  text="Remove Subcategory",
                  command=self.remove_subcategory, width=12).place(x=10, y=107)

    def create_relabel_interface(self, frame_height):

        self.relabel_interface_frame = tk.Frame(self.interface_frame,
                                                width=self.interface_frame_width,
                                                height=frame_height,
                                                bg="grey20")
        self.relabel_interface_frame.pack()

        tk.Label(self.relabel_interface_frame, text="Relabel Category",  fg="white", bg="grey20").place(x=10, y=0)
        self.relabel_category_var = tk.StringVar()
        self.relabel_category_var.set(self.relabel_category)
        self.set_relabel_category_option = tk.OptionMenu(self.relabel_interface_frame,
                                                         self.relabel_category_var,
                                                         *self.category_list,
                                                         command=self.set_relabel_category)
        self.set_relabel_category_option.config(width=10)
        self.set_relabel_category_option.place(x=10, y=25)

        self.relabel_subcategory_list = self.get_subcategory_list(self.relabel_category)

        self.relabel_subcategory_var = tk.StringVar()
        self.relabel_subcategory_var.set(self.relabel_subcategory)
        self.set_relabel_subcategory_option = tk.OptionMenu(self.relabel_interface_frame,
                                                            self.relabel_subcategory_var,
                                                            *self.relabel_subcategory_list,
                                                            command=self.set_relabel_subcategory)
        self.set_relabel_subcategory_option.config(width=10)
        self.set_relabel_subcategory_option.place(x=10, y=51)
        tk.Button(self.relabel_interface_frame, name="relabel_images_button", text="Relabel Images",
                  command=self.relabel_images, width=10).place(x=10, y=81)

    def create_misc_interface(self, frame_height):
        self.misc_interface_frame = tk.Frame(self.interface_frame,
                                             width=self.interface_frame_width,
                                             height=frame_height,
                                             bg="grey20")
        self.misc_interface_frame.pack()

        tk.Label(self.misc_interface_frame, text="Change Highlight Color", bg="grey20",  fg="white").place(x=10, y=0)

        current_color_var = tk.StringVar()
        current_color_var.set(self.color_option_list[0])
        self.fill_color_option = tk.OptionMenu(self.misc_interface_frame,
                                               current_color_var,
                                               *self.color_option_list,
                                               command=self.set_current_color)
        self.fill_color_option.config(width=10)
        self.fill_color_option.place(x=10, y=25)

        tk.Button(self.misc_interface_frame, name="save_button", text="Save", width=8,
                  command=self.save).place(x=5, y=51)
        tk.Button(self.misc_interface_frame, name="quit_button", text="Quit", width=8,
                  command=self.quit).place(x=5, y=81)

    def get_category_list(self):
        category_list = self.dataset.get_category_list()
        category_list.sort()
        return category_list

    def get_subcategory_list(self, category):
        self.dataset.generate_subcategory_df()
        subcategory_list = self.dataset.get_subcategory_list(category)
        subcategory_list.sort()
        if "None" in subcategory_list:
            subcategory_list.remove("None")
            subcategory_list.insert(0, "None")
        return subcategory_list

    def get_video_list(self):
        unique_df = self.dataset.image_df.drop_duplicates(subset=['participant', 'video_name'])
        sorted_video_tuple_list = sorted(list(zip(unique_df['participant'], unique_df['video_name'])))
        string_list = [f"{tup[0]}-{tup[1]}" for tup in sorted_video_tuple_list]
        string_list = ["ALL"] + string_list
        return string_list

    def set_current_video(self, selection):
        self.current_video = selection
        self.current_video_var.set(selection)

        # get the current image_list
        print("Current video changed to {}".format(self.current_video))

    def set_current_category(self, selection):
        self.current_category = selection
        self.current_category_var.set(selection)

        self.current_subcategory_list = self.get_subcategory_list(self.current_category)
        self.set_current_subcategory_option['menu'].delete(0, 'end')

        # Add new menu options based on the current category
        for current_subcategory in self.current_subcategory_list:
            self.set_current_subcategory_option['menu'].add_command(label=current_subcategory,
                                                                    command=lambda subcategory=current_subcategory:
                                                                    self.set_current_subcategory(subcategory))

        if self.current_subcategory_list:
            self.current_subcategory = self.current_subcategory_list[0]
            self.set_current_subcategory_option['text'] = self.current_subcategory

        self.current_subcategory = self.current_subcategory_list[0]
        print("Current category changed to {}".format(self.current_category))

    def set_current_subcategory(self, selection):
        self.current_subcategory = selection
        self.current_subcategory_var.set(selection)
        print("Current subcategory changed to {}".format(self.current_subcategory))

    def set_relabel_category(self, selection):
        self.relabel_category = selection
        self.relabel_category_var.set(selection)

        self.relabel_subcategory_list = self.get_subcategory_list(self.relabel_category)
        menu = self.set_relabel_subcategory_option['menu'].delete(0, 'end')

        # Add new menu options based on the current category
        for relabel_subcategory in self.relabel_subcategory_list:
            menu.add_command(label=relabel_subcategory,
                             command=lambda subcategory=relabel_subcategory: self.set_relabel_subcategory(subcategory))

        self.relabel_subcategory = self.relabel_subcategory_list[0]
        print("Relabel category changed to {}".format(self.relabel_category))

    def set_relabel_subcategory(self, selection):
        self.relabel_subcategory = selection
        self.relabel_subcategory_var.set(selection)
        print("Relabel subcategory changed to {}".format(self.relabel_subcategory))

    def set_change_subcategory_category(self, selection):
        self.add_remove_subcategory_category = selection
        self.add_remove_subcategory_category_var.set(selection)
        print("Current change subcategory category changed to {}".format(self.add_remove_subcategory_category))

    def set_current_color(self, selection):
        self.current_fill_color = selection
        self.current_fill_color_rgb = self.color_option_dict[self.current_fill_color]

    def add_subcategory(self):
        new_subcategory = self.subcategory_entry.get()
        print("Adding subcategory", new_subcategory)
        self.dataset.add_subcategory(self.add_remove_subcategory_category, new_subcategory)
        if self.add_remove_subcategory_category == self.current_category:
            self.create_interface_frame()

        if self.add_remove_subcategory_category == self.relabel_category:
            self.create_interface_frame()
        print(self.dataset.subcategory_df)

    def remove_subcategory(self):
        subcategory = self.subcategory_entry.get()
        print("Removing subcategory", subcategory)
        if subcategory:
            if subcategory == "None":
                tk.messagebox.showerror("ERROR", "Cannot remove subcategory 'None'")
            else:
                filtered_rows = self.dataset.subcategory_df[(self.dataset.subcategory_df['subcategory'] == subcategory) & (self.dataset.subcategory_df['category'] == self.add_remove_subcategory_category)]
                if filtered_rows.empty:
                    tk.messagebox.showerror("ERROR", "Cannot remove because it doesn't exist in that category")
                else:
                    if filtered_rows.iloc[0]['count'] == 0:
                        self.dataset.remove_subcategory(self.add_remove_subcategory_category, subcategory)

                        if self.add_remove_subcategory_category == self.current_category:
                            self.create_interface_frame()

                        if self.add_remove_subcategory_category == self.relabel_category:
                            self.create_interface_frame()

                    else:
                        tk.messagebox.showerror("ERROR", "Cannot remove subcategory with assigned instances")
        print(self.dataset.subcategory_df)

    def get_preview_instance_list(self):

        if self.current_video == "ALL":
            filtered_df = self.dataset.instance_df[(self.dataset.instance_df['category'] == self.preview_category) & (
                        self.dataset.instance_df['subcategory'] == self.preview_subcategory)]
        else:
            filtered_df = self.dataset.instance_df[(self.dataset.instance_df['category'] == self.preview_category) & (
                    self.dataset.instance_df['subcategory'] == self.preview_subcategory) & (self.dataset.instance_df['video_name'] == self.current_video)]

        instance_list = filtered_df.values.tolist()

        return instance_list

    def show_previews(self, increment_index=True):

        self.preview_image_list = []
        self.current_selections_list = []

        if self.current_category != self.preview_category:
            self.preview_index = 0

        if self.current_subcategory != self.preview_subcategory:
            self.preview_index = 0

        if not increment_index:
            self.preview_index = self.old_preview_index

        self.preview_category = self.current_category
        self.preview_subcategory = self.current_subcategory

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

                instance_data_list += self.get_image_data(instance_data_list[:3])

                self.preview_image_list.append(instance_data_list)

                raw_image_path = self.get_image_path(instance_data_list)

                pil_image = Image.open(raw_image_path + ".jpg")
                resized_image = pil_image.resize((self.small_image_dimensions[0],
                                                  self.small_image_dimensions[1]),
                                                 Image.Resampling.LANCZOS)
                tk_image = ImageTk.PhotoImage(resized_image)
                self.preview_label_list[i].configure(image=tk_image)
                self.preview_label_list[i].image = tk_image

                self.preview_index += 1
                if self.preview_index == len(instance_list):
                    self.preview_index = 0
        else:
            tk.messagebox.showinfo(message="There are no images in {}:{} to show.".format(self.preview_category,
                                                                                          self.preview_subcategory))

    def get_image_data(self, image_info_list):

        dt = self.dataset.image_df[
            (self.dataset.image_df['participant'] == image_info_list[0]) &
            (self.dataset.image_df['video_name'] == image_info_list[1]) &
            (self.dataset.image_df['frame'] == image_info_list[2])
            ]['dt'].iloc[0]

        return [dt]

    def get_image_path(self, instance_data_list):
        # ../superannotate_datasets/DTW2/video-7was5_DTW_2022_01_03_1640/DTW_2022_01_03_1640_013300.jpg
        video_name = str(instance_data_list[1])
        participant = instance_data_list[0]
        dt = instance_data_list[-1]
        frame = str(instance_data_list[2]).zfill(6)

        path = self.dataset.sa_dataset_path + "/" + video_name + "/"
        filename = path + participant + "_" + dt + "_" + frame

        return filename

    def resize_image(self, input_image):
        rescaled_x = int(self.small_image_dimensions[0] * self.large_image_scale)
        rescaled_y = int(self.small_image_dimensions[1] * self.large_image_scale)
        output_image = input_image.resize((rescaled_x, rescaled_y), Image.Resampling.LANCZOS)
        return output_image

    def get_image_matrix(self, instance, version):

        raw_image_path = self.get_image_path(instance)

        if version == 'raw':
            image_filename = (raw_image_path + ".jpg")
        elif version == 'unique':
            image_filename = (raw_image_path + ".jpg___save.png")
        else:
            raise Exception('Unrecognized image version', version)
        pil_image = Image.open(image_filename).convert('RGB')
        resized_image = self.resize_image(pil_image)
        image_matrix = np.asarray(copy.deepcopy(resized_image))
        return image_matrix

    def get_recolored_target_instance_image(self, raw_image_matrix, current_instance, label_counter):
        unique_image_matrix = self.get_image_matrix(current_instance, "unique")
        target_image_matrix = copy.deepcopy(raw_image_matrix)
        current_instance_hex_rgb = current_instance[6]
        r, g, b = [int(current_instance_hex_rgb[i:i + 2], 16) for i in (1, 3, 5)]

        target_color = np.array([r, g, b])
        mask = np.all(unique_image_matrix == target_color, axis=2)
        target_image_matrix[mask] = self.current_fill_color_rgb

        target_image = Image.fromarray(np.uint8(target_image_matrix))

        return target_image

    @staticmethod
    def show_image(the_image, location):
        raw_tk_image = ImageTk.PhotoImage(the_image)
        location.configure(image=raw_tk_image)
        location.image = raw_tk_image

    def enter_image(self, event, label_counter):
        if self.preview_image_list is not None:
            if label_counter < len(self.preview_image_list):
                current_instance = self.preview_image_list[label_counter]

                raw_image_matrix = self.get_image_matrix(current_instance, "raw")
                resized_raw_image = Image.fromarray(np.uint8(raw_image_matrix))

                target_image = self.get_recolored_target_instance_image(raw_image_matrix,
                                                                        current_instance,
                                                                        label_counter)

                self.show_image(resized_raw_image, self.top_image_label)
                self.show_image(target_image, self.bottom_image_label)
                image_name = f"{current_instance[0]}_{current_instance[1]}_{current_instance[2]}_{current_instance[3]}"
                self.image_name_label.configure(text=image_name)

                self.root.update()

    def leave_image(self, event, arg):
        self.top_image_label.configure(image="")
        self.top_image_label.image = ""
        self.bottom_image_label.configure(image="")
        self.bottom_image_label.image = ""
        self.image_name_label.configure(text="")

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

    def change_image_category(self, instance):
        messagebox.showinfo(message="This feature is not yet implemented")

    def change_image_subcategory(self, instance):
        index = instance[3]
        old_subcategory = instance[5]

        if old_subcategory != self.relabel_subcategory:
            self.dataset.instance_df.loc[self.dataset.instance_df['instance_id'] == index, 'subcategory'] = self.relabel_subcategory
            self.unsaved_changes_made = True
            self.dataset.generate_subcategory_df()
        else:
            messagebox.showerror(message="Can't change subcategory because already in subcategory")

    def relabel_images(self):

        self.relabel_category = self.relabel_category_var.get()
        self.relabel_subcategory = self.relabel_subcategory_var.get()

        for i in range(len(self.current_selections_list)):
            if self.current_selections_list[i]:
                current_instance = self.preview_image_list[i]

                if self.preview_category != self.relabel_category:
                    response = messagebox.askyesno(
                        "WARNING", "You are changing the image's primary category. Are you sure you want to continue?")
                    if response:
                        self.change_image_category(current_instance)
                else:
                    self.change_image_subcategory(current_instance)
        self.print_subcategory_string()
        self.show_previews(False)

    def print_subcategory_string(self):
        result = self.dataset.subcategory_df.apply(lambda row: f"{row['category']} {row['subcategory']} {row['count']}", axis=1).tolist()
        print()
        for thing in result:
            print(thing)
        print()

    def save(self):
        self.dataset.save_dataset()
        self.unsaved_changes_made = False
        messagebox.showinfo(message="You have saved your changes")

    def quit(self):
        if self.unsaved_changes_made:
            response = messagebox.askyesno(
                "WARNING", "You are attempting to quit without saving changes. Are you sure you want to quit?")
            if response:
                self.root.destroy()
        else:
            self.root.destroy()
