#! /usr/bin/python
from array import array, ArrayType
import struct

print 'H', struct.calcsize('H')
print 'I', struct.calcsize('I')
print 'L', struct.calcsize('L')
print 'Q', struct.calcsize('Q')

assert struct.calcsize('B') == 1
assert struct.calcsize('H') == 2
assert struct.calcsize('I') == 4
assert struct.calcsize('L') in [ 4, 8 ]
assert struct.calcsize('Q') == 8

class NameStruct(object):
    def __init__(self, fmt = ''):
        self._fmt = fmt
        self._members = []
        self.__slots__ = []

    def add(self, fmt, name = None, default = None):
        assert name not in self.__slots__

        # On 64 bit machines the meaning changes a bit
        if struct.calcsize('L') == 8:
            fmt = fmt.replace('L', 'I')

        count = 0
        for c in fmt:
            if c >= '0' and c <= '9':
                count = count * 10 + ord(c) - ord('0')
            else:
                if c == 's':
                    count = 0
                break

        self._fmt += fmt
        if name:
            self._members.append((name, count))
            self.__slots__.append(name)
            setattr(self, name, default)

    def calcsize(self):
        v = struct.calcsize(self._fmt)
        print self.__class__.__name__, v
        return v

    def unpack(self, data):
        l = struct.unpack(self._fmt, data)
        index = 0
        for name, count in self._members:
            if name:
                if count:
                    value = l[index:index+count]
                    index += count
                else:
                    value = l[index]
                    index += 1
                setattr(self, name, value)

    def pack(self):
        l = [ self._fmt ]
        for name, count in self._members:
            if name:
                value = getattr(self, name)
                if count:
                    l += value
                else:
                    l.append(value)
            else:
                if count:
                    l += [ 0 ] * count
                else:
                    l.append(0)
        # print l, type(self)
        return apply(struct.pack, l)

    def items(self):
        l = []
        for name, count in self._members:
            if name:
                l.append((name, getattr(self, name)))
        return l

    def dump(self):
        print type(self)
        print self._fmt
        for name, value in self.items():
            if type(value) == int or type(value) == long:
                value = "0x%08x" % value
            else:
                value = repr(value)
            print "%-20s: %s" % (name, value)

    def update(self, d):
        for k, v in d.items():
            setattr(self, k, v)

    def clear(self):
        self.unpack('\0' * self.calcsize())
