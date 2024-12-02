import tkinter as tk
from ..config import Config
from ..by_category_view import full_image_frame, interface_frame, image_preview_frame


class ByCategoryView:

    def __init__(self, app):
        self.app = app

        self.interface_frame = tk.Frame(app)
        self.main_frame = tk.Frame()


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

        self.app.dataset.print_subcategory_string()

        self.init_frame()
        self.create_frame()


    def init_frame(self):
        self.category_list = self.app.dataset.get_category_list()

        self.current_category = self.category_list[0]
        self.current_category_var = tk.StringVar()
        self.current_category_var.set(self.current_category)

        self.current_subcategory_list = self.app.dataset.get_subcategory_list(self.current_category)
        self.current_subcategory = self.current_subcategory_list[0]
        self.current_subcategory_var = tk.StringVar()
        self.current_subcategory_var.set(self.current_subcategory)

        self.video_list = self.app.dataset.get_video_list()
        self.current_video = self.video_list[0]
        self.current_video_var = tk.StringVar()
        self.current_video_var.set(self.video_list[0])

        self.relabel_subcategory_list = self.app.dataset.get_subcategory_list(self.current_category)
        self.relabel_subcategory = self.relabel_subcategory_list[0]
        self.relabel_subcategory_var = tk.StringVar()
        self.relabel_subcategory_var.set(self.relabel_subcategory)

    def create_frame(self):
        self.image_frame = tk.Frame(self.app.root,
                                    width=Config.main_window_dimensions[0],
                                    height=Config.main_window_dimensions[1]-Config.interface_frame_height,
                                    bg="black")

        self.full_image_frame = full_image_frame.FullImageFrame(self)
        self.image_preview_frame = image_preview_frame.ImagePreviewFrame(self)



        self.image_frame.pack(side=tk.TOP)
        self.image_preview_frame.image_preview_frame.pack(side=tk.LEFT)
        self.full_image_frame.full_image_frame.pack(side=tk.LEFT)

