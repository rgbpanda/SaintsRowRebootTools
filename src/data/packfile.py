import mmap
import os
import io
import lz4.frame

from lz4.frame import BLOCKSIZE_MAX256KB, LZ4FrameCompressor
from tqdm import tqdm

from app import helpers
from data.entry import Entry


# Atrributes:
#
# name       - the packfile name
# path       - location of packfile on disk
# subpack    - whether or not is subpack
# 
# data_o    - value of data offset
# names_o   - value of the filenames offset
#
# num_files - number of files
# num_paths - number of paths
# size      - size of file
# csize     - compressed size of file
# end       - end offset of the file
#
# entries      - list of file entries
# entries_dict - same as entries but hashed by name
class Packfile:
    NAMES_OL = 24
    DATA_OL = 64

    NUM_FILES_O = 16
    NUM_PATHS_O  = 20
    SIZE_O = 40
    CSIZE_O = 48
    HEADER_O = 120

    # needs either packfile_path
    # or subpack_stream and subpack_name
    def __init__(self, packfile_path=None, subpack_stream=None, subpack_name=None):
        self.subpack = subpack_stream is not None
        if self.subpack:
            self.stream = subpack_stream
            self.name = subpack_name
        else:
            self.stream = open(packfile_path, 'rb')
            self.packfile_path = packfile_path
            self.name = os.path.basename(os.path.normpath(packfile_path))
            self.path = os.path.normpath(os.path.join(packfile_path, "..\\"))

        self.validate()

        stream = self.stream
        self.num_files = helpers.read(stream, Packfile.NUM_FILES_O, 4, reverse=True)
        self.num_paths = helpers.read(stream, Packfile.NUM_PATHS_O, 4, reverse=True)
        self.size = helpers.read(stream, Packfile.SIZE_O, 4, reverse=True)
        self.csize = helpers.read(stream, Packfile.CSIZE_O, 4, reverse=True)

        self.data_o = helpers.read(stream, Packfile.DATA_OL, 4, reverse=True)
        self.names_o = helpers.read(stream, Packfile.NAMES_OL, 4, reverse=True)

        self.entries = []
        self.entries_dict = {}
        for f in range(0, self.num_files):
            start = (f * 48) + Packfile.HEADER_O
            entry = Entry(self, start)
            self.entries.append(entry)
            self.entries_dict[entry.name] = entry

        stream.seek(0, os.SEEK_END)
        self.end = stream.tell()

    def validate(self):
        descriptor = helpers.read(self.stream, 0, 4)
        if hex(descriptor) != "0xce0a8951":
            print("Invalid file type")
            quit()

        version = helpers.read(self.stream, 4, 4)
        if hex(version) != "0x11000000":
            print("Invalid file version")
            quit()

    def extract(self, output_directory, recursive):
        entries_bar = tqdm(self.entries, leave=(not self.subpack))
        for file_entry in entries_bar:
            file_entry.extract(output_directory, recursive)
            entries_bar.set_description(f"Extracting: {self.name}", refresh=True)

    def patch(self, patchfile):
        patchfile_name = os.path.basename(os.path.normpath(patchfile))
        patchfile_path = os.path.normpath(os.path.join(patchfile, "..\\"))

        file = self.entries_dict[patchfile_name]

        patch = {}
        file_info = {
            "name": file.name,
            "size": file.size,
            "csize": file.csize,
            "data_o": file.data_o,
            "parent_end": self.end
        }
        patch[self.name] = file_info

        with open(patchfile, "rb") as p:
            patch_data = p.read()
            size = len(patch_data)

        if file.csize != int("0xffffffffffffffff", 16):
            compressor = LZ4FrameCompressor(block_size=BLOCKSIZE_MAX256KB, compression_level=9, auto_flush=True)
            header = compressor.begin()
            data = compressor.compress(patch_data)
            trail = b"\x00" * 4
            data = b"".join([header, data, trail])
            csize = len(data)
        else:
            csize = file.csize
            data = patch_data

        with open(self.packfile_path, 'r+b') as pf:
            print(f"Patching {self.name}")
            pf.seek(file.data_ol)

            print(f"Writing data offset: {hex(self.end - self.data_o)}")
            pf.write(int.to_bytes(self.end - self.data_o, 8, 'little'))

            print(f"Writing size: {hex(size)}")
            pf.write(int.to_bytes(size, 8, 'little'))

            print(f"Writing compressed size: {hex(csize)}")
            pf.write(int.to_bytes(csize, 8, 'little'))

            print("Writing new file data")
            pf.seek(self.end)
            pf.write(data)

            print("Done!")
        return patch

    def unpatch(self, patch_entry):
        patchfile_name = patch_entry["name"]
        file = self.entries_dict[patchfile_name]

        with open(self.packfile_path, 'r+b') as pf:
            print(f"Patching {self.name}")
            pf.seek(file.data_ol)

            print(f"Writing data offset: {hex(self.end - self.data_o)}")
            pf.write(int.to_bytes(self.end - self.data_o, 8, 'little'))

            print(f"Writing size: {hex(size)}")
            pf.write(int.to_bytes(size, 8, 'little'))

            print(f"Writing compressed size: {hex(csize)}")
            pf.write(int.to_bytes(csize, 8, 'little'))

            print("Writing new file data")
            pf.seek(self.end)
            pf.write(data)

            print("Done!")
        print(self.end)
        print(patch_entry)

    def close(self):
        self.stream.close()
