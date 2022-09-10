
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
#
# name   - name of file
# path   - path of file
# size   - size of file
# csize  - compressed size of file
#
class File:
    def __init__(self, parent, start):
        self.name_ol = start

        parent.stream.seek(name_ol)
        self.name_o = int.from_bytes(parent.stream.read(8), "little")
        self.name = name.decode("ascii")

        self.filepath_offset = int.from_bytes(parent.stream.read(8), "little")
        path = self.path_offset + self.filenames_offset
        path = mappings[path_offset]
        self.path = path.decode("ascii")
        self.data_offset = int.from_bytes(parent.stream.read(8), "little")

        self.size = int.from_bytes(parent.stream.read(8), "little")
        compressed_size = int.from_bytes(parent.stream.read(8), "little")
        stream.read(8)

        self.parent = parent




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