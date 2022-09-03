import mmap


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


def extract(filename, output_directory):
    print(filename, output_directory)