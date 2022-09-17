import hashlib
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
        self.size = helpers.read(stream, Packfile.SIZE_O, 8, reverse=True)
        self.csize = helpers.read(stream, Packfile.CSIZE_O, 8, reverse=True)

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

    def parent_data(self):
        entries_bar = tqdm(self.entries, leave=(not self.subpack))
        parents = []
        for file_entry in entries_bar:
            parents += file_entry.parent_data()
            entries_bar.set_description(f"Analyzing: {self.name}", refresh=True)
        parents_dict = helpers.combine_dicts(parents)
        return parents_dict

    def extract_and_patch_subfiles(self, files, gamepath):
        temp = f"{gamepath}\\mod_config\\temp"
        if not os.path.exists(temp):
            os.mkdir(temp)

        created = []
        for file in files.keys():
            entry = self.entries_dict[file]
            entry.extract(temp, False, preserve_path=False)
            packfile = Packfile(f"{temp}\\{entry.name}")
            to_patch = {
                "root": files[file]
            }
            packfile.patch({}, to_patch, gamepath)
            packfile.close()
            created.append(f"{temp}\\{entry.name}")
        return created

    def patch(self, patch_json, to_patch, gamepath):
        if self.name not in patch_json:
            patch_json[self.name] = {
                "end": self.end,
                "patched": {}
            }

        patchfiles = []
        if "root" in to_patch:
            patchfiles += to_patch["root"]

        if "sub" in to_patch:
            patchfiles += self.extract_and_patch_subfiles(to_patch["sub"], gamepath)

        for patchfile in patchfiles:
            patchfile_name = os.path.basename(os.path.normpath(patchfile))
            patchfile_path = os.path.normpath(os.path.join(patchfile, "..\\"))

            file = self.entries_dict[patchfile_name]

            with open(patchfile, "rb") as p:
                patch_data = p.read()
                patch_hash = hashlib.md5(patch_data).hexdigest()

            patched = patch_json[self.name]["patched"]

            # No need to patch if it's exactly the same
            if file.name in patched:
                original_hash = patched[file.name]["patch_hash"]
                if original_hash == patch_hash:
                    print(f"{file.name} already patched")
                    continue

            data, size, csize, patch_size = self.compress(file, patch_data)

            patch_offset = self.stream.seek(0, io.SEEK_END)  # where to write new data
            if file.name in patched:
                original_size = patched[file.name]["patch_size"]
                if original_size >= patch_size:
                    # If it was patched before and the file is smaller now
                    # Just put it in the same place
                    patch_offset = patched[file.name]["patch_offset"]

            patch_json[self.name]["patched"][file.name] = {
                "size": file.size,
                "csize": file.csize,
                "data_o": file.data_o,
                "patch_size": patch_size,
                "patch_hash": patch_hash,
                "patch_offset": patch_offset
            }

            with open(self.packfile_path, 'r+b') as pf:
                print(f"Patching {self.name}: {file.name}")
                pf.seek(file.data_ol)
                pf.write(int.to_bytes(patch_offset - self.data_o, 8, 'little'))
                pf.write(int.to_bytes(size, 8, 'little'))
                pf.write(int.to_bytes(csize, 8, 'little'))

                pf.seek(patch_offset)
                pf.write(data)
        return patch_json

    def unpatch(self, patch_json):
        with open(self.packfile_path, 'r+b') as pf:
            patched = patch_json[self.name]["patched"]
            for name in patched.keys():
                file = self.entries_dict[name]

                print(f"Restoring {self.name}")
                pf.seek(file.data_ol)
                pf.write(int.to_bytes(patched[name]["data_o"], 8, 'little'))
                pf.write(int.to_bytes(patched[name]["size"], 8, 'little'))
                pf.write(int.to_bytes(patched[name]["csize"], 8, 'little'))

        with open(self.packfile_path, 'a') as pf:
            pf.seek(patch_json[self.name]["end"])
            print(f"Removing {self.name} patched data")
            pf.truncate()
            print(f"Done restoring {self.name}")
            del patch_json[self.name]
            return patch_json

        print("unknown error occured unpatching")
        return patch_json

    def compress(self, entry, data):
        size = len(data)
        if entry.compressed:
            compressor = LZ4FrameCompressor(block_size=BLOCKSIZE_MAX256KB, compression_level=9, auto_flush=True)
            header = compressor.begin()
            data = compressor.compress(data)
            trail = b"\x00" * 4
            data = b"".join([header, data, trail])
            csize = len(data)
            patch_size = csize
        else:
            csize = entry.csize
            patch_size = size
        return data, size, csize, patch_size

    def close(self):
        self.stream.close()
