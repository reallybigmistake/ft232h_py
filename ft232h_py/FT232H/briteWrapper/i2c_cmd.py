from ft232.i2c import I2C
import logging
import time
import sys


class I2C_wrap(I2C):

    def __init__(self, speed, slave, regaddr):
        self.description = b'Single RS232-HS'
        self.speed = speed
        self.slave = slave
        self.regaddr = regaddr

    def start(self):
        I2C.__init__(self, self.description)
        self.i2c_config()
        self.set_clock(self.speed)

    def stop(self):
        if self.isOpen():
            self.close()

    def isOpen(self):
        return self.mmpsse_loopback()

    def read(self, inlen, timeout=100):
        if self.isOpen():
            return self.i2c_FastRead(self.slave, self.regaddr, inlen, timeout=timeout)
        else:
            logging.error('device off line')

    def read_brite(self, inlen, timeout=100):
        if self.isOpen():
            return self.i2c_FastRead_brite(self.slave, inlen, timeout=timeout)
        else:
            logging.error('device off line')

    def write(self, bdata, isHex=False):
        if self.isOpen():
            self.i2c_FastWrite(self.slave, self.regaddr, bdata)
        else:
            logging.error('device off line')

    def write_brite(self, bdata, isHex=False):
        if self.isOpen():
            self.i2c_FastWrite_Brite(self.slave, bdata)
            logging.debug('i2c transfer %s' % bdata.hex())
        else:
            logging.error('device off line')


def writeBytes(speed, slave_addr, regaddr, bdata):
    i2c = I2C_wrap(speed, slave_addr, regaddr)
    i2c.start()
    i2c.write(bdata)
    i2c.stop()


def writeBytes_brite(speed, slave_addr, regaddr, bdata):
    i2c = I2C_wrap(speed, slave_addr, 0)
    i2c.start()
    i2c.write_brite(bytes([0x01, regaddr, 0x00, 0x00, 0x00]))
    i2c.write_brite(bytes([0x00]) + bdata)
    i2c.stop()


def setBit_Brite(speed, slave_addr, regaddr, offset):
    bret = read4Bytes_Brite(speed, slave_addr, regaddr)
    num = int.from_bytes(bret, 'little')
    bnum = (num | (1 << offset)).to_bytes(4, 'little')
    writeBytes_brite(speed, slave_addr, regaddr, bnum)


def setBits_Brite(speed, slave_addr, regaddr, offsets):
    bret = read4Bytes_Brite(speed, slave_addr, regaddr)
    num = int.from_bytes(bret, 'little')
    for offset in offsets:
        num = num | (1 << offset)
    bnum = num.to_bytes(4, 'little')
    writeBytes_brite(speed, slave_addr, regaddr, bnum)


def clearBit_Brite(speed, slave_addr, regaddr, offset):
    bret = read4Bytes_Brite(speed, slave_addr, regaddr)
    num = int.from_bytes(bret, 'little')
    bnum = (num & ~(1 << offset)).to_bytes(4, 'little')
    writeBytes_brite(speed, slave_addr, regaddr, bnum)


def clearBits_Brite(speed, slave_addr, regaddr, offsets):
    bret = read4Bytes_Brite(speed, slave_addr, regaddr)
    num = int.from_bytes(bret, 'little')
    for offset in offsets:
        num = num & ~(1 << offset)
    bnum = num.to_bytes(4, 'little')
    writeBytes_brite(speed, slave_addr, regaddr, bnum)


def readBytes(speed, slave_addr, regaddr, inlen):
    i2c = I2C_wrap(speed, slave_addr, regaddr)
    i2c.start()
    indata = i2c.read(inlen)
    i2c.stop()
    return indata


def readBytes_Brite(speed, slave_addr, regaddr, inlen, regaddrbytes=4):
    i2c = I2C_wrap(speed, slave_addr, 0)
    i2c.start()
    i2c.write_brite(bytes([0x01]) + regaddr.to_bytes(regaddrbytes, 'little'))
    ret = i2c.read_brite(inlen)
    i2c.stop()
    return ret


def read4Bytes_Brite(speed, slave_addr, regaddr, num4bytes=1):
    bret = readBytes_Brite(speed, slave_addr, regaddr, num4bytes * 4)
    return bret


def readBit_Brite(speed, slave_addr, regaddr, offset):
    bret = read4Bytes_Brite(speed, slave_addr, regaddr)
    num = int.from_bytes(bret, 'little')
    return num >> offset & 0x01


def readBits_Brite(speed, slave_addr, regaddr, offsets):
    bitvals = []
    bret = read4Bytes_Brite(speed, slave_addr, regaddr)
    num = int.from_bytes(bret, 'little')
    for offset in offsets:
        bitvals.append(num >> offset & 0x01)
    return bitvals


def loadfile(infile, outfile):
    pass


if __name__ == '__main__':
    writeBytes_brite(400000, 0x82 >> 1, 0x80, b'\xff\xff\xff\xff')
    ret = readBytes_Brite(400000, 0x82 >> 1, 0xc4, 4)
    ret = read4Bytes_Brite(400000, 0x82 >> 1, 0xc4)
    setBit_Brite(400000, 0x82 >> 1, 0x80, 0)
    ret = readBit_Brite(400000, 0x82 >> 1, 0x80, 0)
    print(ret)
    clearBit_Brite(400000, 0x82 >> 1, 0x80, 0)
    ret = readBit_Brite(400000, 0x82 >> 1, 0x80, 0)
    print(ret)
