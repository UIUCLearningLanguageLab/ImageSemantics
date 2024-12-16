import tkinter as tk

class FrameView:

    def __init__(self, app):
        self.app = app
        self.color = "red"

        self.frame = tk.Frame(self.app.main_frame, bg=self.color)

        # Example content to verify the frame is displaying correctly
        label = tk.Label(self.frame, text="This is Frame F", bg=self.color, fg="white")
        label.pack(expand=True, fill="both")