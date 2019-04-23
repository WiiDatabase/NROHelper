#!/usr/bin/env python3

from ctypes import *

NROHEADERMAGIC = b"NRO0"
ASSETHEADERMAGIC = b"ASET"


class NRO(LittleEndianStructure):
    """https://switchbrew.org/w/index.php?title=NRO"""

    class Start(LittleEndianStructure):
        """https://switchbrew.org/w/index.php?title=NRO#NRO_Start"""
        _pack_ = 1
        _fields_ = [
            ("unused", c_uint32),
            ("mod0_offset", c_uint32),
            ("padding", c_uint64)
        ]

    class Header(LittleEndianStructure):
        """https://switchbrew.org/w/index.php?title=NRO#NRO_Header"""

        class SegmentHeader(LittleEndianStructure):
            """https://switchbrew.org/w/index.php?title=NRO#SegmentHeader"""
            _pack_ = 1
            _fields_ = [
                ("offset", c_uint32),
                ("size", c_uint32)
            ]

        _pack_ = 1
        _fields_ = [
            ("magic", ARRAY(c_char, 4)),
            ("version", c_uint32),
            ("size", c_uint32),
            ("flags", c_uint32),
            ("segmentHeader", ARRAY(SegmentHeader, 3)),
            ("bssSize", c_uint32),
            ("reserved", c_uint32),
            ("build_id", ARRAY(c_byte, 32)),
            ("reserved", c_uint64),
            ("segmentHeader2", ARRAY(SegmentHeader, 3)),
        ]

    _pack_ = 1
    _fields_ = [
        ("start", Start),
        ("header", Header)
    ]


class Asset(LittleEndianStructure):
    """https://switchbrew.org/w/index.php?title=NRO#Assets"""

    class AssetSection(LittleEndianStructure):
        """https://switchbrew.org/w/index.php?title=NRO#AssetSection"""
        _pack_ = 1
        _fields_ = [
            ("offset", c_uint64),
            ("size", c_uint64)
        ]

    _pack_ = 1
    _fields_ = [
        ("magic", ARRAY(c_char, 4)),
        ("version", c_uint32),
        ("icon", AssetSection),
        ("nacp", AssetSection),
        ("romfs", AssetSection),
    ]


class NACP(LittleEndianStructure):
    """https://switchbrew.org/wiki/Control.nacp"""

    class TitleEntry(LittleEndianStructure):
        """https://switchbrew.org/wiki/Control.nacp#Title_Entry"""
        _pack_ = 1
        _fields_ = [
            ("name", ARRAY(c_byte, 0x200)),
            ("publisher", ARRAY(c_byte, 0x100))
        ]

        def get_name(self):
            return bytes(self.name).rstrip(b"\x00").decode('utf-8')

        def get_publisher(self):
            return bytes(self.publisher).rstrip(b"\x00").decode('utf-8')

        def __repr__(self):
            name = self.get_name()
            publisher = self.get_publisher()
            return "{0} by {1}".format(
                "<not set>" if name == "" else name,
                "<not set>" if publisher == "" else publisher
            )

    _pack_ = 1
    _fields_ = [
        ("title", ARRAY(TitleEntry, 16)),
        ("isbn", ARRAY(c_byte, 0x25)),
        ("startupUserAccount", c_uint8),
        ("unknown1", c_uint8),
        ("unknown2", c_uint8),
        ("applicationAttribute", c_uint32),
        ("supportedLanguages", c_uint32),
        ("parentalControl", c_uint32),
        ("isScreenshotEnabled", c_uint8),
        ("videoCaptureMode", c_uint8),
        ("isDataLossConfirmationEnabled", c_uint8),
        ("unknown3", c_uint8),
        ("presenceGroupId", c_uint64),
        ("ratingAge", ARRAY(c_byte, 0x20)),
        ("displayVersion", ARRAY(c_byte, 0x10)),
        ("addOnContentBaseId", c_uint64),
        ("saveDataOwnerId", c_uint64),
        ("userAccountSaveDataSize", c_uint64),
        ("userAccountSaveDataJournalSize", c_uint64),
        ("deviceSaveDataSize", c_uint64),
        ("deviceSaveDataJournalSize", c_uint64),
        ("bcatDeliveryCacheStorageSize", c_uint64),
        ("applicationErrorCodeCategory", c_uint64),
        ("localCommunicationIds", ARRAY(c_byte, 0x40)),
        ("logoType", c_uint8),
        ("logoHandling", c_uint8),
        ("isRuntimeAddOnContentInstallEnabled", c_uint8),
        ("unknown4", ARRAY(c_byte, 3)),
        ("unknown5", c_uint8),
        ("unknown6", c_uint8),
        ("seedForPseudoDeviceId", c_uint64),
        ("bcatPassphrase", ARRAY(c_byte, 0x41)),
        ("unknown7", c_uint8),
        ("unknown8", ARRAY(c_byte, 0x6)),
        ("userAccountSaveDataMaxSize", c_uint64),
        ("userAccountSaveDataMaxJournalSize", c_uint64),
        ("deviceSaveDataMaxSize", c_uint64),
        ("deviceSaveDataMaxJournalSize", c_uint64),
        ("temporaryStorageSize", c_uint64),
        ("cacheStorageSize", c_uint64),
        ("cacheStorageJournalSize", c_uint64),
        ("cacheStorageMaxSizeAndMaxJournalSize", c_uint64),
        ("cacheStorageMaxIndex", c_uint64),
        ("unknown9", ARRAY(c_byte, 0xE70))
    ]

    def get_version(self):
        return bytes(self.displayVersion).rstrip(b"\x00").decode('utf-8')
