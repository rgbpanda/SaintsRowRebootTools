import os
import sys
import json
import gzip

import app.helpers

from data.packfile import Packfile


def extract_directory(input_directory, output_directory, recursive):
    for path, dirs, files in os.walk(input_directory):
        for name in files:
            if name.endswith(".vpp_pc") or name.endswith(".str2_pc"):
                filepath = os.path.join(path, name)
                extract_file(name, filepath, output_directory, recursive)
    print("Done! You can close this window now")


def extract_file(filename, filepath, output_directory, recursive):
    packfile = Packfile(filepath)
    packfile.extract(output_directory, recursive)


def patch(gamepath):
    try:
        with open(f"{gamepath}\\mod_config\\parent_locations.json", "r") as f:
            parent_dict = json.loads(f.read())
    except FileNotFoundError:
        with open(f"{gamepath}\\mod_config\\parent_locations.patch", "rb") as f:
            data = gzip.decompress(f.read())
            parent_dict = json.loads(data)
            with open(f"{gamepath}\\mod_config\\parent_locations.json", "w") as f:
                f.write(json.dumps(parent_dict, indent=4))

    base_paths = {}
    for path, dirs, files in os.walk(f"{gamepath}\\data"):
        for name in files:
            base_paths[name] = path

    for path, dirs, files in os.walk(f"{gamepath}\\mod_data"):
        for name in files:
            parents = parent_dict[name]
            for parent in parents:
                if parent in base_paths.keys():
                    parent_path = f"{base_paths[parent]}\\{parent}"
                    with open(parent_path, "rb") as parent_file:
                        packfile = Packfile(parent_file, parent)
                        packfile.patch(f"{gamepath}\\mod_data\\{name}", parent_file, parent_path, json_path)
                else:
                    pass
                    #     extract file from parent
                # packfile = Packfile(file, filename)
                # packfile.extract(output_directory, recursive)
            # if name.endswith(".vpp_pc") or name.endswith(".str2_pc"):
            #     filepath = os.path.join(path, name)
            #     # (name, filepath, output_directory, recursive)   

    # with open(f"{gamepath}\\mod_config\\parents2.json", "r+b") as f2:
    #     f2.write(string)
        # string = tools.compressFileToString(f.read())
        # file = json.loads(f.read())





if __name__ == "__main__":
    dir = "C:\\Users\\randy\\Desktop\\Newfolder"
    extract_directory(dir, f"{dir}\\eee", True)
    # if len(sys.argv) == 2:
    #     extract_file(sys.argv[1], sys.argv[1], "output", False)
