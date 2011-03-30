#! /usr/bin/python
from misc import *

if __name__ == '__main__':
    if not sys.argv[0] or len(sys.argv) < 2:
        fn = 'linux.ubi'
        fn = 'wince.ubi'
    else:
        fn = sys.argv[1]
    
    f = open(fn, 'r')
    
    x = X000FF()
    x.debug = 1
    x.fromfile(f)
