import tkinter as tk
from tkinter import messagebox
import re
from ImageSemantics.src.relabeler import config


class InterfaceFrame:

    def __init__(self, app):
        self.app = app
        self.dimensions = (config.Config.main_window_dimensions[0], config.Config.interface_frame_height)

        # interface frame variables
        self.interface_frame = None

        # set current category variables
        self.current_category_title = None
        self.set_current_category_option = None
        self.current_subcategory_title = None
        self.set_current_subcategory_option = None
        self.show_images_button = None

        # set current video interface variables
        self.set_current_video_title = None
        self.set_current_video_option = None

        # relabel interface variables
        self.relabel_subcategory_title = None
        self.set_relabel_subcategory_option = None
        self.relabel_subcategory_button = None

        # add-remove subcategory interface variables
        self.add_remove_subcategory_title = None
        self.add_subcategory_button = None
        self.remove_subcategory_button = None
        self.add_remove_subcategory_entry = None

        self.create_interface_frame()

    @staticmethod
    def create_option_menu(parent, current_selection, choice_list, result, option_width, x, y):
        option_widget = tk.OptionMenu(parent,
                                      current_selection,
                                      *choice_list,
                                      command=result)
        option_widget.config(width=option_width, borderwidth=0, highlightthickness=0, relief='flat')
        option_widget.place(x=x, y=y)
        return option_widget

    @staticmethod
    def create_button(parent, text, command, width, x, y):
        new_button = tk.Button(parent,
                               text=text,
                               command=command,
                               width=width,
                               borderwidth=0,
                               highlightthickness=0,
                               relief='flat')
        new_button.place(x=x, y=y)
        return new_button

    @staticmethod
    def create_label(parent, text, bg_color, fg_color, x, y):
        label_widget = tk.Label(parent, text=text, bg=bg_color, fg=fg_color)
        label_widget.place(x=x, y=y)
        return label_widget

    def refresh_subcategory_options(self):
        self.app.current_subcategory_list = self.app.dataset.get_subcategory_list(self.app.current_category)
        self.set_current_subcategory_option = self.create_option_menu(self.interface_frame,
                                                                      self.app.current_subcategory_var,
                                                                      self.app.current_subcategory_list,
                                                                      self.set_current_subcategory,
                                                                      10,
                                                                      160,
                                                                      25)

        self.app.relabel_subcategory_list = self.app.dataset.get_subcategory_list(self.app.current_category)
        self.set_relabel_subcategory_option = self.create_option_menu(self.interface_frame,
                                                                      self.app.relabel_subcategory_var,
                                                                      self.app.relabel_subcategory_list,
                                                                      self.set_relabel_subcategory,
                                                                      10,
                                                                      710,
                                                                      25)

    def create_interface_frame(self):
        if self.interface_frame is not None:
            self.interface_frame.destroy()

        self.interface_frame = tk.Frame(self.app.root,
                                        width=self.dimensions[0],
                                        height=self.dimensions[1],
                                        bg="grey20",
                                        bd=5, relief=tk.RIDGE)

        self.current_category_title = self.create_label(self.interface_frame,
                                                        "Current Category",
                                                        "grey20",
                                                        "white",
                                                        10,
                                                        0)

        self.set_current_category_option = self.create_option_menu(self.interface_frame,
                                                                   self.app.current_category_var,
                                                                   self.app.category_list,
                                                                   self.set_current_category,
                                                                   10,
                                                                   8, 25)

        self.current_subcategory_title = self.create_label(self.interface_frame,
                                                           "Current Subcategory",
                                                           "grey20",
                                                           "white",
                                                           160,
                                                           0)

        self.set_current_video_title = self.create_label(self.interface_frame,
                                                         "Current Video",
                                                         "grey20",
                                                         "white",
                                                         310,
                                                         0)

        self.set_current_video_option = self.create_option_menu(self.interface_frame,
                                                                self.app.current_video_var,
                                                                self.app.video_list,
                                                                self.set_current_video,
                                                                10,
                                                                310,
                                                                25)

        self.show_images_button = self.create_button(self.interface_frame,
                                                     "Show Images",
                                                     self.app.image_preview_frame.update_preview_frame,
                                                     10,
                                                     460,
                                                     25)

        self.relabel_subcategory_title = self.create_label(self.interface_frame,
                                                           "Relabel Subcategory",
                                                           "grey20",
                                                           "white",
                                                           710,
                                                           0)

        self.relabel_subcategory_button = self.create_button(self.interface_frame,
                                                             "Relabel Images",
                                                             self.relabel_images,
                                                             10,
                                                             860,
                                                             25)

        self.add_remove_subcategory_title = self.create_label(self.interface_frame,
                                                              "+/- Subcategory",
                                                              "grey20",
                                                              "white",
                                                              1010,
                                                              0)

        self.add_remove_subcategory_entry = tk.Entry(self.interface_frame,
                                                     width=20,
                                                     bg="white",
                                                     fg="black")
        self.add_remove_subcategory_entry.place(x=1010, y=23)

        self.add_subcategory_button = self.create_button(self.interface_frame,
                                                         "Add Subcategory",
                                                         self.add_subcategory,
                                                         10,
                                                         1210,
                                                         25)

        self.remove_subcategory_button = self.create_button(self.interface_frame,
                                                            "Remove Subcategory",
                                                            self.remove_subcategory,
                                                            12,
                                                            1340,
                                                            25)

        self.refresh_subcategory_options()

    def change_image_subcategory(self, instance):
        index = instance.instance_id
        old_subcategory = instance.subcategory

        if old_subcategory != self.app.relabel_subcategory:
            self.app.dataset.instance_df.loc[
                self.app.dataset.instance_df['instance_id'] == index, 'subcategory'] = self.app.relabel_subcategory
            # self.app.dataset.instance_df.loc[
            #     self.app.dataset.instance_df[
            #         'instance_id'] == index, 'last_modified'] = datetime.datetime.now().replace(microsecond=0)

            self.app.unsaved_changes_made = True
            self.app.dataset.generate_subcategory_df()
        else:
            messagebox.showerror(message="Can't change subcategory because already in subcategory")

    def set_current_video(self, selection):
        self.app.current_video = selection
        self.app.current_video_var.set(selection)
        self.app.image_preview_frame.preview_index = 0

        print("Current video changed to {}".format(self.app.current_video))

    def set_current_category(self, selection):
        self.app.current_category = selection
        self.app.current_category_var.set(selection)

        self.app.current_subcategory_list = self.app.dataset.get_subcategory_list(self.app.current_category)
        self.app.current_subcategory = self.app.current_subcategory_list[0]

        self.app.image_preview_frame.preview_index = 0

        self.refresh_subcategory_options()
        print("Current category changed to {}".format(self.app.current_category))

    def set_current_subcategory(self, selection):
        self.app.current_subcategory = selection
        self.app.current_subcategory_var.set(selection)
        self.app.image_preview_frame.preview_index = 0
        print("Current subcategory changed to {}".format(self.app.current_subcategory))

    def set_relabel_subcategory(self, selection):
        self.app.relabel_subcategory = selection
        self.app.relabel_subcategory_var.set(selection)
        print("Relabel subcategory changed to {}".format(self.app.relabel_subcategory))

    def add_subcategory(self):
        illegal_subcategory_list = ["", None]
        new_subcategory = self.add_remove_subcategory_entry.get()

        if new_subcategory in self.app.dataset.get_subcategory_list(self.app.current_category):
            tk.messagebox.showerror(f"Not adding subcategory {new_subcategory} because already in subcategory list")

        elif new_subcategory in illegal_subcategory_list:
            tk.messagebox.showerror(f"Not adding subcategory {new_subcategory} because in illegal subcategory list")

        elif bool(re.fullmatch(r'^ +$', new_subcategory)):
            tk.messagebox.showerror(f"Cannot add subcategory '{new_subcategory}' because it is only spaces")

        else:
            print("Adding subcategory", new_subcategory)
            self.app.dataset.add_subcategory(self.app.current_category, new_subcategory)
            self.refresh_subcategory_options()
            print(self.app.dataset.subcategory_df)

    def remove_subcategory(self):
        subcategory = self.add_remove_subcategory_entry.get()
        print("Removing subcategory", subcategory)
        if subcategory:
            if subcategory == "None":
                tk.messagebox.showerror("ERROR", "Cannot remove subcategory 'None'")
            else:
                filtered_rows = self.app.dataset.subcategory_df[
                    (self.app.dataset.subcategory_df['subcategory'] == subcategory) & (
                                self.app.dataset.subcategory_df[
                                    'category'] == self.app.current_category)]
                if filtered_rows.empty:
                    tk.messagebox.showerror("ERROR", "Cannot remove because it doesn't exist in that category")
                else:
                    if filtered_rows.iloc[0]['count'] == 0:
                        self.app.dataset.remove_subcategory(self.app.current_category, subcategory)
                        self.refresh_subcategory_options()
                    else:
                        tk.messagebox.showerror("ERROR", "Cannot remove subcategory with assigned instances")
        print(self.app.dataset.subcategory_df)

    def relabel_images(self):
        self.app.relabel_subcategory = self.app.relabel_subcategory_var.get()
        print(self.app.image_preview_frame.current_selections_list)

        for i in range(len(self.app.image_preview_frame.current_selections_list)):
            if self.app.image_preview_frame.current_selections_list[i]:
                current_instance = self.app.image_preview_frame.preview_image_list[i]

                if self.app.image_preview_frame.preview_subcategory != self.app.relabel_subcategory:
                    self.change_image_subcategory(current_instance)

        self.app.dataset.print_subcategory_string()
        self.app.image_preview_frame.update_preview_frame(False)
