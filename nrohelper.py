#!/usr/bin/env python3

from nro import *


def pad_blocksize(value, block=64):
    """Pads value to blocksize

    Args:
        value (bytes): Value to pad
        block (int): Block size (Default: 64)
    """
    if len(value) % block != 0:
        value += b"\x00" * (block - (len(value) % block))
    return value


class NROHelper:
    def __init__(self, f):
        try:
            self.fp = open(f, 'r+b')
        except:
            raise FileNotFoundError("File not found")

        self.nro = NRO.from_buffer_copy(self.fp.read(sizeof(NRO)))

        if self.nro.header.magic != NROHEADERMAGIC:
            self.fp.close()
            raise Exception("Header magic is wrong, should be 'NRO0'")

        self.fp.seek(self.nro.header.size)
        try:
            self.asset = Asset.from_buffer_copy(self.fp.read(sizeof(Asset)))
        except ValueError:
            self.fp.close()
            raise NotImplementedError("NROs without an Assets section are currently not supported.")

        if self.asset.magic != ASSETHEADERMAGIC:
            self.fp.close()
            raise Exception("Asset header magic is wrong, should be 'ASET'")

        # Assets are located at: End of NRO (Beginning of Assets) + Asset Offset
        self.fp.seek(self.nro.header.size + self.asset.icon.offset)
        self.icon = self.fp.read(self.asset.icon.size)

        self.fp.seek(self.nro.header.size + self.asset.nacp.offset)
        self.nacp = NACP.from_buffer_copy(self.fp.read(self.asset.nacp.size))

        self.fp.seek(self.nro.header.size + self.asset.romfs.offset)
        self.romfs = self.fp.read(self.asset.romfs.size)

    def extract_icon(self, name="icon.jpg"):
        """Extracts icon to name."""
        if self.asset.icon.size != 0:
            with open(name, "wb") as icon_file:
                icon_file.write(self.icon)
        else:
            print("No icon available")

    def extract_nacp(self, name="control.nacp"):
        """Extracts NACP to name."""
        if self.asset.nacp.size != 0:
            with open(name, "wb") as nacp_file:
                nacp_file.write(bytes(self.nacp))
        else:
            print("No NACP available")

    def extract_romfs(self, name="romfs.romfs"):
        """Extracts RomFS to name."""
        if self.asset.romfs.size != 0:
            with open(name, "wb") as romfs_file:
                romfs_file.write(self.romfs)
        else:
            print("No RomFS available")

    def edit_name(self, name):
        """Edits name of the NRO in the NACP (currently all languages)."""
        if len(name) > 512:
            raise ValueError("Name must be < 512 characters")

        name = pad_blocksize(name.encode(), 512)
        name = ARRAY(c_byte, 512).from_buffer_copy(name)
        for language in self.nacp.title:
            language.name = name

    def edit_publisher(self, publisher):
        """Edits publisher name of the NRO in the NACP (currently all languages)."""
        if len(publisher) > 256:
            raise ValueError("Publisher name must be < 256 characters")

        publisher = pad_blocksize(publisher.encode(), 256)
        publisher = ARRAY(c_byte, 256).from_buffer_copy(publisher)
        for language in self.nacp.title:
            language.publisher = publisher

    def edit_version(self, version):
        """Edits the version in the NACP."""
        if len(version) > 16:
            raise ValueError("Version must be < 16 characters")

        version = pad_blocksize(version.encode(), 16)
        version = ARRAY(c_byte, 16).from_buffer_copy(version)
        self.nacp.displayVersion = version

    def save(self):
        """Saves NRO and asset header."""
        self.fp.seek(0)
        self.fp.write(bytes(self.nro))
        self.fp.seek(self.nro.header.size)
        self.fp.write(bytes(self.asset))

    def save_nacp(self):
        """Saves NACP."""
        self.fp.seek(self.nro.header.size + self.asset.nacp.offset)
        self.fp.write(bytes(self.nacp))

    def get_name(self):
        """Returns first language entry name."""
        return self.nacp.title[0].get_name()

    def get_publisher(self):
        """Returns first language entry publisher."""
        return self.nacp.title[0].get_publisher()

    def __del__(self):
        self.fp.close()

    def __repr__(self):
        name = self.nacp.title[0].get_name()
        publisher = self.nacp.title[0].get_publisher()
        version = self.nacp.get_version()

        return "{name} v{version} by {author}".format(
            name="<not set>" if name == "" else name,
            version="<not set>" if version == "" else version,
            author="<not set>" if publisher == "" else publisher,
        )

    def __str__(self):
        name = self.nacp.title[0].get_name()
        publisher = self.nacp.title[0].get_publisher()
        version = self.nacp.get_version()

        output = "NRO:\n"
        output += "  Name: {0}\n".format("<not set>" if name == "" else name)
        output += "  Author: {0}\n".format("<not set>" if publisher == "" else publisher)
        output += "  Version: {0}\n".format("<not set>" if version == "" else version)
        output += "\n"

        output += "  RomFS available: {0}\n".format("Yes" if self.asset.romfs.size > 0 else "No")

        return output
