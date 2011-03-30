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

def dump(region):
    data = region.blobify()
    base = region.addr
    
    nentries = struct.unpack('<L', data[0:4])[0]

    ofs = 4
    for i in range(nentries):
        fmt('XIPEntry', base + ofs)
        xipentry = XIPEntry()
        end = ofs + xipentry.calcsize()
        xipentry.unpack(data[ofs:end])
        ofs = end
            
        xipentry.dump()
        print
        
if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.argv.append('wince.ubi.8')
    
    for fn in sys.argv[1:]:
        try:
            region = Region()
            region.fromfile(open(fn, 'r'))

            dump(region)

        except FileFormatException, msg:
            sys.stderr.write('%s: %s\n' % (fn, str(msg)))
