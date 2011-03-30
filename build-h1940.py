#! /usr/bin/python
import string
import struct
from array import array, ArrayType
from misc import *

class NBFHeader(NameStruct):
    def __init__(self):
        NameStruct.__init__(self, '<')
        self.add('15s', 'hw')
        self.add('15s', 'sw')
        self.add('L', 'checksum')
        self.add('L', 'size')

class R2SDHeader(NameStruct):
    def __init__(self):
        NameStruct.__init__(self, '<')
        self.add('12s', 'magic')
        self.add('L', 'checksum')
        self.add('580s', 'ones')
        self.add('L', 'size')
        self.add('424s', 'zeroes')

        self.ones = '\xff' * 580
        self.zeroes = '\0' * 424

def main():
    params = Params()
    
    # Physical RAM address
    params.ram_phys = 0x30000000l

    # The amount of RAM in the device
    params.ram_size = 64 * 1024 * 1024l
    
    # Virtual RAM address, i.e. where the bootloader has mapped the RAM
    params.ram_virt = 0x80000000l

    # The offset from the start of RAM where the ROM image should be loaded
    params.rom_offset = 256 * 1024

    params.machine_type = 347	  # Ipaq H1940
    params.mpllcon = 0		  # Don't change the clock

    params.video_lines = 48
    params.video_cols = 40

    # Configuration
    params.cmdline = ('console=tty verbose' +
                      ' root=nfs nfsroot=192.168.131.102:/export/n30/nfsroot' +
                      ' ip=192.168.131.201:192.168.131.102:192.168.131.102:255.255.255.0:n30:usb0:off' +
                      ' rootdelay=5 noinitrd')

    # The data to put into the image
    params.prepare = open('prepare.bin').read()
    params.kernel = open('zImage').read()
    if 0:
        params.initrd = open('initrd').read()
    else:
        params.initrd = None

    region = create_linux_region(params)

    # Make the image size an even multiple of a megabyte
    # The WinCE image is padded to a megabyte, so follow that example
    region.size = (region.size + 0xfffff) & ~0xfffff

    data = region.blobify()

    # dump_regions(region)

    checksum = sum(data)
    
    f = open('linux-h1940.raw', 'w')
    data.tofile(f)
    f.close()

    nbf = NBFHeader()
    nbf.hw = "hp iPAQ h1940"
    nbf.sw = "1.00.00 ENG"
    nbf.checksum = checksum
    nbf.size = len(data)

    f = open('linux-h1940.nbf', 'w')
    f.write(nbf.pack())
    data.tofile(f)
    f.close()

    r2sd = R2SDHeader()
    r2sd.magic = 'HTC$HB20-222'
    r2sd.checksum = checksum
    r2sd.size = len(data)

    # to generate this file, use:
    # bzcat h1940_r2sd.img.bz2 | dd bs=512 skip=2 count=8 of=h1940-bootstrap-1.07.bin

    f = open('h1940-bootstrap-1.07.bin')
    bootstrap = f.read()
    f.close()

    f = open('linux-h1940.r2sd', 'w')
    f.write(r2sd.pack())
    f.write(bootstrap)
    data.tofile(f)
    f.close()

    print "H1940 kernel done"

main()
