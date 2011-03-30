#! /usr/bin/python
from array import array, ArrayType
import struct
import sys
from copy import copy
from namestruct import NameStruct
from tags import *
from hd import hd

class Foo:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class RomException(Exception):
    pass
    
class FileFormatException(RomException):
    """When the file format isn't ok"""

class RecordBoundsException(RomException):
    """When the records bounds are bad"""

def read32(f):
    data = f.read(4)
    if not data:
        return None
    return struct.unpack('<L', data)[0]

def write32(f, val):
    f.write(struct.pack('<L', val))

class Record:
    def __init__(self, addr, data, name = 'unknown'):
        self.addr = addr
        if data.__class__ == ArrayType:
            self.data = data
        else:
            self.data = array('B', data)
        self.name = name

    def __repr__(self):
        return 'Region: %08x:%08x (%08x) name=%s' % (self.addr, self.addr + len(self.data), len(self.data), self.name)

    def __cmp__(self, other):
        return cmp(self.addr, other.addr)

    def tofile(self, f):
        write32(f, self.addr)
        write32(f, len(self.data))
        write32(f, sum(self.data))
        self.data.tofile(f)
        
class Region:
    MAGIC = 'B000FF\n'
    
    debug = 0
    
    def __init__(self):
        self.records = []
        self.entry = 0

    def update(self):
        self.addr = 0x100000000l
        self.end = 0
        for record in self.records:
            if self.addr > record.addr:
                self.addr = record.addr
            if self.end < record.addr + len(record.data):
                self.end = record.addr + len(record.data)
        self.size = self.end - self.addr

    def add(self, record):
        self.records.append(record)
        
    def header(self):
        return struct.pack('<LL', self.addr, self.size)

    def sorted(self):
        records = copy(self.records)
        records.sort()
        end = self.addr + self.size
        addr = 0
        last = None
        for record in records:
            if record.addr < addr:
                raise RecordBoundsException("records overlap for %s and %s" % (record, last))
            addr = record.addr + len(record.data)
            last = record
            if addr > end:
                raise RecordBoundsException("records extend outside region for %s" % record)
        return records

    def blobify(self):
        """Create a large array with the contents of the region"""
        
        data = array('B', '\0' * self.size)
        for record in self.sorted():
            ofs = record.addr - self.addr
            data[ofs : ofs + len(record.data)] = record.data
        return data

    def fromfile(self, f):
        magic = f.read(len(self.MAGIC))
        if magic != self.MAGIC:
            raise FileFormatException("invalid magic, expected %s, got %s" % (repr(self.MAGIC), repr(magic)))
            
        self.addr = read32(f)
        self.size = read32(f)

        if self.debug:
            print "region addr: 0x%08x" % self.addr
            print "region size: 0x%08x" % self.size
            print

        while 1:
            addr = read32(f)
            size = read32(f)
            checksum = read32(f)

            if addr == None:
                if self.debug:
                    print "    record EOF"
                    print
                break
                
            if self.debug:
                print "    record addr: 0x%08x" % addr
                print "    record size: 0x%08x" % size
                print "    record sum:  0x%08x" % checksum
                print

            if not addr:
                self.entry = size
                break
                
            data = array('B')
            data.fromfile(f, size)

            if checksum != sum(data):
                raise FileFormatException("invalid checksum, expected 0x%08x, got 0x%08x" % (checksum, sum(data)))

            self.records.append(Record(addr, data))
                
    def tofile(self, f):
        f.write(self.MAGIC)

        write32(f, self.addr)
        write32(f, self.size)
        
        for record in self.records:
            record.tofile(f)
            
        write32(f, 0)
        write32(f, self.entry)
        write32(f, 0)

class X000FF:
    MAGIC = 'X000FF\n'
    
    debug = 0
    
    def __init__(self):
        self.regions = []
        
    def fromfile(self, f):
        magic = f.read(len(self.MAGIC))
        if magic != self.MAGIC:
            raise FileFormatException("invalid magic, expected %s, got %s" % (repr(self.MAGIC), repr(magic)))
            
        checksum = read32(f)
        numregions = read32(f)

        if self.debug:
            print "x000ff sum: 0x%08x" % checksum
            print "x000ff count: 0x%08x" % numregions
            print
            
        headers = []
        for i in range(numregions):
            addr = read32(f)
            size = read32(f)
        
            if self.debug:
                print "header addr: 0x%08x" % addr
                print "header size: 0x%08x" % size
            
            headers.append((addr, size))
        if self.debug:
            print

        self.regions = []
        for i in range(numregions):
            region = Region()
            if self.debug:
                region.debug = 1
            region.fromfile(f)
            
            if region.addr != headers[i][0] or region.size != headers[i][1]:
                raise FileFormatException("header does not match region %d" % i)
                
            self.regions.append(region)
                
        if read32(f) != 0:
            raise FileFormatException("missing terminating zero")
           
        if f.read(1):
            raise FileFormatException("file continues past end")

        print "0x%x" % f.tell()

