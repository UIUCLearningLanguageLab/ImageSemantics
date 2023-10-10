from ImageSemantics.src.relabeler import config
import tkinter as tk


class InstanceWindow:

    def __init__(self, app, image):
        self.app = app
        self.image = image
        self.image_display_dimensions = (config.Config.comment_image_dimensions[0],
                                         config.Config.comment_image_dimensions[1])

        self.comment_window = None
        self.raw_tk_image = None

        self.recolored_tk_image = None

        self.img_label = None

        self.comment_type_var = None
        self.comment_type_option_menu = None
        self.name_entry = None
        self.submit_btn = None
        self.comment_text_widget = None

        self.alternate_image_event_id = None

        self.create_window()
        self.display_image()
        self.create_interface()

    def create_window(self):
        # Create a new Toplevel window
        self.comment_window = tk.Toplevel(self.app.root)  # Assuming self.root is your main window
        self.comment_window.title("Add Instance Comment")
        h = self.image_display_dimensions[1] + 200
        dimensions = f"{self.image_display_dimensions[0]}x{h}+100+100"
        self.comment_window.geometry(dimensions)
        self.comment_window.protocol("WM_DELETE_WINDOW", self.close_window)

    def display_image(self):
        # Display the image
        raw_pil_image = self.image.raw_pil_image
        resized_pil_image = self.image.resize_image(raw_pil_image, self.image_display_dimensions)
        self.raw_tk_image = self.image.create_tk_image(resized_pil_image)

        recolored_instance_pil_image = self.image.get_recolored_image()
        recolored_resized_pil_image = self.image.resize_image(recolored_instance_pil_image,
                                                              self.image_display_dimensions)
        self.recolored_tk_image = self.image.create_tk_image(recolored_resized_pil_image)

        self.img_label = tk.Label(self.comment_window, image=self.raw_tk_image)
        self.img_label.image = self.raw_tk_image  # Keep a reference to avoid garbage collection
        self.img_label.place(x=0, y=0)
        self.alternate_image()

    def alternate_image(self):
        # Get the current image of the label
        current_image = self.img_label.cget("image")

        # Alternate the image
        if current_image == str(self.raw_tk_image):
            self.img_label.config(image=self.recolored_tk_image)
        else:
            self.img_label.config(image=self.raw_tk_image)

        # Schedule the function to run again after 1000ms (1 second)
        self.alternate_image_event_id = self.app.root.after(500, self.alternate_image)

    def create_interface(self):
        # OptionMenu for error type
        comment_type_label = tk.Label(self.comment_window, text="Comment Type", bg="grey20", fg="white")
        comment_type_label.place(x=320, y=self.image_display_dimensions[1] + 20)
        self.comment_type_var = tk.StringVar()
        option_list = ["Subcategory Question/Comment", "Segment Error", "Category Error", "Other"]
        self.comment_type_var.set(option_list[0])  # default value
        self.comment_type_option_menu = tk.OptionMenu(self.comment_window, self.comment_type_var, *option_list)
        self.comment_type_option_menu.config(width=50)
        self.comment_type_option_menu.place(x=420, y=self.image_display_dimensions[1] + 20)

        name_label = tk.Label(self.comment_window, text="Name", bg="grey20", fg="white")
        name_label.place(x=10, y=self.image_display_dimensions[1] + 20)
        self.name_entry = tk.Entry(self.comment_window, bg="white", fg="black")
        self.name_entry.place(x=50, y=self.image_display_dimensions[1] + 20)

        # Text entry field with label
        self.comment_text_widget = tk.Text(self.comment_window, width=180, height=6, bg="white", fg="black")
        self.comment_text_widget.place(x=10, y=self.image_display_dimensions[1] + 60)

        # # Submit button
        self.submit_btn = tk.Button(self.comment_window, text="Submit", command=self.add_instance_comment)
        self.submit_btn.place(x=950, y=self.image_display_dimensions[1] + 20)
        self.comment_window.bind("<Return>", lambda event=None: self.add_instance_comment())

    def add_instance_comment(self):
        comment = self.comment_text_widget.get("1.0", tk.END).replace("\n", "")
        comment_type = self.comment_type_var.get()
        name = self.name_entry.get()

        category = self.image.category
        new_comment = [name, comment_type, comment,
                       self.image.participant, self.image.video, self.image.frame, self.image.dt,
                       self.image.instance_id, self.image.category, self.image.subcategory]

        self.app.dataset.instance_comment_dict[category].append(new_comment)
        self.app.unsaved_changes_made = True
        self.close_window()

    def close_window(self):
        if self.alternate_image_event_id is not None:
            self.app.root.after_cancel(self.alternate_image_event_id)
        self.comment_window.destroy()
