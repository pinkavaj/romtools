#! /usr/bin/python
import string
import struct
from array import array, ArrayType
from misc import *

def create_xip(region):
    xipentry = XIPEntry()
    xipentry.clear()
    name = 'XIPKERNEL'
    xipentry.szName = name + '\0' * (32-len(name))
    xipentry.pvAddr = region.addr
    xipentry.dwLength = region.size
    xipentry.dwMaxLength = region.size
    xipentry.usOrder = 1
    xipentry.usFlags = 0x8001
    xipentry.dwAlgoFlags = 0x00008003
    xipentry.dwKeyLen = 0x114
    xipentry.bType = 6
    xipentry.bVersion = 2
    xipentry.aKeyAlg = 0x00002400
    xipentry.magic = 'RSA1'
    xipentry.bitlen = 0x800
    xipentry.pubexp = 0x10001
    xipentry.modulusdata = (151, 100, 210, 10, 97, 1, 241, 98, 114,
    177, 172, 249, 44 , 13, 6, 174, 88, 122, 186, 192, 64, 25, 79,
    219, 232, 170, 126, 74, 16, 88, 39, 99, 70, 124, 131, 17, 120, 18,
    85, 231, 119, 79, 212, 172, 18, 159, 60, 236, 177, 143, 233, 122,
    112, 68, 250, 133, 157, 156, 106, 131, 47, 140, 54, 112, 241, 63,
    149, 194, 189, 110, 2, 194, 166, 98, 163, 76, 222, 38, 98, 26, 19,
    180, 64, 66, 134, 70, 104, 255, 67, 90, 220, 185, 91, 189, 150,
    162, 16, 30, 41, 68, 166, 164, 244, 6, 177, 79, 72, 223, 3, 120,
    168, 78, 7, 70, 116, 88, 82, 52, 87, 249 , 221, 156, 35, 106, 177,
    117, 175, 199, 237, 1, 247, 7, 235, 120, 171, 31, 102, 139, 29,
    44, 158, 93, 32, 252, 243, 207, 206, 13, 110, 201, 123, 181, 130,
    153, 100, 149, 190, 105, 191, 234, 122, 115, 65, 110, 101, 145,
    230, 165, 226, 206, 245, 166, 179, 187, 198, 19, 241, 177, 77,
    185, 36, 226, 8, 11, 219, 196, 3, 213 , 225, 222, 17, 112, 138,
    81, 202, 7, 109, 51, 218, 37, 13, 230, 175, 216, 183, 13, 110,
    244, 184, 216, 196, 184, 200, 240, 239, 185, 199, 164, 138, 47,
    192, 153, 217, 175, 169, 255, 27, 124, 189, 8, 37, 207, 173, 53,
    22, 248, 154, 225, 72, 12, 111, 4, 34, 27, 4, 130, 134, 195, 127,
    190, 145, 95, 0, 176, 231, 204, 0, 0 , 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0 , 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 , 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 , 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0)

    xip = Region()
    xip.add(Record(region.end,
                   struct.pack('<L', 1) +
                   xipentry.pack() +
                   struct.pack('<L', 0), 'XIP'))
    xip.update()

    return xip

def main():
    params = Params()

    # Physical RAM address
    params.ram_phys = 0x30000000l

    # The amount of RAM in the device
    params.ram_size = 64 * 1024 * 1024l

    # Virtual RAM address, i.e. where the bootloader has mapped the RAM
    params.ram_virt = 0x8c000000l

    # The offset from the start of RAM where the ROM image should be loaded
    params.rom_offset = 32 * 1024 * 1024

    if 0:
        params.machine_type = 656	  # Acer N30
    else:
        params.machine_type = 927	  # Acer N35
    params.mpllcon = 0x0007f011  # 270MHz from a 12MHz clock

    params.video_lines = 48
    params.video_cols = 40

    # Configuration

    if 1:
        console_cmd = 'console=tty verbose loglevel=7'
    else:
        console_cmd = 'console=tty console=ttySAC0,115200 verbose loglevel=7'

    root_cmds = {
        # boot from an initramfs cpio archive loaded as a ramdisk
        'bootchoice' : 'rdinit=/sbin/bootchoice',
        'initramfs' : 'rdinit=/sbin/init',

        # boot using NFS via the USB port
        'nfs' : ('root=nfs nfsroot=192.168.131.102:/export/n30/nfsroot' +
                 ' ip=192.168.131.201:192.168.131.102:192.168.131.102:255.255.255.0:n30:usb0:off' +
                 ' rootdelay=5 noinitrd'),

        # a mmc partition
        'mmc1' : 'console=tty verbose rootdelay=2 root=/dev/mmcblk0p2 ro init=/linuxrc',
        'mmc3' : 'root=0xfe03 rootdelay=5 rw noinitrd',

        # jffs2 on internal flash
        'mtd1' : 'console=tty verbose rootdelay=2 root=/dev/mmcblk0p2 ro ubi.mtd=rootfs',
        'mtd3' : 'root=0x1f03 rootfstype=jffs2 rw noinitrd'
        }

    root_cmd = root_cmds['mtd1']

    params.cmdline = '%s %s' % (console_cmd, root_cmd)

    # The data to put into the image

    params.prepare = open('prepare.bin').read()
    params.kernel = open('zImage').read()
    if 0:
        params.initrd = open('initrd').read()
    else:
        params.initrd = None

    region = create_linux_region(params)

    xip = create_xip(region)

    # dump_regions(region, xip)

    f = open('linux-n30.ubi', 'w')
    write_x000ff(f, [region, xip])
    f.close()

    print "N30 kernel done"

main()
