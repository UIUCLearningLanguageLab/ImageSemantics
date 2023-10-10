import tkinter as tk
from tkinter import messagebox
from ImageSemantics.src.relabeler import config
from ImageSemantics.src.relabeler import interface_frame
from ImageSemantics.src.relabeler import image_preview_frame
from ImageSemantics.src.relabeler import full_image_frame


class RelabelerApp:

    def __init__(self, dataset):
        self.dataset = dataset
        self.unsaved_changes_made = False

        # main window variables
        self.root = tk.Tk()

        # menu variables
        self.main_menu = None
        self.file_menu = None

        self.interface_frame = None
        self.image_frame = None
        self.image_preview_frame = None
        self.full_image_frame = None
        self.instance_window = None

        self.category_list = None

        self.current_category = None
        self.current_category_var = None
        self.current_subcategory_list = None
        self.current_subcategory = None
        self.current_subcategory_var = None

        self.video_list = None
        self.current_video = None
        self.current_video_var = None

        self.relabel_subcategory_list = None
        self.relabel_subcategory = None
        self.relabel_subcategory_var = None

        self.dataset.print_subcategory_string()
        self.init_app()
        self.create_main_window()
        self.create_menu()

    def init_app(self):
        self.category_list = self.dataset.get_category_list()

        self.current_category = self.category_list[0]
        self.current_category_var = tk.StringVar()
        self.current_category_var.set(self.current_category)

        self.current_subcategory_list = self.dataset.get_subcategory_list(self.current_category)
        self.current_subcategory = self.current_subcategory_list[0]
        self.current_subcategory_var = tk.StringVar()
        self.current_subcategory_var.set(self.current_subcategory)

        self.video_list = self.dataset.get_video_list()
        self.current_video = self.video_list[0]
        self.current_video_var = tk.StringVar()
        self.current_video_var.set(self.video_list[0])

        self.relabel_subcategory_list = self.dataset.get_subcategory_list(self.current_category)
        self.relabel_subcategory = self.relabel_subcategory_list[0]
        self.relabel_subcategory_var = tk.StringVar()
        self.relabel_subcategory_var.set(self.relabel_subcategory)

        self.add_remove_subcategory_category = self.category_list[0]
        self.add_remove_subcategory_category_var = tk.StringVar()
        self.add_remove_subcategory_category_var.set(self.category_list[0])

    def create_main_window(self):
        self.root.configure(background='black')
        self.root.geometry("{}x{}".format(config.Config.main_window_dimensions[0],
                                          config.Config.main_window_dimensions[1]))
        self.root.title("Image Relabeler")
        self.root.protocol("WM_DELETE_WINDOW", self.quit)

        self.image_frame = tk.Frame(self.root,
                                    width=config.Config.main_window_dimensions[0],
                                    height=config.Config.main_window_dimensions[1]-config.Config.interface_frame_height,
                                    bg="black")

        self.full_image_frame = full_image_frame.FullImageFrame(self)
        self.image_preview_frame = image_preview_frame.ImagePreviewFrame(self)

        self.interface_frame = interface_frame.InterfaceFrame(self)

        self.interface_frame.interface_frame.pack(side=tk.TOP)
        self.image_frame.pack(side=tk.TOP)
        self.image_preview_frame.image_preview_frame.pack(side=tk.LEFT)
        self.full_image_frame.full_image_frame.pack(side=tk.LEFT)

    def create_menu(self):
        self.main_menu = tk.Menu(self.root)
        self.root.config(menu=self.main_menu)

        self.file_menu = tk.Menu(self.main_menu, tearoff=0)
        self.main_menu.add_cascade(label="File", menu=self.file_menu)

        self.file_menu.add_command(label="Save  ⌘S     ", command=self.save)
        self.file_menu.add_command(label="Quit  ⌘Q     ", command=self.quit)

        self.root.bind("<Command-s>", self.save)
        self.root.bind("<Command-q>", self.quit)

    def save(self):
        self.dataset.save_dataset(split_by_category=True)
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
