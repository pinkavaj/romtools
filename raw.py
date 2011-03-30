#! /usr/bin/python
import struct

def main():
    prepare_data = open('prepare.bin').read()

    machine_data = struct.pack('<L', 656)

    tag_data = open('tag.bin').read()

    kernel_data = open('zImage').read()

    initrd_data = open('initrd').read()

    buf = '\0' * 0x1000

    buf += prepare_data

    buf += '\0' * (0x10fc - len(buf))

    buf += machine_data
    buf += tag_data

    buf += '\0' * (0x2000 - len(buf))

    buf += kernel_data

    buf += '\0' * (2 * 1024 * 1024 - len(buf))

    buf += initrd_data

    buf = '\0' * 0x2c000 + buf
    
    open('raw.img', 'w').write(buf)

main()


    
    

    
