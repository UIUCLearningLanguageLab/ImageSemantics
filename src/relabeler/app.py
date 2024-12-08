import tkinter as tk
from tkinter import messagebox
from .config import Config
from .by_category_view import by_category_view
from .dataframe_view import dataframe_view
from .frame_view import frame_view
from .video_view import video_view


class RelabelerApp:

    def __init__(self, dataset):
        self.dataset = dataset
        self.unsaved_changes_made = False

        # main window variables
        self.root = tk.Tk()

        self.interface_frame = None
        self.button_dimensions = (4, 2)
        self.frame_x_padding = 10
        self.interface_frame_width = self.button_dimensions[0] + self.frame_x_padding


        self.main_frame = None
        self.main_frame_dimensions = (Config.main_window_dimensions[0],
                                      Config.main_window_dimensions[1]-self.interface_frame_width)

        self.content_frame_dict = None
        self.current_content_frame = None

        # menu variables
        self.main_menu = None
        self.file_menu = None

        self.create_menu()
        self.create_main_window()
        self.create_interface_frame()
        self.create_main_frame()
        self.create_content_frames()
        self.create_interface_buttons()

        self.show_content_frame("F")

    def create_interface_frame(self):
        self.interface_frame = tk.Frame(self.root, width=self.interface_frame_width, bg="gray")
        self.interface_frame.pack(side=tk.LEFT, fill=tk.Y)

    def create_main_window(self):
        self.root.configure(background='black')
        self.root.geometry("{}x{}".format(Config.main_window_dimensions[0],
                                          Config.main_window_dimensions[1]))
        self.root.title("Image Annotator")
        self.root.protocol("WM_DELETE_WINDOW", self.quit)

    def create_main_frame(self):
        self.main_frame = tk.Frame(self.root, bg="black", bd=5, relief=tk.RIDGE)
        self.main_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)


    def create_content_frames(self):
        self.content_frame_dict = {"F": frame_view.FrameView(self),
                                   "C": by_category_view.ByCategoryView(self),
                                   "V": video_view.VideoView(self),
                                   "D": dataframe_view.DataFrameView(self)}

    def create_interface_buttons(self):
        for key, value in self.content_frame_dict.items():
            label_button = tk.Label(
                self.interface_frame,
                text=key,
                bg=value.color,
                fg="black",
                height=self.button_dimensions[1],
                width=self.button_dimensions[0],
                relief="raised"
            )
            label_button.pack(pady=10)
            label_button.bind("<Button-1>", lambda event, frame=key: self.show_content_frame(frame))

    def show_content_frame(self, frame_name):
        print(f"Showing Frame {frame_name}")
        # Hide the current frame
        if self.current_content_frame:
            self.current_content_frame.frame.pack_forget()

        # Show the new frame
        self.current_content_frame = self.content_frame_dict[frame_name]
        self.current_content_frame.frame.pack(expand=True, fill="both")

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
