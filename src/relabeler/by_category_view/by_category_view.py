import tkinter as tk
from .interface_frame import InterfaceFrame
from .image_preview_frame import ImagePreviewFrame
from.full_image_frame import FullImageFrame

class ByCategoryView:

    def __init__(self, app):
        self.app = app
        self.color = "blue"
        self.frame = tk.Frame(self.app.main_frame, bg=self.color) # this is the frame everything else goes in

        self.interface_frame = None  # this is the menu frame at the top
        self.interface_height = 40
        self.main_frame = None  #  this is the content frame under the interface frame, holds image and image_preview frames

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

        self.relabel_category_list = None
        self.relabel_category = None
        self.relabel_category_var = None
        self.relabel_subcategory_list = None
        self.relabel_subcategory = None
        self.relabel_subcategory_var = None

        self.init_frame()
        self.create_main_frame()
        self.create_interface_frame()

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

    def create_main_frame(self):
        self.main_frame = tk.Frame(self.frame,
                                    width=self.app.main_frame_dimensions[0],
                                    height=self.app.main_window_dimensions[1] - Config.interface_frame_height,
                                    bg="black")
        self.main_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.image_preview_frame = ImagePreviewFrame(self.app, self)

        self.full_image_frame = FullImageFrame(self.app, self)
        self.full_image_frame.full_image_frame.pack()

    def create_interface_frame(self):
        self.interface_frame = InterfaceFrame(self.app, self)



    #
    #
    #     self.image_frame = tk.Frame(self.app.root,
    #                                 width=Config.main_window_dimensions[0],
    #                                 height=Config.main_window_dimensions[1]-Config.interface_frame_height,
    #                                 bg="black")
    #
    #     self.full_image_frame = full_image_frame.FullImageFrame(self)
    #     self.image_preview_frame = image_preview_frame.ImagePreviewFrame(self)
    #
    #
    #
    #     self.image_frame.pack(side=tk.TOP)
    #     self.image_preview_frame.image_preview_frame.pack(side=tk.LEFT)
    #     self.full_image_frame.full_image_frame.pack(side=tk.LEFT)
    #
