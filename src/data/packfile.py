import mmap
import os
import io
from turtle import update
import lz4.frame

from lz4.frame import BLOCKSIZE_MAX256KB, LZ4FrameCompressor

from helpers import tools
from tqdm import tqdm


class Packfile:
    def __init__(self, stream, packfile_name, subpack=False):
        self.subpack = subpack
        self.validate(stream)

        self.packfile_name = packfile_name

        stream.seek(0)
        self.num_files = tools.read(stream, 16, 4, reverse=True)
        self.num_paths = tools.read(stream, 20, 4, reverse=True)

        self.data_size = tools.read(stream, 40, 4, reverse=True)
        self.compressed_data_size = tools.read(stream, 48, 4, reverse=True)

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

    def filename_mappings(self, stream, inverse=False):
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

        if inverse:
            names = [name.decode('ascii') for name in names]
            return dict(zip(names, locations))
        else:
            return dict(zip(locations, names))

    def patch(self, new, stream):
        with open(new, 'rb') as new:
            new_data = new.read()

        mappings = self.filename_mappings(stream)
        stream.seek(self.header_offset, 0)

        for file in range(0, self.num_files):
            name_offset = int.from_bytes(stream.read(8), "little")
            name_offset += self.filenames_offset

            name = mappings[name_offset]
            name = name.decode("ascii")

            next = stream.read(8)
            update_from_here = stream.tell()
            if update_from_here < 0:
                update_from_here = update_from_here + 8196

            path_offset = int.from_bytes(next, "little")
            path_offset += self.filenames_offset

            path = mappings[path_offset]
            path = path.decode("ascii")
            
            file_data_offset = int.from_bytes(stream.read(8), "little")
            file_data_offset += self.data_offset

            size = int.from_bytes(stream.read(8), "little")
            compressed_size = int.from_bytes(stream.read(8), "little")
            stream.read(8)
    
            if compressed_size != int("0xffffffffffffffff", 16):
                print(compressed_size)
                compressor = LZ4FrameCompressor(block_size=BLOCKSIZE_MAX256KB, compression_level=9, auto_flush=True)
                header = compressor.begin()
                data = compressor.compress(new_data)
                trail = b"\x00" * 4
                data = b"".join([header, data, trail])
                compressed_size = len(data)
            else:
                data = new_data

            if name == new.name:
                print(f"Patching {name}")
                stream.seek(0, io.SEEK_END)
                new_location = stream.tell()
                if new_location < 0:
                    new_location = new_location + 8196
                print(update_from_here)
                print(new_location)
                new_location_bytes = int.to_bytes(new_location - self.data_offset, 8, 'little')
                new_size = int.to_bytes(len(new_data), 8, 'little')
                flag = int.to_bytes(256, 4, 'big')

                with open(self.packfile_name, 'r+b') as file:
                    print(f"Patching {self.packfile_name}")
                    print("Writing header data")
                    file.seek(update_from_here)
                    file.write(new_location_bytes)
                    file.write(new_size)
                    file.write(int.to_bytes(compressed_size, 8, 'little'))
                    file.write(flag)
                    print("Writing new file data")
                    file.seek(new_location)
                    file.write(data)
                    print("done!")
                break

    def extract(self, output_directory, recursive):
        stream = self.stream
        mappings = self.filename_mappings()

        mm = mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ)
        stream.seek(self.header_offset, 0)

        t = tqdm(
            range(0, self.num_files),
            leave=(not self.subpack),
        )
        for file in t:
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
            compressed_size = int.from_bytes(stream.read(8), "little")
            stream.read(8)

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

    def write_file(
        self,
        name,
        path,
        size,
        compressed_size,
        offset,
        mm,
        output_directory,
        recursive=True,
    ):
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


def extract_subfile(filename, root_packfile, output_directory):
    with open(filename, "rb") as f:
        packfile = Packfile(f, root_packfile, subpack=True)
        packfile.extract(output_directory)
    os.remove(filename)
