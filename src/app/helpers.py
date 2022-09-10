import mmap
import io

from data.packfile import Packfile


def reverse(input_bytes):
    output_data = bytearray(input_bytes)
    output_data.reverse()
    return bytes(output_data)


def find(file, data, start=0, is_string=False, reverse=False):
    mm = mmap.mmap(file.fileno(), start, access=mmap.ACCESS_READ)
    if is_string:
        data = data.encode("ascii")

    if type(data) is int:
        data = int.to_bytes(data, 4, "big")

    if reverse:
        data = bytearray(data)
        data.reverse()
        data = bytes(data)

    location = mm.find(data)
    return location


def read(file, location, data_bytes, integer=True, reverse=False):
    file.seek(location, 0)
    output_data = file.read(data_bytes)
    if reverse:
        output_data = bytearray(output_data)
        output_data.reverse()
        output_data = bytes(output_data)

    if integer:
        return int.from_bytes(output_data, "big")

    return output_data


def read_string(stream, seperator):
    output = b''
    while len(output) == 0 or output[-1:] != seperator:
        output += stream.read(1)
    return output[:-1].decode("ascii")


def extract_subpack(data, output_directory, name):
    subpack_stream = io.BytesIO(data)
    packfile = Packfile(subpack_stream=subpack_stream, subpack_name=name)
    packfile.extract(output_directory, recursive=True)


