import os
import srrutil

from tkinter import ttk, Tk, END, StringVar, messagebox
from tkinter import filedialog as fd


# create the root window
root = Tk()
root.title("SR Reboot Extraction Tool")
root.resizable(False, False)

content = ttk.Frame(root)
frame = ttk.Frame(content, borderwidth=5, relief="ridge")
namelbl = ttk.Label(content, text="Name")
name = ttk.Entry(content)

root_dir = os.path.abspath(os.sep)


def extract_all():
    input_directory = input_box_value.get()
    output_directory = output_box_value.get()
    if messagebox.askyesno("Extract Files?"):
        srrutil.extract_directory(input_directory, output_directory)


def select_input_dir():
    directory = fd.askdirectory(title="Select input directory", initialdir=root_dir)
    directory = os.path.normpath(directory)
    input_box.delete(0, END)
    input_box.insert(0, directory)
    if output_box_value.get() == "":
        directory = os.path.normpath(os.path.join(directory, "../extracted"))
        output_box.delete(0, END)
        output_box.insert(0, directory)


def select_output_dir():
    directory = fd.askdirectory(title="Select output directory", initialdir=root_dir)
    directory = os.path.normpath(directory)
    output_box.delete(0, END)
    output_box.insert(0, directory)


input_button = ttk.Button(
    content, text="Select Input Directory", command=select_input_dir
)
input_button.config(width=22)
input_box_value = StringVar()
input_box = ttk.Entry(content, textvariable=input_box_value)
input_box.config(width=60)

output_button = ttk.Button(
    content, text="Select Output Directory", command=select_output_dir
)
output_button.config(width=22)
output_box_value = StringVar()
output_box = ttk.Entry(content, textvariable=output_box_value)
output_box.config(width=60)

path = os.path.join(root_dir, "Program Files\\Epic Games\\SaintsRow\\sr5\\data")
if os.path.exists(path):
    input_box.delete(0, END)
    input_box.insert(0, path)

    output_path = os.path.normpath(os.path.join(path, "..\\", "extracted"))
    output_box.delete(0, END)
    output_box.insert(0, output_path)

extract_button = ttk.Button(content, text="Extract All", command=extract_all)

content.grid(column=0, row=0)
input_box.grid(column=0, row=1, columnspan=3, padx=(20, 20), pady=(20, 0))
input_button.grid(column=3, row=1, padx=(0, 20), pady=(20, 0))
output_box.grid(column=0, row=2, columnspan=3, padx=(20, 20), pady=(20, 20))
output_button.grid(column=3, row=2, padx=(0, 20), pady=(20, 20))
extract_button.grid(column=1, columnspan=2, row=3, padx=(10, 20), pady=(20, 20))

# run the application
root.mainloop()
