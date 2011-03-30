#! /usr/bin/python
import string
import struct
from array import array, ArrayType
from misc import *

def main():
    params = Params()

    # Physical RAM address
    params.ram_phys = 0x10000000l

    # The amount of RAM in the device
    params.ram_size = 64 * 1024 * 1024l

    # The offset from the start of RAM where the ROM image should be loaded
    params.rom_offset = 0

    params.machine_type = 1666
    params.mpllcon = 0

    params.video_lines = 48
    params.video_cols = 40

    # Configuration

    if 0:
        console_cmd = 'console=tty verbose'
    else:
        console_cmd = 'console=ttySAC0,115200 verbose'

    root_cmds = {
        # boot from an initramfs cpio archive loaded as a ramdisk
        'initramfs' : 'rdinit=/sbin/bootchoice',

        # boot using NFS via the USB port
        'nfs' : ('root=nfs nfsroot=192.168.131.102:/export/n30/nfsroot' +
                 ' ip=192.168.131.201:192.168.131.102:192.168.131.102:255.255.255.0:n30:usb0:off' +
                 ' rootdelay=5 noinitrd'),

        # a mmc partition
        'mmc1' : 'root=0xfe01 rootdelay=5 rw noinitrd',
        'mmc2' : 'root=0xfe02 rootdelay=5 rw noinitrd',
        'mmc3' : 'root=0xfe03 rootdelay=5 rw noinitrd',

        # jffs2 on internal flash
        'mtd3' : 'root=0x1f03 rootfstype=jffs2 rw noinitrd'
        }

    root_cmd = root_cmds['initramfs']

    params.cmdline = '%s %s' % (console_cmd, root_cmd)

    # The data to put into the image

    params.prepare = open('prepare.bin').read()
    params.kernel = '\x55' * 65536 + open('zImage').read()
    if 0:
        params.initrd = open('initrd').read()
    else:
        params.initrd = None

    image = create_linux(params, 0x10000000)

    image.dump()

    data = image.pack()

    open('bchs2.bin', 'w').write(data)

main()
