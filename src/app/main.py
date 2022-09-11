import os
import sys
import json
import gzip

import app.helpers
import subprocess

from data.packfile import Packfile


def extract(input_directory, output_directory, recursive):
    output_directory = os.path.join(output_directory, "sr5")
    for path, dirs, files in os.walk(input_directory):
        for name in files:
            if name.endswith(".vpp_pc") or name.endswith(".str2_pc"):
                filepath = os.path.join(path, name)
                packfile = Packfile(filepath)
                packfile.extract(output_directory, recursive)
                packfile.close()
    print("Done! You can close this window now")


def get_base_paths(gamepath):
    base_paths = {}
    for path, dirs, files in os.walk(f"{gamepath}\\data"):
        for name in files:
            base_paths[name] = path
    return base_paths


def mod_data_exists(gamepath):
    mod_data_dir = f"{gamepath}\\mod_data"
    if not os.path.exists(mod_data_dir):
        return False

    if os.listdir(mod_data_dir) == 0:
        return False
    return True


def is_patched(gamepath):
    if os.path.basename(gamepath) != "sr5":
        print("Invalid game path location")
        return None

    if not os.path.exists(f"{gamepath}\\mod_config\\patch.json"):
        return False

    with open(f"{gamepath}\\mod_config\\patch.json", "r") as patch_json:
        patch_dict = patch_json.read()
        if patch_dict != "{}":
            return True
        else:
            return False

    return None


def open_mod_folder(gamepath):
    if os.path.basename(gamepath) != "sr5":
        print("Invalid game path location")
        return

    mod_folder = f"{gamepath}\\mod_data"
    if not os.path.exists(mod_folder):
        os.mkdir(mod_folder)
    subprocess.Popen(f"explorer {mod_folder}")


def validate_patch_files(gamepath):
    if os.path.basename(gamepath) != "sr5":
        print("Invalid game path location")
        return

    if not os.path.exists(f"{gamepath}\\mod_config"):
        os.mkdir(f"{gamepath}\\mod_config")

    if not os.path.exists(f"{gamepath}\\mod_data"):
        os.mkdir(f"{gamepath}\\mod_data")

    parent_path = f"{gamepath}\\mod_config\\parent_locations.json"
    if not os.path.exists(parent_path):
        with open("dist\\parent_locations.gz", "rb") as f:
            # TODO: Copy from dist if not here
            data = gzip.decompress(f.read())
            parent_dict = json.loads(data)
            with open(f"{gamepath}\\mod_config\\parent_locations.json", "w") as f:
                f.write(json.dumps(parent_dict, indent=4))

    try:
        patch = f"{gamepath}\\mod_config\\patch.json"
        with open(patch, "r") as patch_file:
            json.loads(patch_file.read)
    except Exception:
        with open(f"{gamepath}\\mod_config\\patch.json", "w") as f:
            f.write(json.dumps({}))


def patch(gamepath):
    validate_patch_files(gamepath)

    with open(f"{gamepath}\\mod_config\\parent_locations.json", "r") as f:
        parent_dict = json.loads(f.read())

    base_paths = get_base_paths(gamepath)
    for path, dirs, files in os.walk(f"{gamepath}\\mod_data"):
        for name in files:
            parents = parent_dict[name]
            for parent in parents:
                if parent in base_paths.keys():
                    parent_path = f"{base_paths[parent]}\\{parent}"
                    packfile = Packfile(parent_path)
                    output = packfile.patch(f"{path}\\{name}")
                    with open(f"{gamepath}\\mod_config\\patch.json", "w") as f:
                        patch_json_data = json.dumps(output, indent=4)
                        f.write(patch_json_data)
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


def unpatch(gamepath):
    validate_patch_files(gamepath)

    base_paths = get_base_paths(gamepath)
    with open(f"{gamepath}\\mod_config\\patch.json", "r") as patch_json:
        patch_json = json.loads(patch_json.read())
        for filename in patch_json.keys():
            base_path = base_paths[filename]
            packfile = Packfile(f"{base_path}\\{filename}")
            packfile.unpatch(patch_json[filename])
