import os

from data.packfile import Packfile


def extract_file(filename, filepath):
    with open(filepath, "rb") as file:
        packfile = Packfile(file, filename)
        packfile.extract()


def extract_directory(checkpath):
    for path, files in os.walk(checkpath):
        for name in files:
            if name.endswith(".vpp_pc"):
                filepath = os.path.join(path, name)
                extract_file(name, filepath)


# for file in os.listdir("data"):
#     print(file)
#     print(os.path.isdir(file))
