#! /usr/bin/python
from misc import *
from hd import hd
import sys

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.argv.append('nboot.ubi')
    
    for fn in sys.argv[1:]:
        try:
            region = Region()
            region.fromfile(open(fn, 'r'))

            data = region.blobify()

            hd(data, base=region.addr)

        except FileFormatException, msg:
            sys.stderr.write('%s: %s\n' % (fn, str(msg)))
