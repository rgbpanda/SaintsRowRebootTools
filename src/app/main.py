import os
import sys
import json
import gzip
import shutil

import subprocess

from app import helpers
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
    print("Extraction Complete!")


def mod_data_exists(gamepath):
    mod_data_dir = f"{gamepath}\\mod_data"
    if not os.path.exists(mod_data_dir):
        return False

    if os.listdir(mod_data_dir) == 0:
        return False
    return True


def is_patched(gamepath):
    if os.path.basename(gamepath) != "sr5":
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
    mod_folder = f"{gamepath}\\mod_data"
    if not os.path.exists(mod_folder):
        os.mkdir(mod_folder)
    subprocess.Popen(f"explorer {mod_folder}")


def validate_gamepath(gamepath):
    if os.path.basename(gamepath) != "sr5":
        return False
    return True


def validate_patch_files(gamepath):
    if not os.path.exists(f"{gamepath}\\mod_config"):
        os.mkdir(f"{gamepath}\\mod_config")

    if not os.path.exists(f"{gamepath}\\mod_data"):
        os.mkdir(f"{gamepath}\\mod_data")

    parent_path = f"{gamepath}\\mod_config\\parent_locations.json"
    if not os.path.exists(parent_path):
        with open("dist\\parent_locations.gz", "rb") as f:
            # TODO: Copy from dist if not here
            data = gzip.decompress(f.read())
            parents_dict = json.loads(data)
            with open(f"{gamepath}\\mod_config\\parent_locations.json", "w") as f:
                f.write(json.dumps(parents_dict, indent=4))

    try:
        patch = f"{gamepath}\\mod_config\\patch.json"
        with open(patch, "r") as patch_file:
            json.loads(patch_file.read())
    except Exception:
        with open(f"{gamepath}\\mod_config\\patch.json", "w") as f:
            f.write(json.dumps({}))
    return True


def get_base_paths(gamepath):
    base_paths = {}
    for path, dirs, files in os.walk(f"{gamepath}\\data"):
        for name in files:
            base_paths[name] = path
    return base_paths


def patch(gamepath):
    validate_patch_files(gamepath)

    with open(f"{gamepath}\\mod_config\\parent_locations.json", "r") as f:
        parents_dict = json.loads(f.read())

    with open(f"{gamepath}\\mod_config\\patch.json", "r") as r:
        patch_json = json.loads(r.read())

    base_paths = get_base_paths(gamepath)

    to_patch = {}
    print("Finding data to patch")
    for path, dirs, files in os.walk(f"{gamepath}\\mod_data"):
        for file in files:
            if file not in parents_dict:
                print("Invalid file name")
                print(f"Cannot patch {path}\\{file}")
                print("Cancelling")
                return

            for parent in parents_dict[file]:
                if parent.split(".")[-1] == "vpp_pc":
                    if parent not in to_patch.keys():
                        to_patch[parent] = {}
                    
                    if "root" not in to_patch[parent]:
                        to_patch[parent]["root"] = []

                    to_patch[parent]["root"].append(f"{path}\\{file}")

                if parent.split(".")[-1] == "str2_pc":
                    for root_vpp_pc in parents_dict[parent]:
                        if root_vpp_pc not in to_patch.keys():
                            to_patch[root_vpp_pc] = {}

                        if "sub" not in to_patch[root_vpp_pc]:
                            to_patch[root_vpp_pc]["sub"] = {}

                        if parent not in to_patch[root_vpp_pc]["sub"]:
                            to_patch[root_vpp_pc]["sub"][parent] = []
                        to_patch[root_vpp_pc]["sub"][parent].append(f"{path}\\{file}")

    for file in base_paths:
        if file in to_patch:
            packfile = Packfile(f"{base_paths[file]}\\{file}")
            patch_json = packfile.patch(patch_json, to_patch[file], gamepath)

    # temp = f"{gamepath}\\mod_config\\temp"
    # if os.path.exists(temp):
    #     shutil.rmtree(temp)

    with open(f"{gamepath}\\mod_config\\patch.json", "w") as r:
        r.write(json.dumps(patch_json, indent=4))

    print("Patch Complete!")


def unpatch(gamepath):
    validate_patch_files(gamepath)

    base_paths = get_base_paths(gamepath)
    with open(f"{gamepath}\\mod_config\\patch.json", "r") as patch_json:
        patch_json = json.loads(patch_json.read())

        files = dict.fromkeys(patch_json).keys()
        for filename in files:
            base_path = base_paths[filename]
            packfile = Packfile(f"{base_path}\\{filename}")
            patch_json = packfile.unpatch(patch_json)

        with open(f"{gamepath}\\mod_config\\patch.json", "w") as f:
            patch_json = json.dumps(patch_json, indent=4)
            f.write(patch_json)


def get_parent_data(gamepath):
    output_jsons = []
    for path, dirs, files in os.walk(gamepath):
        for name in files:
            if name.endswith(".vpp_pc"):
                filepath = os.path.join(path, name)
                packfile = Packfile(filepath)
                output_jsons += packfile.parent_data()
                packfile.close()

    output_json = helpers.combine_dicts(output_jsons)
    with open("dist/parent_locations.json", "w") as f:
        print("Writing file...")
        f.write(json.dumps(output_json, indent=4))

    print("Done!")
