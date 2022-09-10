import mmap
import os
import lz4.frame
import io
from lz4.frame import BLOCKSIZE_MAX256KB, LZ4FrameCompressor
from helpers import tools
from tqdm import tqdm

from data import file


# Atrributes:
#
# name       - the packfile name
# path       - location of packfile on disk (None if subpack?)
# subpack    - whether pack is inside another pack
#
# data_o    - value of data offset
# names_o   - value of the filenames offset
#
# num_files - number of files
# num_paths - number of paths
# size      - size of file
# csize     - compressed size of file
#
class Packfile:
    NAMES_OL = 24
    DATA_OL = 64

    NUM_FILES_O = 16
    NUM_PATHS_O  = 20
    SIZE_O = 40
    CSIZE_O = 48
    HEADER_O = 120

    def __init__(self, packfile_path, subpack=False):
        self.stream = open(packfile_path, 'rb')

        self.name = os.path.basename(os.path.normpath(packfile_path))
        self.path = os.path.normpath(os.path.join(packfile_path, "..\\"))

        self.subpack = subpack
        self.validate()

        stream = self.stream
        self.num_files = tools.read(stream, Packfile.NUM_FILES_O, 4, reverse=True)
        self.num_paths = tools.read(stream, Packfile.NUM_PATHS_O, 4, reverse=True)
        self.size = tools.read(stream, Packfile.SIZE_O, 4, reverse=True)
        self.csize = tools.read(stream, Packfile.CSIZE_O, 4, reverse=True)

        self.data_o = tools.read(stream, Packfile.DATA_OL, 4, reverse=True)
        self.names_o = tools.read(stream, Packfile.NAMES_OL, 4, reverse=True)

        self.files = []
        for f in range(0, self.num_files):
            start = (f * 48) + Packfile.HEADER_O
            self.files.append(file.File(self, start))

        stream.close()

    def validate(self):
        descriptor = tools.read(self.stream, 0, 4)
        if hex(descriptor) != "0xce0a8951":
            print("Invalid file type")
            quit()

        version = tools.read(self.stream, 4, 4)
        if hex(version) != "0x11000000":
            print("Invalid file version")
            quit()


    # def patch(self, new, patch_path, json_path):
    #     with open(new, 'rb') as new:
    #         new_data = new.read()

    #     mappings = self.filename_mappings(self.stream)
    #     self.stream.seek(self.header_offset, 0)

    #     for file in range(0, self.num_files):
    #         name, data, compressed_size, update_start = self.get_file_data(self.stream, mappings, new_data)
    #         filename = os.path.basename(os.path.normpath(new.name))
    #         if name == filename:
    #             self.update_patch_json(name, )
    #             self.write_patch_data(name, self.stream, data, new_data, patch_path, compressed_size, update_start)
    #             break

            # name, data, compressed_size, update_start = self.get_file_data(self.stream, mappings, new_data)
            # filename = os.path.basename(os.path.normpath(new.name))
            # if name == filename:
            #     self.update_patch_json(name, )
            #     self.write_patch_data(name, self.stream, data, new_data, patch_path, compressed_size, update_start)
            #     break
    # def get_file_data(self, mappings, new_data):

    def write_patch_data(self, name, data, new_data, patch_path, compressed_size, update_start):
        print(f"Patching {name}")
        self.stream.seek(0, io.SEEK_END)
        new_location = self.stream.tell()
        if new_location < 0:
            new_location = new_location + 8196

        new_location_bytes = int.to_bytes(new_location - self.data_offset, 8, 'little')
        new_size = int.to_bytes(len(new_data), 8, 'little')
        flag = int.to_bytes(256, 4, 'big')

        with open(patch_path, 'r+b') as file:
            print(f"Patching {self.packfile_name}")
            print("Writing header data")
            file.seek(update_start)
            file.write(new_location_bytes)
            file.write(new_size)
            file.write(int.to_bytes(compressed_size, 8, 'little'))
            file.write(flag)
            print("Writing new file data")
            file.seek(new_location)
            file.write(data)
            print("done!")

    def extract(self, output_directory, recursive):
        mm = mmap.mmap(self.stream.fileno(), 0, access=mmap.ACCESS_READ)
        self.stream.seek(self.header_offset, 0)

        t = tqdm(
            range(0, self.num_files),
            leave=(not self.subpack),
        )
        for file in t:
            name_offset = int.from_bytes(self.stream.read(8), "little")
            name_offset += self.filenames_offset
            name = self.mappings[name_offset]
            name = name.decode("ascii")

            path_offset = int.from_bytes(self.stream.read(8), "little")
            path_offset += self.filenames_offset

            path = self.mappings[path_offset]
            path = path.decode("ascii")

            file_data_offset = int.from_bytes(self.stream.read(8), "little")
            file_data_offset += self.data_offset

            size = int.from_bytes(self.stream.read(8), "little")
            compressed_size = int.from_bytes(self.stream.read(8), "little")
            self.stream.read(8)

            t.set_description(f"Extracting: {self.packfile_name}", refresh=True)
            self.write_file(
                name,
                path,
                size,
                compressed_size,
                file_data_offset,
                mm,
                output_directory,
                recursive,
            )

    def write_file(self, name, path, size, compressed_size, offset, mm, output_directory, recursive=True):
        path = f"{output_directory}\\{path}"
        if not os.path.exists(path):
            os.makedirs(path)

        mm.seek(offset)
        output_file = f"{path}\\{name}"

        if compressed_size != int("0xffffffffffffffff", 16):
            file = mm.read(compressed_size)
            file = lz4.frame.decompress(bytearray(file))
            file = bytes(file)
        else:
            file = mm.read(size)

        with open(output_file, "wb") as f:
            f.write(file)

        is_packfile = output_file.endswith(".vpp_pc") or output_file.endswith(
            ".str2_pc"
        )
        if is_packfile and recursive:
            extract_subfile(output_file, self.packfile_name, output_directory)

    def close(self):
        self.stream.close()

def extract_subfile(filename, root_packfile, output_directory):
    with open(filename, "rb") as f:
        packfile = Packfile(f, root_packfile, subpack=True)
        packfile.extract(output_directory, recursive=True)
    os.remove(filename)
