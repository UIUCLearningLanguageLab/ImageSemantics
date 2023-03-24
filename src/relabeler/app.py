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
        self.dataset_path = None
        self.root = tk.Tk()
        self.interface_frame = None
        self.image_frame = None
        self.interface_subframe_list = None
        self.set_current_category_option = None
        self.set_current_subcategory_option = None
        self.set_relabel_category_option = None
        self.set_relabel_subcategory_option = None
        self.subcategory_entry = None
        self.image_name_label = None
        self.top_image_label = None
        self.bottom_image_label = None
        self.current_category_var = None
        self.current_subcategory_var = None
        self.change_subcategory_category_var = None
        self.change_subcategory_category = None
        self.relabel_category_var = None
        self.relabel_subcategory_var = None

        self.main_window_dimensions = config.Config.main_window_dimensions
        self.small_image_dimensions = config.Config.small_image_dimensions
        self.large_image_scale = config.Config.large_image_scale
        self.interface_frame_width = config.Config.interface_frame_width
        self.mini_frame_height = config.Config.mini_frame_height
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
        self.current_subcategory = None
        self.current_subcategory_list = None
        self.relabel_category = None
        self.relabel_subcategory = None
        self.relabel_subcategory_list = None

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

        self.unsaved_changes_made = False

        self.init_categories()
        self.create_main_window()
        self.create_interface_frame()
        self.create_image_frame()

    def init_categories(self):
        self.category_list = self.dataset.category_name_list
        self.category_list.sort()
        self.current_category = self.relabel_category = self.category_list[0]

        self.current_subcategory_list = self.relabel_subcategory_list = self.get_subcategory_list(self.current_category)

        self.current_subcategory = self.current_subcategory_list[0]
        self.relabel_subcategory = self.relabel_subcategory_list[0]

    def create_main_window(self):
        self.root.configure(background='black')
        self.root.geometry("{}x{}".format(self.main_window_dimensions[0],
                                          self.main_window_dimensions[1]))
        self.root.title("Image Relabeler")
        self.root.protocol("WM_DELETE_WINDOW", self.quit)

    # def disable_close_button(self):
    #     pass

    def create_preview_images(self):
        image_start_x = 5
        image_start_y = 10
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
        self.interface_frame = tk.Frame(self.root,
                                        height=self.main_window_dimensions[1],
                                        width=self.interface_frame_width,
                                        bg="grey20")
        self.interface_frame.pack(side=tk.LEFT)

        self.interface_subframe_list = []
        for i in range(4):
            if i == 3:
                the_height = self.main_window_dimensions[0] - 3 * self.mini_frame_height
            else:
                the_height = self.mini_frame_height
            new_frame = tk.Frame(self.interface_frame,
                                 width=self.interface_frame_width,
                                 height=the_height,
                                 bg="grey20")
            new_frame.pack()
            self.interface_subframe_list.append(new_frame)

        self.create_current_category_interface(self.interface_subframe_list[0])
        self.create_relabel_interface(self.interface_subframe_list[1])
        self.create_new_subcategory_interface(self.interface_subframe_list[2])
        self.create_misc_interface(self.interface_subframe_list[3])

    def create_misc_interface(self, parent_frame):
        tk.Label(parent_frame, text="Change Highlight Color", bg="grey20").place(x=10, y=0)

        current_color_var = tk.StringVar()
        current_color_var.set(self.color_option_list[0])
        self.fill_color_option = tk.OptionMenu(parent_frame,
                                               current_color_var,
                                               *self.color_option_list,
                                               command=self.set_current_color)
        self.fill_color_option.config(width=10)
        self.fill_color_option.place(x=10, y=25)

        tk.Button(parent_frame, name="save_button", text="Save", width=8,
                  command=self.save).place(x=5, y=51)
        tk.Button(parent_frame, name="quit_button", text="Quit", width=8,
                  command=self.quit).place(x=5, y=81)

    def create_current_category_interface(self, parent_frame):
        tk.Label(parent_frame, text="Current Category", bg="grey20").place(x=10, y=0)
        self.current_category_var = tk.StringVar()
        self.current_category_var.set(self.current_category)
        self.set_current_category_option = tk.OptionMenu(parent_frame,
                                                         self.current_category_var,
                                                         *self.category_list,
                                                         command=self.set_current_category)
        self.set_current_category_option.config(width=10)
        self.set_current_category_option.place(x=10, y=25)

        self.current_subcategory_var = tk.StringVar()
        self.current_subcategory_var.set(self.current_subcategory)
        self.set_current_subcategory_option = tk.OptionMenu(parent_frame,
                                                            self.current_subcategory_var,
                                                            *self.current_subcategory_list,
                                                            command=self.set_current_subcategory)
        self.set_current_subcategory_option.config(width=10)
        self.set_current_subcategory_option.place(x=10, y=51)
        tk.Button(parent_frame, name="show_images_button", text="Show Images",
                  command=self.show_previews, width=10).place(x=10, y=81)

    def create_new_subcategory_interface(self, parent_frame):
        tk.Label(parent_frame, text="+/- Subcategory", bg="grey20").place(x=10, y=0)
        self.change_subcategory_category = self.category_list[0]
        self.change_subcategory_category_var = tk.StringVar()
        self.change_subcategory_category_var.set(self.category_list[0])
        self.set_relabel_category_option = tk.OptionMenu(parent_frame,
                                                         self.change_subcategory_category_var,
                                                         *self.category_list,
                                                         command=self.set_change_subcategory_category)
        self.set_relabel_category_option.config(width=10)
        self.set_relabel_category_option.place(x=10, y=25)

        self.subcategory_entry = tk.Entry(parent_frame, name="subcategory_entry", bg="grey25", fg="white", width=15)
        self.subcategory_entry.place(x=10, y=55)

        tk.Button(parent_frame, name="add_subcategory_button", text="Add Subcategory",
                  command=self.add_subcategory, width=12).place(x=10, y=81)
        tk.Button(parent_frame, name="remove_subcategory_button", text="Remove Subcategory",
                  command=self.remove_subcategory, width=12).place(x=10, y=107)


    def create_relabel_interface(self, parent_frame):
        tk.Label(parent_frame, text="Relabel Category", bg="grey20").place(x=10, y=0)
        self.relabel_category_var = tk.StringVar()
        self.relabel_category_var.set(self.relabel_category)
        self.set_relabel_category_option = tk.OptionMenu(parent_frame,
                                                         self.relabel_category_var,
                                                         *self.category_list,
                                                         command=self.set_relabel_category)
        self.set_relabel_category_option.config(width=10)
        self.set_relabel_category_option.place(x=10, y=25)

        self.relabel_subcategory_var = tk.StringVar()
        self.relabel_subcategory_var.set(self.relabel_subcategory)
        self.set_relabel_subcategory_option = tk.OptionMenu(parent_frame,
                                                            self.relabel_subcategory_var,
                                                            *self.relabel_subcategory_list,
                                                            command=self.set_relabel_subcategory)
        self.set_relabel_subcategory_option.config(width=10)
        self.set_relabel_subcategory_option.place(x=10, y=51)
        tk.Button(parent_frame, name="relabel_images_button", text="Relabel Images",
                  command=self.relabel_images, width=10).place(x=10, y=81)

    def get_subcategory_list(self, category):
        subcategory_list = list(self.dataset.category_dict[category].subcategory_dict.keys())
        subcategory_list.sort()
        subcategory_list.insert(0, "None")
        return subcategory_list

    def set_current_category(self, selection):
        self.current_category = selection
        self.current_category_var.set(selection)
        self.update_current_subcategory_list()
        self.current_subcategory = self.current_subcategory_list[0]
        print("Current category changed to {}".format(self.current_category))

    def set_current_subcategory(self, selection):
        self.current_subcategory = selection
        self.current_subcategory_var.set(selection)
        print("Current subcategory changed to {}".format(self.current_subcategory))

    def set_change_subcategory_category(self, selection):
        self.change_subcategory_category = selection
        self.change_subcategory_category_var.set(selection)
        print("Current change subcategory category changed to {}".format(self.change_subcategory_category))

    def set_relabel_category(self, selection):
        self.relabel_category = selection
        self.relabel_category_var.set(selection)
        self.update_relabel_subcategory_list()
        self.relabel_subcategory = self.relabel_subcategory_list[0]
        print("Relabel category changed to {}".format(self.relabel_category))

    def set_relabel_subcategory(self, selection):
        self.relabel_subcategory = selection
        self.relabel_subcategory_var.set(selection)
        print("Relabel subcategory changed to {}".format(self.relabel_subcategory))

    def set_current_color(self, selection):
        self.current_fill_color = selection
        self.current_fill_color_rgb = self.color_option_dict[self.current_fill_color]

    def update_current_subcategory_list(self):
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

    def update_relabel_subcategory_list(self):
        self.relabel_subcategory_list = self.get_subcategory_list(self.relabel_category)

        menu = self.set_relabel_subcategory_option['menu']
        menu.delete(0, 'end')

        # Add new menu options based on the current category
        for relabel_subcategory in self.relabel_subcategory_list:
            menu.add_command(label=relabel_subcategory,
                             command=lambda subcategory=relabel_subcategory: self.set_relabel_subcategory(subcategory))

    def add_subcategory(self):
        subcategory = self.subcategory_entry.get()
        if subcategory:
            if subcategory not in self.dataset.category_dict[self.change_subcategory_category].subcategory_dict:
                self.dataset.add_subcategory(self.change_subcategory_category, subcategory)
                self.update_current_subcategory_list()
                self.update_relabel_subcategory_list()
                self.unsaved_changes_made = True
                print("Added {} to {}".format(subcategory, self.change_subcategory_category))
            else:
                print("Cannot add {} to {} it already exists".format(subcategory, self.change_subcategory_category))
            self.subcategory_entry.delete(0, 'end')

    def remove_subcategory(self):
        subcategory = self.subcategory_entry.get()
        print(subcategory)
        if subcategory:
            if subcategory == "None":
                tk.messagebox.showerror("Cannot remove subcategory 'None'")
            elif subcategory in self.dataset.category_dict[self.change_subcategory_category].subcategory_dict:
                print(self.change_subcategory_category, self.dataset.category_dict[self.change_subcategory_category].subcategory_dict)
                num_instances = len(self.dataset.category_dict[self.change_subcategory_category].subcategory_dict[subcategory].instance_dict)
                if num_instances:
                    tk.messagebox.showerror("Cannot remove subcategory with instances ({})".format(num_instances))
                else:
                    del self.dataset.category_dict[self.change_subcategory_category].subcategory_dict[subcategory]
                    # TODO deal with what happens if removed subcategory is current_subcategory or relabel_subcategory
                    self.update_current_subcategory_list()
                    self.update_relabel_subcategory_list()
                    self.unsaved_changes_made = True
                    messagebox.showinfo(message="Removed {} from {}".format(subcategory,
                                                                            self.change_subcategory_category))
            else:
                print("HERE")
                tk.messagebox.showerror(
                    message="Cannot remove {} from {} as it doesn't exist".format(subcategory,
                                                                                  self.change_subcategory_category))
            self.subcategory_entry.delete(0, 'end')

    def show_previews(self):

        self.preview_image_list = []
        self.current_selections_list = []

        if self.current_category != self.preview_category:
            self.preview_index = 0

        if self.current_subcategory != self.preview_subcategory:
            self.preview_index = 0

        self.preview_category = self.current_category
        self.preview_subcategory = self.current_subcategory

        if self.preview_subcategory == "None":
            instance_dict = self.dataset.category_dict[self.preview_category].instance_dict
        else:
            instance_dict = self.dataset.category_dict[self.preview_category].subcategory_dict[self.preview_subcategory].instance_dict

        instance_list = list(instance_dict.values())
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

        if num_images_to_show:
            for i in range(num_images_to_show):
                self.current_selections_list.append(False)

                instance = instance_list[self.preview_index]
                self.preview_image_list.append(instance)

                raw_image_filename = (instance.image.path + "/" + instance.image.jpg_file_name)
                pil_image = Image.open(raw_image_filename)
                resized_image = pil_image.resize((self.small_image_dimensions[0],
                                                  self.small_image_dimensions[1]),
                                                 Image.ANTIALIAS)
                tk_image = ImageTk.PhotoImage(resized_image)
                self.preview_label_list[i].configure(image=tk_image)
                self.preview_label_list[i].image = tk_image

                self.preview_index += 1
                if self.preview_index == len(instance_list):
                    self.preview_index = 0
        else:
            tk.messagebox.showinfo(message="There are no images in {}:{} to show.".format(self.preview_category,
                                                                                          self.preview_subcategory))

    def resize_image(self, input_image):
        rescaled_x = int(self.small_image_dimensions[0] * self.large_image_scale)
        rescaled_y = int(self.small_image_dimensions[1] * self.large_image_scale)
        output_image = input_image.resize((rescaled_x, rescaled_y), Image.ANTIALIAS)
        return output_image

    def get_image_matrix(self, instance, version):
        if version == 'raw':
            image_filename = (instance.image.path + "/" + instance.image.jpg_file_name)
        elif version == 'unique':
            image_filename = (instance.image.path + "/" + instance.image.unique_mask_file_name)
        else:
            raise Exception('Unrecognized image version', version)

        pil_image = Image.open(image_filename).convert('RGB')
        resized_image = self.resize_image(pil_image)
        image_matrix = np.asarray(copy.deepcopy(resized_image))
        return image_matrix

    def get_recolored_target_instance_image(self, raw_image_matrix, current_instance, label_counter):
        unique_image_matrix = self.get_image_matrix(current_instance, "unique")
        target_image_matrix = copy.deepcopy(raw_image_matrix)
        current_instance_hex_rgb = current_instance.color
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

                self.image_name_label.configure(text=current_instance.image.name)

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
        # TODO Known Bug: if you change an instance's category to a new category, with an old subcategory that doesnt exist in
        # the new category, I am not sure what happens

        old_category = instance.category
        old_subcategory = instance.subcategory

        if instance.category != self.relabel_category:

            if instance.id_number in self.dataset.category_dict[old_category].instance_dict or instance.id_number in self.dataset.category_dict[old_category].subcategory_dict[old_subcategory].instance_dict:

                if instance.id_number not in self.dataset.category_dict[self.relabel_category].instance_dict:

                    # remove from the old category
                    if old_subcategory == "None":
                        del self.dataset.category_dict[old_category].instance_dict[instance.id_number]
                        instance.subcategory = self.relabel_subcategory
                    elif old_subcategory in self.dataset.category_dict[old_category].subcategory_dict:
                        del self.dataset.category_dict[old_category].subcategory_dict[old_subcategory].instance_dict[
                            instance.id_number]
                        instance.subcategory = self.relabel_subcategory
                    else:
                        print("Cant change category due to problem with the subcategory")

                    # add to the new category
                    if self.relabel_subcategory == "None":
                        self.dataset.category_dict[self.relabel_category].instance_dict[instance.id_number] = instance
                        instance.category = self.relabel_category
                    elif self.relabel_subcategory in self.dataset.category_dict[self.relabel_category].subcategory_dict:
                        self.dataset.category_dict[self.relabel_category].subcategory_dict[self.relabel_subcategory].instance_dict[instance.id_number] = instance
                        instance.category = self.relabel_category
                    else:
                        print("Cant change category into subcategory that the category doesnt have. Create the subcategory first.")
                else:
                    print("The instance is already in the new category")
            else:
                print("The instance is not in the old category instance dict")
        else:
            print("The instance's category and the relabel category are the same")

    def change_image_subcategory(self, instance):

        old_subcategory = instance.subcategory

        if instance.id_number not in self.dataset.category_dict[self.relabel_category].subcategory_dict[self.relabel_subcategory].instance_dict:
            if old_subcategory == "None":
                self.dataset.category_dict[self.relabel_category].subcategory_dict[self.relabel_subcategory].instance_dict[instance.id_number] = instance
                del self.dataset.category_dict[self.relabel_category].instance_dict[instance.id_number]
                instance.subcategory = self.relabel_subcategory
                self.unsaved_changes_made = True
            elif instance.id_number in self.dataset.category_dict[self.relabel_category].subcategory_dict[old_subcategory].instance_dict:
                self.dataset.category_dict[self.relabel_category].subcategory_dict[self.relabel_subcategory].instance_dict[instance.id_number] = instance
                del self.dataset.category_dict[self.relabel_category].subcategory_dict[old_subcategory].instance_dict[instance.id_number]
                instance.subcategory = self.relabel_subcategory
                self.unsaved_changes_made = True
            else:
                messagebox.showerror(message="Can't change subcategory because of problem with existing subcategory")
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
        self.show_previews()

    def save(self):
        self.dataset.save_dataset()
        self.unsaved_changes_made = False
        messagebox.showinfo(message="You have saved your changes")

    def quit(self):
        if self.unsaved_changes_made:
            messagebox.showerror(message="You cannot quit without saving changes")
        else:
            self.root.destroy()
