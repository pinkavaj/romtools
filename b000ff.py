#! /usr/bin/python
from misc import *
import sys

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.argv.append('nboot.ubi')
    
    for fn in sys.argv[1:]:
        try:
            region = Region()
            region.debug = 1
            region.fromfile(open(fn, 'r'))
        except FileFormatException, msg:
            sys.stderr.write('%s: %s\n' % (fn, str(msg)))

