#ARM_COMPILE=/usr/local/arm/3.3.2/bin/arm-linux-

# CROSS_COMPILE=/opt/crosstool/gcc-3.4.1-glibc-2.3.3/arm-9tdmi-linux-gnu/bin/arm-9tdmi-linux-gnu-
#CROSS_COMPILE=arm-softfloat-linux-gnueabi-
CROSS_COMPILE=armv4tl-softfloat-linux-gnueabi-
#CROSS_COMPILE=arm-softfloat-linux-uclibcgnueabi-

CC=gcc
CFLAGS=-Wall
LDLIBS=-lusb

TARGETS=dnw prepare.bin hello.bin linux-n30.ubi \
	resume.bin reset.bin

all: $(TARGETS)

linux-n30.ubi: build-n30.py prepare.bin zImage
	./build-n30.py

linux-h1940.nbf linux-h1940.r2sd linux-h1940.raw: build-h1940.py prepare.bin zImage initrd
	./build-h1940.py

clean:
	rm -f $(TARGETS) *.o *.pyc *.pyo core *~

dummy.s: dummy.c
	$(CROSS_COMPILE)gcc -Os -S $<

%.o: %.S
	$(CROSS_COMPILE)gcc -D__ASSEMBLY__ -c $+

%.bin: %.o
	$(CROSS_COMPILE)objcopy $< -O binary $@

zip:
	rm -f romtools.zip
	zip romtools.zip Makefile *.[chS] *.py

dummy:
