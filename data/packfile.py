# This class stores the information from the header of the packfile
from helpers import tools
from tqdm import tqdm
import mmap
import os


class Packfile:
    def __init__(self, stream, packfile_name, subpack=False):
        self.subpack = subpack
        self.validate(stream)

        self.packfile_name = packfile_name

        self.num_files = tools.read(stream, 16, 4, reverse=True)
        self.num_paths = tools.read(stream, 20, 4, reverse=True)
        self.data_offset = tools.read(stream, 64, 4, reverse=True)

        self.header_offset = 120
        self.filenames_offset = (
            tools.read(stream, 24, 4, reverse=True) + self.header_offset
        )
        self.stream = stream

    def validate(self, stream):
        descriptor = tools.read(stream, 0, 4)
        if hex(descriptor) != "0xce0a8951":
            print("Invalid file type")
            quit()

        version = tools.read(stream, 4, 4)
        if hex(version) != "0x11000000":
            print("Invalid file version")
            quit()

    def filename_mappings(self, stream):
        filenames_bytes = self.data_offset - self.filenames_offset
        data = tools.read(stream, self.filenames_offset, filenames_bytes, integer=False)

        names = data.split(b"\x00")
        del names[(self.num_files + self.num_paths) :]

        locations = []
        locations.append(self.filenames_offset)
        offset = self.filenames_offset
        mm = mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ)
        while len(locations) < self.num_files + self.num_paths:
            location = mm.find(b"\x00", offset + 1)
            locations.append(location + 1)
            offset = location

        return dict(zip(locations, names))

    def extract(self, output_directory):
        stream = self.stream
        mappings = self.filename_mappings(stream)

        mm = mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ)

        stream.seek(self.header_offset, 0)

        for file in tqdm(range(0, self.num_files), leave=(not self.subpack)):
            name_offset = int.from_bytes(stream.read(8), "little")
            name_offset += self.filenames_offset
            name = mappings[name_offset]
            name = name.decode("ascii")

            path_offset = int.from_bytes(stream.read(8), "little")
            path_offset += self.filenames_offset

            path = mappings[path_offset]
            path = path.decode("ascii")

            file_data_offset = int.from_bytes(stream.read(8), "little")
            file_data_offset += self.data_offset

            size = int.from_bytes(stream.read(8), "little")
            stream.read(16)

            self.write_file(name, path, size, file_data_offset, mm, output_directory)

    def write_file(self, name, path, size, offset, mm, output_directory):
        path = f"{output_directory}\\{path}"
        if not os.path.exists(path):
            os.makedirs(path)

        mm.seek(offset)
        output_file = f"{path}\\{name}"

        file = mm.read(size)

        with open(output_file, "wb") as f:
            f.write(file)

        if output_file.endswith(".vpp_pc") or output_file.endswith(".str2_pc"):
            extract_subfile(output_file, self.packfile_name, output_directory)


def extract_subfile(filename, root_packfile, output_directory):
    with open(filename, "rb") as f:
        packfile = Packfile(f, root_packfile, subpack=True)
        packfile.extract(output_directory)
    os.remove(filename)
