#! /usr/bin/python
import sys
from array import array, ArrayType

def hd_line(block, addr = 0):
    sys.stdout.write('%08x ' % addr)
    for i in range(16):
        if i < len(block):
            if i == 8:
                sys.stdout.write(' -')
            sys.stdout.write(' %02x' % block[i])
        else:
            if i == 8:
                sys.stdout.write('  ')
            sys.stdout.write('   ')
                
    sys.stdout.write('  ')
    for v in block:
        if v >= 32 and v < 127:
            sys.stdout.write(chr(v))
        else:
            sys.stdout.write('.')

    sys.stdout.write('\n')
    
def hd(data, base = 0):
    if data.__class__ != ArrayType:
        data = array('B', data)
    
    last_block = None
    last_same = False
    for ofs in range(0, len(data), 16):
        block = data[ofs:ofs+16]

        if last_block == block:
            if not last_same:
                last_same = True
                sys.stdout.write('  ...\n')
            continue

        last_block = block
        last_same = False

        hd_line(block, base + ofs)
            
    if last_same:
        hd_line(block, base + ofs)

if __name__ == '__main__':
    data = open('nboot.ubi', 'r').read()
    hd(data)
