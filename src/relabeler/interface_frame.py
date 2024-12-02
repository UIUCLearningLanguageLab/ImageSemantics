import tkinter as tk
from .config import Config
from by_category_view import by_category_view
from dataframe_view import dataframe_view
from frame_view import frame_view
from video_view import video_view

class InterfaceFrame:

    def __init__(self, app):
        self.app = app
        self.button_size = 20
        self.frame_x_padding = 10
        self.dimensions = (self.button_size+self.frame_x_padding, Config.main_window_dimensions[1])

        self.interface_frame = None

    def create_interface_frame(self):
        self.interface_frame = tk.Frame(self.app.root,
                                        width=self.dimensions[0],
                                        height=self.dimensions[1],
                                        bg="grey20",
                                        bd=5, relief=tk.RIDGE)

        # create a button