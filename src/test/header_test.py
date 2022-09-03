import pytest
import os

from src.data.packfile import Packfile


def test_vpp_pc_header_values():
    with open("src/test/test_header.vpp_pc", "rb") as vpp:
        packfile = Packfile(vpp, "test", False)
        assert packfile.num_files == 149383
        assert packfile.num_paths == 290

        assert packfile.header_offset == int("0x78", 0)
        assert packfile.filenames_offset == int("0x6d72d8", 0)
        assert packfile.data_offset == int("0xca6800", 0)


def test_str2_header_values():
    with open("src/test/test_header.str2_pc", "rb") as vpp:
        packfile = Packfile(vpp, "test", False)
        assert packfile.num_files == 1365
        assert packfile.num_paths == 290

        assert packfile.header_offset == int("0x78", 0)
        assert packfile.filenames_offset == int("0x6d72d8", 0)
        assert packfile.data_offset == int("0xca6800", 0)
