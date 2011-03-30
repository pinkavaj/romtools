#! /usr/bin/python
from misc import *
import sys

def usage_exit(code):
    sys.stderr.write("Usage: %s files...\n" % sys.argv[0])
    sys.exit(code)
    
if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.argv.append('wince.ubi')
        # usage_exit(1)
    
    for fn in sys.argv[1:]:
        print "Splitting", fn
        f = open(fn, 'r')
        x = X000FF()
        x.fromfile(f)
        f.close()
        
        for i in range(len(x.regions)):
            outfn = '%s.%d' % (fn, i)
            print "Writing", outfn
            f = open(outfn, 'w')
            x.regions[i].tofile(f)
