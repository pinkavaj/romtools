#! /usr/bin/python
from namestruct import NameStruct

class Tag(NameStruct):
    def __init__(self, tag):
        NameStruct.__init__(self, '<')
        self.add('L', 'tag_size')
        self.add('L', 'tag_tag')
        self.tag_tag = tag

    def pack(self):
        size = self.calcsize()

        # the size of a tag must be multiple of a dword
        assert not size & 3
        self.tag_size = size >> 2
        return NameStruct.pack(self)

class Tag_Core(Tag):
    ATAG_CORE = 0x54410001

    def __init__(self, **d):
        Tag.__init__(self, self.ATAG_CORE)
        self.add('L', 'flags')
        self.add('L', 'pagesize')
        self.add('L', 'rootdev')

        self.update(d)
        
class Tag_Mem(Tag):
    ATAG_MEM = 0x54410002

    def __init__(self, **d):
        Tag.__init__(self, self.ATAG_MEM)
        self.add('L', 'size')
        self.add('L', 'start')

        self.update(d)

class Tag_Videotext(Tag):
    ATAG_VIDEOTEXT = 0x54410003

    def __init__(self, **d):
        Tag.__init__(self, self.ATAG_VIDEOTEXT)
        self.add('B', 'x', 0)
        self.add('B', 'y', 0)
        self.add('H', 'video_page', 0)
        self.add('B', 'video_mode', 0)
        self.add('B', 'video_cols', 0)
        self.add('H', 'video_ega_bx', 0)
        self.add('B', 'video_lines', 0)
        self.add('B', 'video_isvga', 0)
        self.add('H', 'video_points', 0)

        self.update(d)

class Tag_Initrd(Tag):
    ATAG_INITRD2 = 0x54420005

    def __init__(self, **d):
        Tag.__init__(self, self.ATAG_INITRD2)
        self.add('L', 'start')
        self.add('L', 'size')

        self.update(d)

class Tag_Cmdline(Tag):
    ATAG_CMDLINE = 0x54410009

    def __init__(self, cmdline):
        Tag.__init__(self, self.ATAG_CMDLINE)
        self.__slots__.append('cmdline')
        self.cmdline = cmdline

    def calcsize(self):
        # The header, the command line and a the terminating zero, all
        # padded to a 4 byte boundary
        return (Tag.calcsize(self) + len(self.cmdline) + 1 + 3) & ~3

    def pack(self):
        size = self.calcsize()
        self.tag_size = size >> 2

        data = NameStruct.pack(self) + self.cmdline
        data += '\0' * (size - len(data))
        return data

class Tag_None(Tag):
    ATAG_NONE = 0x00000000

    def __init__(self):
        Tag.__init__(self, self.ATAG_NONE)

    def pack(self):
        # the NONE tag is a bit special in that the size is 0
        self.tag_size = 0
        return NameStruct.pack(self)

if __name__ == '__main__':
    import os
    import hd

    ram_addr = 0x30000000
    ram_size = 64 * 1024 * 1024

    initrd_addr = 0x30800000
    initrd_size = os.stat('initrd')[6]

    cmdline = "console=ttySAC0,115200 verbose rdinit=/sbin/bootchoice"
    
    tags = [
        Tag_Core(flags = 0, pagesize = 0x1000, rootdev = 0x00ff),
        Tag_Cmdline(cmdline),
        Tag_Mem(start = ram_addr, size = ram_size),
        ]

    if initrd_addr and initrd_size:
        tags += [
            Tag_Initrd(start = initrd_addr, size = initrd_size),
            ]

    tags += [
        Tag_Videotext(video_lines = 40, video_cols = 48),
        Tag_None()
        ]

    l = []
    for t in tags:
        l.append(t.pack())

    hd.hd(''.join(l))

