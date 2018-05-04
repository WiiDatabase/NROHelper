#!/usr/bin/env python3
from Struct import Struct


class NRO:
    """Represents an NRO file
       Reference: http://switchbrew.org/index.php?title=NRO

    Args:
        f (str): Path to an NRO
    """

    class NROHeader(Struct):
        def __format__(self, format_spec=None):
            self.unused = Struct.uint32
            self.mod0_offset = Struct.uint32
            self.padding_1 = Struct.uint64
            self.magic = Struct.string(4)
            self.unknown_1 = Struct.uint32
            self.size = Struct.uint32
            self.unknown_2 = Struct.uint32
            self.segment_hdr_1 = self.SegmentHeader()
            self.segment_hdr_2 = self.SegmentHeader()
            self.segment_hdr_3 = self.SegmentHeader()  # TODO: Should be a list()...
            self.bss_size = Struct.uint32
            self.unknown_3 = Struct.uint32
            self.build_id = Struct.string(32)
            self.padding_2 = Struct.string(16)
            self.unknown_4 = Struct.string(16)

        class SegmentHeader(Struct):
            """Reference: http://switchbrew.org/index.php?title=NRO#SegmentHeader"""

            def __format__(self, format_spec=None):
                self.offset = Struct.uint32
                self.size = Struct.uint32

    class AssetHeader(Struct):
        """Reference: http://switchbrew.org/index.php?title=NRO#AssetHeader"""

        def __format__(self, format_spec=None):
            self.magic = Struct.string(4)
            self.version = Struct.uint32
            self.icon = self.AssetSection()
            self.nacp = self.AssetSection()
            self.romfs = self.AssetSection()

        class AssetSection(Struct):
            """Reference: http://switchbrew.org/index.php?title=NRO#AssetSection"""

            def __format__(self, format_spec=None):
                self.offset = Struct.uint64
                self.size = Struct.uint64

    class NACP(Struct):
        """Reference: http://switchbrew.org/index.php?title=Control.nacp"""

        def __format__(self, format_spec=None):
            self.padding_1 = Struct.string(36)
            self.unknown_1 = Struct.uint32
            self.unknown_2 = Struct.uint32
            self.unknown_3 = Struct.uint32
            self.unknown_4 = Struct.uint32
            self.unknown_5 = Struct.uint32
            self.titleid = Struct.uint64
            self.unknown_6 = Struct.string(32)
            self.version = Struct.string(16)
            self.base_titleid = Struct.uint64
            self.titleid_2 = Struct.uint64
            self.unknown_7 = Struct.uint32
            self.unknown_8 = Struct.uint32
            self.unknown_9 = Struct.uint32
            self.padding_2 = Struct.string(28)
            self.product_code = Struct.string(8)  # or uint64?
            self.titleid_3 = Struct.uint64
            self.titleid_4 = Struct.uint64[7]
            self.unknown_10 = Struct.uint32
            self.unknown_11 = Struct.uint32
            self.titleid_5 = Struct.uint64
            self.bcat_pass = Struct.string(64)
            self.padding = Struct.string(3776)

        def get_version(self):
            return self.version.rstrip(b"\x00").decode('utf-8')

    class LanguageEntry(Struct):
        """Reference: http://switchbrew.org/index.php?title=Control.nacp#Language_Entry"""

        def __format__(self, format_spec=None):
            self.name = Struct.string(512)
            self.author = Struct.string(256)

        def get_name(self):
            return self.name.rstrip(b"\x00").decode('utf-8')

        def get_author(self):
            return self.author.rstrip(b"\x00").decode('utf-8')

        def __repr__(self):
            name = self.get_name()
            author = self.get_author()
            return "{0} by {1}".format(
                "<not set>" if name == "" else name,
                "<not set>" if author == "" else author
            )

    def __init__(self, f):
        self.f = f
        try:
            fp = open(self.f, 'rb')
            file = fp.read()
        except:
            raise FileNotFoundError("File not found")

        self.hdr = self.NROHeader().unpack(file[:128])

        if self.hdr.magic != b"NRO0":
            fp.close()
            raise Exception("Header magic is wrong, should be 'NRO0'")

        assetbuffer = file[self.hdr.size:self.hdr.size + 56]
        if len(assetbuffer) == 0:
            raise Exception("NROs without an Assets section are currently not supported.")
        self.asset_hdr = self.AssetHeader().unpack(assetbuffer)
        if self.asset_hdr.magic != b"ASET":
            fp.close()
            raise Exception("Asset header magic is wrong, should be 'ASET'")

        # Assets are located at: End of NRO (Beginning of Assets) + Asset Offset
        self.icon = file[self.hdr.size + self.asset_hdr.icon.offset:
                         self.hdr.size + self.asset_hdr.icon.offset + self.asset_hdr.icon.size]
        self.rawnacp = file[self.hdr.size + self.asset_hdr.nacp.offset:
                            self.hdr.size + self.asset_hdr.nacp.offset + self.asset_hdr.nacp.size]
        self.romfs = file[self.hdr.size + self.asset_hdr.romfs.offset:
                          self.hdr.size + self.asset_hdr.romfs.offset + self.asset_hdr.romfs.size]

        langbuffer = self.rawnacp[:12288]
        self.language_entries = []
        for lang in range(14):
            entry = self.LanguageEntry().unpack(langbuffer[lang * 768:(lang * 768) + 768])
            self.language_entries.append(entry)

        self.nacp = self.NACP().unpack(self.rawnacp[12288:])

        fp.close()

    def extract_icon(self, name="icon.jpg"):
        """Extracts icon to name"""
        if self.asset_hdr.icon.size != 0:
            with open(name, "wb") as icon_file:
                icon_file.write(self.icon)
        else:
            print("No icon available")

    def extract_nacp(self, name="control.nacp"):
        """Extracts NACP to name"""
        if self.asset_hdr.nacp.size != 0:
            with open(name, "wb") as nacp_file:
                nacp_file.write(self.rawnacp)
        else:
            print("No NACP available")

    def extract_romfs(self, name="romfs.romfs"):
        """Extracts RomFS to name"""
        if self.asset_hdr.romfs.size != 0:
            with open(name, "wb") as romfs_file:
                romfs_file.write(self.romfs)
        else:
            print("No RomFS available")

    def __repr__(self):
        name = self.language_entries[0].get_name()
        author = self.language_entries[0].get_author()
        version = self.nacp.get_version()

        return "{name} v{version} by {author}".format(
            name="<not set>" if name == "" else name,
            version="<not set>" if version == "" else version,
            author="<not set>" if author == "" else author,
        )

    def __str__(self):
        name = self.language_entries[0].get_name()
        author = self.language_entries[0].get_author()
        version = self.nacp.get_version()

        output = "NRO:\n"
        output += "  Name: {0}\n".format("<not set>" if name == "" else name)
        output += "  Author: {0}\n".format("<not set>" if author == "" else author)
        output += "  Version: {0}\n".format("<not set>" if version == "" else version)
        output += "\n"

        output += "  RomFS available: {0}\n".format("Yes" if self.asset_hdr.romfs.size > 0 else "No")

        return output


def extract_icon(nro, icon_name="icon.jpg"):
    NRO(nro).extract_icon(icon_name)


def extract_nacp(nro, nacp_name="control.nacp"):
    NRO(nro).extract_nacp(nacp_name)


def extract_romfs(nro, romfs_name="romfs.romfs"):
    NRO(nro).extract_romfs(romfs_name)


def show_info(nro):
    print(NRO(nro))
