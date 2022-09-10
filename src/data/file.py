
from helpers import tools


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
class File:
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
        self.name = tools.read_string(stream, b'\x00')

        stream.seek(parent.HEADER_O + parent.names_o + self.path_o)
        self.path = tools.read_string(stream, b'\x00')




    #         path = mappings[path_offset]
    #         path = path.decode("ascii")

    #         file_data_offset = int.from_bytes(self.stream.read(8), "little")
    #         file_data_offset += self.data_offset

    #         size = int.from_bytes(self.stream.read(8), "little")
    #         compressed_size = int.from_bytes(self.stream.read(8), "little")
    #         self.stream.read(8)



    #     if compressed_size != int("0xffffffffffffffff", 16):
    #         compressor = LZ4FrameCompressor(block_size=BLOCKSIZE_MAX256KB, compression_level=9, auto_flush=True)
    #         header = compressor.begin()
    #         data = compressor.compress(new_data)
    #         trail = b"\x00" * 4
    #         data = b"".join([header, data, trail])
    #         compressed_size = len(data)
    #     else:
    #         data = new_data

    #     return name, data, compressed_size, update_start

    # def write():