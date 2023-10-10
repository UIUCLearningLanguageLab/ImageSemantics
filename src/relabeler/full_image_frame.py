from ImageSemantics.src.relabeler import config
import tkinter as tk


class FullImageFrame:

    def __init__(self, app):
        self.app = app
        self.dimensions = None

        self.full_image_frame = None
        self.image_display_dimensions = None

        self.image_name_label = None
        self.top_image_frame = None
        self.top_image_label = None
        self.bottom_image_frame = None
        self.bottom_image_label = None

        self.create_full_image_frame()
        self.create_full_image_labels()

    def create_full_image_frame(self):
        full_image_dimensions = config.Config.image_dimensions
        non_image_height = config.Config.interface_frame_height + 10
        image_display_height = int((config.Config.main_window_dimensions[1] - non_image_height)/2)
        image_display_ratio = image_display_height / full_image_dimensions[1]
        image_display_width = int(full_image_dimensions[0]*image_display_ratio)
        self.image_display_dimensions = (image_display_width, image_display_height)
        self.dimensions = (image_display_width+20, image_display_height*2+non_image_height)

        self.full_image_frame = tk.Frame(self.app.image_frame,
                                         width=self.dimensions[0],
                                         height=self.dimensions[1],
                                         bg="black")

    def create_full_image_labels(self):
        image_start_y = 30
        image_start_x = 10

        self.image_name_label = tk.Label(self.full_image_frame, text="", bg="black", fg="white", font="Helvetica 20")
        self.image_name_label.place(x=image_start_x, y=0)

        self.top_image_frame = tk.Frame(self.full_image_frame,
                                        height=self.image_display_dimensions[1],
                                        width=self.image_display_dimensions[0],
                                        bg="gray22", borderwidth=0, padx=0, pady=0)

        self.bottom_image_frame = tk.Frame(self.full_image_frame,
                                           height=self.image_display_dimensions[1],
                                           width=self.image_display_dimensions[0],
                                           bg="gray22", borderwidth=0, padx=0, pady=0)

        self.top_image_frame.place(x=image_start_x, y=image_start_y)
        self.bottom_image_frame.place(x=image_start_x,
                                      y=image_start_y+self.image_display_dimensions[1]+10)

        self.top_image_frame.pack_propagate(False)
        self.bottom_image_frame.pack_propagate(False)

        self.top_image_label = tk.Label(self.top_image_frame, bg="gray22", name="top_image_label",
                                        height=self.image_display_dimensions[1],
                                        width=self.image_display_dimensions[0])
        self.top_image_label.pack(side=tk.LEFT, anchor=tk.NW)

        self.bottom_image_label = tk.Label(self.bottom_image_frame, bg="gray22", name="bottom_image_label",
                                           height=self.image_display_dimensions[1],
                                           width=self.image_display_dimensions[0])
        self.bottom_image_label.pack(side=tk.LEFT, anchor=tk.NW)

    def show_images(self, current_instance_image):
        big_raw_pil_image = current_instance_image.resize_image(current_instance_image.raw_pil_image,
                                                                self.image_display_dimensions)
        big_raw_tk_image = current_instance_image.create_tk_image(big_raw_pil_image)

        recolored_instance_pil_image = current_instance_image.get_recolored_image()
        recolored_resized_pil_image = current_instance_image.resize_image(recolored_instance_pil_image,
                                                                          self.image_display_dimensions)
        recolored_tk_image = current_instance_image.create_tk_image(recolored_resized_pil_image)

        p = current_instance_image.participant
        v = current_instance_image.video
        f = current_instance_image.frame
        i = current_instance_image.instance_id
        image_name = f"{p}-{v}-{f}-{i}"
        self.image_name_label.configure(text=image_name)

        self.top_image_label.configure(image=big_raw_tk_image)
        self.top_image_label.image = big_raw_tk_image

        self.bottom_image_label.configure(image=recolored_tk_image)
        self.bottom_image_label.image = recolored_tk_image

    def hide_images(self):
        self.top_image_label.configure(image="")
        self.top_image_label.image = ""
        self.bottom_image_label.configure(image="")
        self.bottom_image_label.image = ""
        self.image_name_label.configure(text="")