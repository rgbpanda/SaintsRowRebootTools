import os
import sys

from data.packfile import Packfile

# def patch()

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
    if len(sys.argv) == 4:
        if sys.argv[1] == "patch":
            file = sys.argv[2].replace(".\\", "")
            new = sys.argv[3].replace(".\\", "")
            with open(file, "rb") as ogfile:
                packfile = Packfile(ogfile, file)
                packfile.patch(new, ogfile)
        elif sys.argv[1] == "extract":
            extract_file(sys.argv[2], sys.argv[2], "output", False)
