import os
import sys

from data.packfile import Packfile


def extract_directory(input_directory, output_directory, recursive):
    for path, dirs, files in os.walk(input_directory):
        for name in files:
            if name.endswith(".vpp_pc") or name.endswith(".str2_pc"):
                filepath = os.path.join(path, name)
                extract_file(name, filepath, output_directory, recursive)
    print("Done! You can close this window now")


def extract_file(filename, filepath, output_directory, recursive):
    with open(filepath, "rb") as file:
        packfile = Packfile(file, filename)
        packfile.extract(output_directory, recursive)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        extract_file(sys.argv[1], sys.argv[1], "output", False)