class ROMHDR(NameStruct):
    def __init__(self):
        NameStruct.__init__(self, '<')
        self.add('L', 'dllfirst')
        self.add('L', 'dlllast')
        self.add('L', 'physfirst')
        self.add('L', 'physlast')
        self.add('L', 'nummods')
        self.add('L', 'ulRAMStart')
        self.add('L', 'ulRAMFree')
        self.add('L', 'ulRAMEnd')
        self.add('L', 'ulCopyEntries')
        self.add('L', 'ulCopyOffset')
        self.add('L', 'ulProfileLen')
        self.add('L', 'ulProfileOffset')
        self.add('L', 'numfiles')
        self.add('L', 'ulKernelFlags')
        self.add('L', 'ulFSRamPercent')
        self.add('L', 'ulDrivglobStart')
        self.add('L', 'ulDrivglobLen')
        self.add('H', 'usCPUType')
        self.add('H', 'usMiscFlags')
        self.add('L', 'pExtensions')
        self.add('L', 'ulTrackingStart')
        self.add('L', 'ulTrackingLen')

class PTOC(NameStruct):
    def __init__(self, address = None):
        NameStruct.__init__(self, '<')
        self.add('4B', 'magic')
        self.add('L', 'addr')

        self.magic = array('B', 'ECEC')
        self.address = address

class TOCEntry(NameStruct):
    def __init__(self):
        NameStruct.__init__(self, '<')
        self.add('L', 'dwFileAttributes')
        self.add('Q', 'ftTime')
        self.add('L', 'nFileSize')
        self.add('L', 'lpszFileName')
        self.add('L', 'ulE32Offset')
        self.add('L', 'ulO32Offset')
        self.add('L', 'ulLoadOffset')

class FileEntry(NameStruct):
    def __init__(self):
        NameStruct.__init__(self, '<')
        self.add('L', 'dwFileAttributes')
        self.add('Q', 'ftTime')
        self.add('L', 'nRealFileSize')
        self.add('L', 'nCompFileSize')
        self.add('L', 'lpszFileName')
        self.add('L', 'ulLoadOffset')

class CopyEntry(NameStruct):
    def __init__(self):
        NameStruct.__init__(self, '<')
        self.add('L', 'ulSource')
        self.add('L', 'ulDest')
        self.add('L', 'ulCopyLen')
        self.add('L', 'ulDestLen')

class E32Rom(NameStruct):
    def __init__(self):
        NameStruct.__init__(self, '<')
        self.add('H', 'objcnt')
        self.add('H', 'imageflags')
        self.add('L', 'entryrva')
        self.add('L', 'vbase')
        self.add('H', 'subsysmajor')
        self.add('H', 'subsysminor')
        self.add('L', 'stackmax')
        self.add('L', 'vsize')
        self.add('L', 'sect14rva')
        self.add('L', 'sect14size')
        self.add('72B', 'unit')
        self.add('H', 'subsys')

class E32Info(NameStruct):
    def __init__(self):
        NameStruct.__init__(self, '<')
        self.add('L', 'rva')
        self.add('L', 'size')

class O32Rom(NameStruct):
    def __init__(self):
        NameStruct.__init__(self, '<')
        self.add('L', 'vsize')
        self.add('L', 'rva')
        self.add('L', 'psize')
        self.add('L', 'dataptr')
        self.add('L', 'reladdr')
        self.add('L', 'flags')

class O32Obj(NameStruct):
    def __init__(self):
        NameStruct.__init__(self, '<')
        self.add('8s', 'name')
        self.add('L', 'vsize')
        self.add('L', 'rva')
        self.add('L', 'pSize')
        self.add('L', 'dataptr')
        self.add('L', 'reladdr')
        self.add('L', 'access')
        self.add('L', 'temp3')
        self.add('L', 'flags')
    
