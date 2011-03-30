#! /usr/bin/python
import sys
import string

def main():
    if not sys.argv[0]:
        path = '/tmp/n30.log'
    else:
        path = sys.argv[1]
        
    f = open(path, 'r')

    t0 = 0
    last_charge = -1
    while 1:
        l = f.readline()
        if not l:
            break

        parts = l.split()
        if len(parts) != 15 or parts[12][-1:] != '%':
            continue

        h, m, s = parts[3].split(':')
        t = (string.atoi(h) * 60 + string.atoi(m)) * 60 + string.atoi(s)
        if not t0:
            t0 = t

        if t < t0:
            sys.stderr.write("%d %d %d\n" % (t, t0, hours * 3600))
            t0 = t - hours * 3600

        hours = (t - t0) / 3600.0

        charge = string.atoi(parts[12][:-1])

        if charge == -1 or last_charge == charge:
            continue

        last_charge = charge

        print "%.2f %2d" % (hours, charge)

    print "%.2f %2d" % (hours, charge)

main()


                
