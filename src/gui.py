import os
import srrutil

from tkinter import ttk, messagebox
from tkinter import StringVar, IntVar
from tkinter import Tk, END

from tkinter import filedialog as fd

root = Tk()
root.title("SR Reboot Extraction Tool")
root.resizable(False, False)

content = ttk.Frame(root)
frame = ttk.Frame(content, borderwidth=5, relief="ridge")
namelbl = ttk.Label(content, text="Name")
name = ttk.Entry(content)
root_dir = os.path.abspath(os.sep)

input_box_value = StringVar()
output_box_value = StringVar()
recursive_enabled = IntVar()


def extract_all():
    input_directory = input_box_value.get()
    output_directory = output_box_value.get()
    if messagebox.askyesno(
        "Extract Files?",
        "Are you sure you would like to extract all files from the selected directory? (This may take a while)",
    ):
        print(recursive_enabled.get())
        srrutil.extract_directory(
            input_directory, output_directory, recursive_enabled.get()
        )


def select_input_dir():
    initial_dir = root_dir
    if input_box_value.get() != "":
        initial_dir = os.path.normpath(os.path.join(input_box_value.get(), "../"))
    directory = fd.askdirectory(title="Select input directory", initialdir=initial_dir)

    if directory != "":
        # update input box with selected location
        directory = os.path.normpath(directory)
        input_box.delete(0, END)
        input_box.insert(0, directory)

        directory = os.path.normpath(os.path.join(directory, "./extracted"))
        output_box.delete(0, END)
        output_box.insert(0, directory)


def select_output_dir():
    initial_dir = root_dir
    if output_box_value.get() != "":
        initial_dir = os.path.normpath(os.path.join(output_box_value.get(), "../"))
    directory = fd.askdirectory(title="Select output directory", initialdir=initial_dir)
    if directory != "":
        directory = os.path.normpath(directory)
        output_box.delete(0, END)
        output_box.insert(0, directory)


input_button = ttk.Button(
    content, text="Select Input Directory", command=select_input_dir
)
input_button.config(width=22)

input_box = ttk.Entry(content, textvariable=input_box_value)
input_box.config(width=60)

output_button = ttk.Button(
    content, text="Select Output Directory", command=select_output_dir
)
output_button.config(width=22)
output_box = ttk.Entry(content, textvariable=output_box_value)
output_box.config(width=60)

path = os.path.join(root_dir, "Program Files\\Epic Games\\SaintsRow\\sr5\\data")
if os.path.exists(path):
    input_box.delete(0, END)
    input_box.insert(0, path)

    output_path = os.path.normpath(os.path.join(path, "extracted"))
    output_box.delete(0, END)
    output_box.insert(0, output_path)

extract_button = ttk.Button(content, text="Extract All", command=extract_all)

recursive_box = ttk.Checkbutton(
    content,
    text="Enable Recursive",
    variable=recursive_enabled,
    onvalue=1,
    offvalue=0,
)
recursive_box.state(["!alternate"])
recursive_box.state(["selected"])

content.grid(column=0, row=0)
input_box.grid(column=0, row=1, columnspan=3, padx=(20, 20), pady=(20, 0))
input_button.grid(column=3, row=1, padx=(0, 20), pady=(20, 0))
output_box.grid(column=0, row=2, columnspan=3, padx=(20, 20), pady=(20, 20))
output_button.grid(column=3, row=2, padx=(0, 20), pady=(20, 20))
recursive_box.grid(column=0, row=3, padx=(0, 0))
extract_button.grid(column=1, columnspan=2, row=3, padx=(0, 20), pady=(20, 20))

# run the application
root.mainloop()