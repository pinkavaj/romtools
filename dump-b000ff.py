#! /usr/bin/python
from misc import *
from hd import hd
import sys

def fmt(key, value):
    if type(value) == int or type(value) == long:
        value = "0x%08x" % value
    print "%-20s: %s" % (key, value)
        
def getsz(data):
    z = data.index(0)
    return data[:z].tostring()

def dump_copyentries(data, base, addr, count):
    ofs = addr - base
    
    for i in range(count):
        fmt('CopyEntry', addr)

        copyentry = CopyEntry()
        end = ofs + copyentry.calcsize()
        copyentry.unpack(data[ofs:end])
        ofs = end

        for name in copyentry.names:
            print "%-20s: 0x%08x" % (name, copyentry[name])
        print

def dump_obj(data, base, addr, obj):
    fmt(obj.__class__.__name__, addr)
    obj.unpack(data[addr-base : addr-base + obj.calcsize()])
    obj.dump()
    print

def dump_e32(data, base, addr):
    e32 = E32Rom()
    fmt(e32.__class__.__name__, addr)
    e32.unpack(data[addr-base : addr-base + e32.calcsize()])
    e32.names.remove('unit')
    e32.dump()
    print

    unit = e32['unit']
    for i in range(9):
        dump_obj(unit, 0, i * 8, E32Info())
    
def dump_romhdr(data, base, addr):
    ofs = addr - base
    
    fmt('ROMHDR', addr)

    romhdr = ROMHDR()
    end = ofs + romhdr.calcsize()
    romhdr.unpack(data[ofs:end])
    ofs = end

    romhdr.dump()
    print

    for i in range(romhdr['nummods']):
        fmt('module', ofs + base)
        tocentry = TOCEntry()
        end = ofs + tocentry.calcsize()
        tocentry.unpack(data[ofs:end])
        ofs = end
        fmt('szFileName', getsz(data[tocentry['lpszFileName']-base:]))
        tocentry.dump()
        print

        dump_e32(data, base, tocentry['ulE32Offset'])
        dump_obj(data, base, tocentry['ulO32Offset'], O32Rom())

    for i in range(romhdr['numfiles']):
        fmt('file', ofs + base)
        fileentry = FileEntry()
        end = ofs + fileentry.calcsize()
        fileentry.unpack(data[ofs:end])
        ofs = end
        fmt('szFileName', getsz(data[fileentry['lpszFileName']-base:]))
        fileentry.dump()
        print

    dump_copyentries(data, base, romhdr['ulCopyOffset'], romhdr['ulCopyEntries'])

def dump(region):
    fmt("region addr", region.addr)
    fmt("region size", region.size)
    fmt("region entry", region.entry)
    print
    
    data = region.blobify()

    base = region.addr

    if data[0x40:0x44] != array('B', 'ECEC'):
        print "no TOC found"
        return

    romhdr_addr = struct.unpack('<L', data[0x44:0x48])[0]

    dump_romhdr(data, base, romhdr_addr)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        if 0:
            sys.argv.append('nboot.ubi')
        else:
            sys.argv.append('wince.ubi.7')
    
    for fn in sys.argv[1:]:
        try:
            region = Region()
            region.fromfile(open(fn, 'r'))

            dump(region)

        except FileFormatException, msg:
            sys.stderr.write('%s: %s\n' % (fn, str(msg)))
