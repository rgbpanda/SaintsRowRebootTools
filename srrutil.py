import os

from data.packfile import Packfile


def extract_directory(input_directory, output_directory):
    for path, dirs, files in os.walk(input_directory):
        for name in files:
            if name.endswith(".vpp_pc"):
                filepath = os.path.join(path, name)
                extract_file(name, filepath, output_directory)


def extract_file(filename, filepath, output_directory):
    print(filepath)
    with open(filepath, "rb") as file:
        packfile = Packfile(file, filename)
        packfile.extract(output_directory)


# for file in os.listdir("data"):
#     print(file)
#     print(os.path.isdir(file))
