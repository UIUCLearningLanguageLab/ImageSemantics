import tkinter as tk
from tkinter import messagebox
from ImageSemantics.src.relabeler import config
from ImageSemantics.src.relabeler.by_category_view import full_image_frame, interface_frame, image_preview_frame


class RelabelerApp:

    def __init__(self, dataset):
        self.dataset = dataset
        self.unsaved_changes_made = False

        # main window variables
        self.root = tk.Tk()

        self.interface_frame = None
        self.button_size = 20
        self.frame_x_padding = 10

        self.main_frame = None
        self.main_frame_dimensions = (config.Config.main_window_dimensions[0],
                                      config.Config.main_window_dimensions[1]-config.Config.interface_frame_height)

        # menu variables
        self.main_menu = None
        self.file_menu = None

        self.create_menu()
        self.create_main_window()
        self.create_interface_frame()
        self.create_main_frame()

    def create_interface_frame(self):
        self.interface_frame = tk.Frame(self.root, width=self.button_size+self.frame_x_padding, bg="gray")
        self.interface_frame.pack(side=tk.LEFT, fill=tk.Y)

    def create_main_window(self):
        self.root.configure(background='black')
        self.root.geometry("{}x{}".format(config.Config.main_window_dimensions[0],
                                          config.Config.main_window_dimensions[1]))
        self.root.title("Image Relabeler")
        self.root.protocol("WM_DELETE_WINDOW", self.quit)

    def create_main_frame(self):

        self.main_frame = tk.Frame(self.root,
                                   width=self.main_frame_dimensions[0],
                                   height=self.main_frame_dimensions[1],
                                   bg="blue",
                                   bd=5, relief=tk.RIDGE)
        self.main_frame.pack(side=tk.LEFT)

    def create_menu(self):
        self.main_menu = tk.Menu(self.root)
        self.root.config(menu=self.main_menu)

        self.file_menu = tk.Menu(self.main_menu, tearoff=0)
        self.main_menu.add_cascade(label="File", menu=self.file_menu)

        self.file_menu.add_command(label="Save  ⌘S     ", command=self.save)
        self.file_menu.add_command(label="Quit  ⌘Q     ", command=self.quit)

        self.root.bind("<Command-s>", self.save)
        self.root.bind("<Command-q>", self.quit)

        self.root.bind("<Control-s>", self.save)
        self.root.bind("<Control-q>", self.quit)

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