class XIPEntry(NameStruct):
    def __init__(self):
        NameStruct.__init__(self, '<')
        self.add('L', 'pvAddr')
        self.add('L', 'dwLength')
        self.add('L', 'dwMaxLength')
        self.add('H', 'usOrder')
        self.add('H', 'usFlags')
        self.add('L', 'dwVersion')
        self.add('32s', 'szName')
        self.add('L', 'dwAlgoFlags')
        self.add('L', 'dwKeyLen')
        self.add('B', 'bType')
        self.add('B', 'bVersion')
        self.add('H', 'reserved')
        self.add('L', 'aKeyAlg')
        self.add('4s', 'magic')
        self.add('L', 'bitlen')
        self.add('L', 'pubexp')
        self.add('576B', 'modulusdata')

class PartEntry(NameStruct):
    def __init__(self):
        NameStruct.__init__(self, '<')
        self.add('B', 'BootInd')
        self.add('B', 'FirstHead')
        self.add('B', 'FirstSector')
        self.add('B', 'FirstTrack')
        self.add('B', 'FileSystem')
        self.add('B', 'LastHead')
        self.add('B', 'LastSector')
        self.add('B', 'LastTrack')
        self.add('L', 'StartSector')
        self.add('L', 'TotalSectors')

class Memory(object):
    def __init__(self, addr = None):
        self.addr = addr
        if addr != None:
            self.start = addr
            self.end = addr
        else:
            self.start = 1l<<32
            self.end = 0
        self.areas = []

    def calcsize(data):
        if type(data) == str:
            return len(data)
        else:
            return data.calcsize()
    calcsize = staticmethod(calcsize)

    def add(self, data, name = None, addr = None):
        if addr == None:
            addr = self.addr

        size = self.calcsize(data)
        end = addr + size
        
        # print "add %08x:%08x (%08x) %s" % (addr, end, size, name)

        for old_addr, old_end, old_data, old_name in self.areas:
            if addr >= old_addr and end < old_end:
                raise ValueError("%s at 0x%x-0x%x overlaps existing area %s at 0x%x-0x%x" % (name, addr, end, old_name, old_addr, old_end))
        
        self.areas.append((addr, end, data, name))

        self.addr = end

        if self.start > addr:
            self.start = addr
        if self.end < end:
            self.end = end

    def align(self, alignment):
        self.addr = (self.addr + alignment - 1) & ~(alignment - 1)
        if self.end < self.addr:
            self.end = self.addr

    def translate(self, old, new):
        t = Memory()
        for addr, end, data, name in self.areas:
            assert end - addr == self.calcsize(data)
            t.add(data, name = name, addr = addr - old + new)
        return t

    def pack(self):
        """Create a large array from Memory.start to Memory.end"""

        size = self.end - self.start

        data = array('B', '\0' * size)
        for start, end, data, name in self.areas:
            size = end - start
            assert size == self.calcsize(data)
            ofs = start - self.start
            data[ofs : ofs + size] = array('B', record.data)
        return data.tostring()

    def dump(self):
        print hex(self.start), hex(self.end)
        for addr, end, data, name in self.areas:
            print hex(addr), self.calcsize(data), name

def create_linux(params, load_addr):
    tags = [
        Tag_Core(flags = 0, pagesize = 0x1000, rootdev = 0x00ff),
        Tag_Cmdline(params.cmdline),
        Tag_Mem(start = params.ram_phys, size = params.ram_size),
        ]

    if params.initrd:
        initrd_tag = Tag_Initrd(size = len(params.initrd))
        tags.append(initrd_tag)

    tags += [
        Tag_Videotext(video_lines = params.video_lines,
                      video_cols = params.video_cols),
        Tag_None()
        ]

    tags_size = sum([tag.calcsize() for tag in tags])

    mem = Memory(load_addr)
    
    mem.add(params.prepare, 'prepare')
	
    mem.add(struct.pack('<L', params.mpllcon), 'MPLLCON')
    mem.add(struct.pack('<L', tags_size >> 2), 'tags size')

    for t in tags:
        mem.add(t, str(type(t)))

    mem.add(struct.pack('<L', params.machine_type), 'machine type')

    mem.add(params.kernel, 'kernel')

    if params.initrd:
        # some space needed for some reason, 32k is too little, 64k is
        # enough, so add a lot to be on the safe side.
        mem.addr += 0x80000

        mem.align(0x1000)
        initrd_tag.start = mem.addr
        mem.add(params.initrd, 'initrd')

    return mem

