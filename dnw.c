#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>
#include <time.h>
#include <usb.h>
#include <errno.h>

static struct usb_device *find_s3c2410() 
{
    struct usb_bus *busses;
    struct usb_bus *bus;
    struct usb_device *dev;

    busses = usb_get_busses();

    for (bus = busses; bus; bus = bus->next) {
	for (dev = bus->devices; dev; dev = dev->next) {
	    if (dev->descriptor.idVendor == 0x5345 
		&& dev->descriptor.idProduct == 0x1234)
		return dev;
	}
    }

    return NULL;
}

enum { bufsize = 0x4000 };

int main(int argc, char *argv[]) 
{
    struct usb_device *dev;
    usb_dev_handle *udev; 
    ssize_t n, count;
    char product[64];
    const char *fn;
    int fd;
    char buf[bufsize];
    off_t size, divisor, written;
    time_t t0, t1, t;
    int r;

    if (argc != 2) {
	fprintf(stderr, "Usage: %s ubi-file\n", argv[0]);
	exit(1);
    }

    fn = argv[1];
    
    usb_init();
    usb_find_busses();
    usb_find_devices();

    dev = find_s3c2410();
    if (!dev) {
	fprintf(stderr, "no matching usb device found\n");
	exit(1);
    }

    udev = usb_open(dev); 
    if (!udev) {
	fprintf(stderr, "failed to open usb device %s/%s\n", 
		dev->bus->dirname, dev->filename);
	exit(1);
    }

    r = usb_claim_interface(udev, 0);
    if (r < 0) {
	fprintf(stderr, "failed to claim usb device %s/%s: %s\n", 
		dev->bus->dirname, dev->filename, strerror(r));
	exit(1);
    }

    if (!dev->descriptor.iProduct) {
	fprintf(stderr, "no product name for usb device %s/%s\n", 
		dev->bus->dirname, dev->filename);
	exit(1);
    }

    r = usb_get_string_simple(udev, dev->descriptor.iProduct, product, sizeof(product));
    if (r < 0) {
	fprintf(stderr, "unable to fetch product for usb device %s/%s: %s\n",
		dev->bus->dirname, dev->filename, strerror(r));
	exit(1);
    }

    printf("%s/%s: %s\n", dev->bus->dirname, dev->filename, product);

    if (!dev->config) {
	fprintf(stderr, "could not get configuration for usb device %s/%s\n",
		dev->bus->dirname, dev->filename);
	exit(1);
    }

    if ((fd = open(fn, O_RDONLY)) < 0) {
	perror(fn);
	exit(1);
    }

    if ((size = lseek(fd, 0L, SEEK_END)) == -1
	|| lseek(fd, 0L, SEEK_SET) == -1) {
	perror(fn);
	exit(1);
    }

    divisor = size / 100;
    if (!divisor)
	divisor = 1;

    printf("Downloading Image...\n");
    fflush(stdout);

    written = 0;

    time(&t0);
    t1 = t0;
    while ((n = read(fd, buf, bufsize)) > 0) {
	count = n;

	n = usb_bulk_write(udev, 3, buf, count, 10000);
	if (n < 0) {
	    perror("usb_bulk_write");
	    exit(1);
	}
	if (n != count) {
	    fprintf(stderr, "short usb_bulk_write, got %d, expected %d\n", 
		    n, count);
	    exit(1);
	}

	written += n;

	time(&t);
	if (t - t1 >= 5) {
	    unsigned percent = (unsigned)(written / divisor);
	    unsigned speed = written / (t - t0) / 1000;

	    printf("Downloading image, %u%% done, %d kByte/sec\n", percent, speed);
	    fflush(stdout);

	    t1 = t;
	}
    }

    if (n < 0) {
	perror(fn);
	exit(1);
    }

    printf("Starting N30 Programming...\n");
    fflush(stdout);

    time(&t0);
    t1 = t0;
    while ((n = usb_bulk_read(udev, 1, buf, sizeof(buf), 5000)) > 0) {
	if (buf[3] == 0x7f) {
	    int i;

	    fprintf(stderr, "Download failed, status=[");
	    for (i = 0; i < n; i++) {
		if (i)
		    putc(' ', stderr);
		fprintf(stderr, "%02x", buf[i]);
	    }
	    fprintf(stderr, "]\n");
	    break;
	}

	if (buf[0] == 0x10) {
	    printf("Preparing...\n");
	} else if (buf[0] == 0x20) {
	    time(&t);
	    if (t - t1 >= 5) {
		printf("Flashing BINFS, %u%% done\n", buf[2]);
		fflush(stdout);
		t1 = t;
	    }
	} else if (buf[0] == 0x40) {
	    time(&t);
	    if (buf[3] == 100 || t - t1 >= 5) {
		printf("Flashing, %u%% done\n", buf[3]);
		fflush(stdout);
		t1 = t;
	    }
	    if (buf[3] == 100)
		break;
	} else {
	    int i;
	    for (i = 0; i < n; i++) 
		printf("%02x ", buf[i]);
	    printf("\n");
	}
		   
	sleep(1);
    }
    
    if (n < 0 && errno != ETIMEDOUT) {
	perror("usb read status");
	exit(1);
    }
    
    printf("Rebooting...\n");
    fflush(stdout);
    
    memset(buf, 0, sizeof(buf));
    buf[0] = 1;
    n = usb_bulk_write(udev, 3, buf, 4, 10000);
    
    if (n < 0) {
	perror("usb write ack");
	exit(1);
    }
    
    usb_release_interface(udev, 0);
    
    exit(0);
}
