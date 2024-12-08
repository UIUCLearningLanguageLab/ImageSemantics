import tkinter as tk

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