def create_rom(rom_addr, ram_end, images):
    rom = Memory(rom_addr)

    # The pointer to the table of contents must be at the ROM address + 0x40
    # The ptoc value will be updated later
    ptoc = PTOC()
    rom.addr = rom_addr + 0x40
    rom.add(ptoc, 'ptoc')

    # Leave some space between the PTOC and the TOC itself
    rom.align(0x400)

    # First put all the data pointed to by the table of contents into
    # the rom
    tocentries = []
    start = 1l<<32
    end = 0
    for im in images:
        o32 = O32Rom()
        o32.clear()
        rom.align(0x10)
        o32_addr = rom.addr
        rom.add(o32, 'o32')
        
        e32 = E32Rom()
        e32.clear()
        rom.align(0x10)
        e32_addr = rom.addr
        rom.add(e32, 'e32')
        
        rom.align(0x10)
        tocentry_fn_addr = rom.addr
        rom.add(im.name + '\0', "%s string" % im.name)
        
        tocentry = TOCEntry()
        tocentry.clear()

        tocentry.lpszFileName = tocentry_fn_addr
        tocentry.dwFileAttributes = 0x00000001
        tocentry.ftTime = 0x1c4920fd41ac84al
        tocentry.ulLoadOffset = im.start
        tocentry.nFileSize = im.end - im.start
        tocentry.ulO32Offset = o32_addr
        tocentry.ulE32Offset = e32_addr

        tocentry.name = "%s tocentry" % im.name
        tocentries.append(tocentry)

        if start > im.start:
            start = im.start
        if end < im.end:
            end = im.end
            
    rom.align(0x10)
    ptoc.addr = rom.addr

    # The table of contents that starts with the ROM header.     
    romhdr = ROMHDR()
    romhdr.clear()
    romhdr.dllfirst = 0x02000000l
    romhdr.dlllast = 0x02000000l
    romhdr.physfirst = rom_addr
    romhdr.physlast = end - 1
    romhdr.ulRAMStart = end
    romhdr.ulRAMFree = end + 256 * 1024 * 1024
    romhdr.ulRAMEnd = ram_end
    romhdr.ulFSRamPercent = 0x80808080l
    romhdr.usCPUType = 0x01c0
    romhdr.nummods = len(tocentries)
    rom.add(romhdr, 'romhdr')

    # And immediately after, all the toc entries
    for te in tocentries:
        rom.add(te, te.name)

    return rom

def write_header(f, region):
    write32(f, region.addr)
    write32(f, region.size)

def write_x000ff(f, regions):
    f.write('X000FF\n')
    
    header = ''
    for region in regions:
        header = header + region.header()
    header_sum = sum(array('B', header))

    write32(f, header_sum)

    write32(f, len(regions))

    for region in regions:
        write_header(f, region)

    for region in regions:
        region.tofile(f)

    # end marker
    write32(f, 0)

def dump_regions(*regions):
    records = []

    for region in regions:
        records += region.records

    def cmp(a, b):
        return int(a.addr - b.addr)
    
    records.sort(cmp)

    end = 0
    for record in records:
        print record
        hd(record.data[:0x200])
        assert record.addr >= end
        end = record.addr + len(record.data)

class Params:
    pass

def create_linux_region(params):
    # First create a bootable linux image with the prepare binary, the
    # linux kernel and optionally an initrd.  The linux image should
    # be at the rom address +0x1000 so that there is some space for
    # the table of contents.

    image = create_linux(params, 
                         params.ram_phys + params.rom_offset + 0x1000)
    image.name = "image"

    # The Linux image uses physical address so we have to create a
    # copy of the linux image that uses virtual addresses
    image_virtual = image.translate(params.ram_phys, params.ram_virt)
    image_virtual.name = 'nk.exe'

    # Create a ROM with a table of contents based on this image
    rom = create_rom(params.ram_virt + params.rom_offset,
                     params.ram_virt + params.ram_size,
                     [ image_virtual ])
    rom.name = "rom"

    # Add a branch to the image at the start of the ROMs
    rom.addr = params.ram_virt + params.rom_offset
    rom.add('\xfe\x03\x00\xea', 'branch')

    rom.align(0x10)

    # Create a region
    region = Region()

    # The entry point is the Linux image
    region.entry = params.ram_virt + params.rom_offset + 0x1000

    # Add all the memory areas
    for mem in rom, image_virtual:
        for addr, end, data, name in mem.areas:
            if isinstance(data, NameStruct):
                data = data.pack()
            region.add(Record(addr, data, name))

    # Update the size for the region
    region.update()

    for mem in rom, image_virtual:
        if region.addr > mem.start:
            region.addr = mem.start
        if region.size < mem.end - region.addr:
            region.size = mem.end - region.addr

    return region

if __name__ == '__main__':
    pass

