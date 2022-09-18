import io
import os
import lz4.frame

from app import helpers


# Atrributes:
#
# parent    - the packfile which contains this file
#
# name_ol   - location of filename offset in parent
# path_ol   - location of filepath offset in parent
# data_ol   - location of data offset in the parent
#
# name_o - value of filename offset in parent
# path_o - value of filepath offset in parent
# data_o - value of data offset
#
# size_l   - location of size in parent
# csize_l  - location of compressed size in parent
# flags_l  - location of flags
#
# name   - name of file
# type   - extension of file
# path   - path of file
# size   - size of file
# csize  - compressed size of file
# flags  - file flags
#
# compressed - whether or not compressed
class Entry:
    def __init__(self, parent, start):
        self.parent = parent

        stream = parent.stream
        stream.seek(start)

        self.name_ol = start
        self.name_o = int.from_bytes(stream.read(8), "little")

        self.path_ol = stream.tell()
        self.path_o = int.from_bytes(stream.read(8), "little")

        self.data_ol = stream.tell()
        self.data_o = int.from_bytes(parent.stream.read(8), "little")

        self.size_l = stream.tell()
        self.size = int.from_bytes(parent.stream.read(8), "little")

        self.csize_l = stream.tell()
        self.csize = int.from_bytes(parent.stream.read(8), "little")

        self.flags_l = stream.tell()
        self.flags = int.from_bytes(parent.stream.read(8), "little")

        stream.seek(parent.HEADER_O + parent.names_o + self.name_o)
        self.name = helpers.read_string(stream, b'\x00')
        self.type = self.name.split(".")[-1]

        stream.seek(parent.HEADER_O + parent.names_o + self.path_o)
        self.path = helpers.read_string(stream, b'\x00')

        self.compressed = (self.csize != int("0xffffffffffffffff", 16))

    def extract(self, output_directory, recursive, preserve_path=True):
        if preserve_path:
            path = f"{output_directory}\\{self.path}"
        else:
            path = output_directory

        if not os.path.exists(path):
            os.makedirs(path)

        stream = self.parent.stream
        stream.seek(self.parent.data_o + self.data_o)
        if self.csize != int("0xffffffffffffffff", 16):
            data = stream.read(self.csize)
            data = lz4.frame.decompress(data)
        else:
            data = stream.read(self.size)

        packfile_types = ["vpp_pc", "str2_pc"]
        if (self.type in packfile_types) and recursive:
            helpers.extract_subpack(data, output_directory, self.name)
        else:
            output_file = f"{path}\\{self.name}"
            with open(output_file, "wb") as f:
                f.write(data)

    def parent_data(self):
        parents = []

        parent_dict = {}
        if self.name not in parent_dict:
            parent_dict[self.name] = []
        parent_dict[self.name].append(self.parent.name)
        parents.append(parent_dict)
        packfile_types = ["vpp_pc", "str2_pc"]
        if (self.type in packfile_types):
            stream = self.parent.stream
            stream.seek(self.parent.data_o + self.data_o)
            if self.csize != int("0xffffffffffffffff", 16):
                data = stream.read(self.csize)
                data = lz4.frame.decompress(data)
            else:
                data = stream.read(self.size)
                parents += helpers.subpack_parents(data, self.name)
        return parents
