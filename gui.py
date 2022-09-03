import os

from tkinter import ttk, Tk, END, StringVar
from tkinter import filedialog as fd


# create the root window
root = Tk()
root.title("SR Reboot Extraction Tool")
root.resizable(False, False)

content = ttk.Frame(root)
frame = ttk.Frame(content, borderwidth=5, relief="ridge")
namelbl = ttk.Label(content, text="Name")
name = ttk.Entry(content)


def extract_all():
    pass


def select_dir():
    pass


def select_file():

    directory = fd.askdirectory(title="Open a file", initialdir=initial_dir)
    print(directory)
    # filetypes = (("vpp_pc", "*.vpp_pc"), ("All files", "*.*"))


#
#     # text_box.
#     text_box.insert(filename)


# def select_output():
#     output_directory =

#     # tools.extract(filename, output_directory)


input_button = ttk.Button(content, text="Select Data Directory", command=select_file)
input_button.config(width=20)
input_box_value = StringVar()
input_box = ttk.Entry(content, textvariable=input_box_value)
input_box.config(width=100)

output_button = ttk.Button(content, text="Select Output Directory", command=select_dir)
output_button.config(width=20)
output_box_value = StringVar()
output_box = ttk.Entry(content, textvariable=output_box_value)
output_box.config(width=100)

root_dir = os.path.abspath(os.sep)
path = os.path.join(root_dir, "Program Files\\Epic Games\\SaintsRow\\sr5\\data")
if os.path.exists(path):
    input_box.delete(0, END)
    input_box.insert(0, path)

    output_path = os.path.join(path, "..\\", "extracted")
    output_box.delete(0, END)
    output_box.insert(0, output_path)
else:
    initial_dir = root_dir


extract_button = ttk.Button(content, text="Extract All", command=extract_all)

content.grid(column=0, row=0)
input_box.grid(column=0, row=1, columnspan=3, padx=(20, 5), pady=(20, 0))
input_button.grid(column=2, row=1, padx=(0, 20), pady=(20, 0))
output_box.grid(column=0, row=2, columnspan=3, padx=(20, 5), pady=(20, 20))
output_button.grid(column=2, row=2, padx=(10, 20), pady=(20, 20))
extract_button.grid(column=1, row=3, padx=(10, 20), pady=(20, 20))

# run the application
root.mainloop()
