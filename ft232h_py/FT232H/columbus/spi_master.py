import time
import random
import sys
from ft232.spi import SPI
from columbus.data_format import bytesToSPI


def printbytes(bdata, bytesinline=16):
    numlist = [hex(i) for i in bdata]
    while numlist:
        line, numlist = numlist[:bytesinline], numlist[bytesinline:]
        print(line)


def formatbytes(bdata, bytesinline=16):
    numlist = [hex(i) for i in bdata]
    out = ''
    while numlist:
        line, numlist = numlist[:bytesinline], numlist[bytesinline:]
        out += ' '.join(line)+'\n'
    out += '\n'
    return out


def waitslave(bsub):
    com = UART_downloader('com40')
    com.start()
    bdata = com.readuntil(bsub, timeout=0.5)
    com.stop()
    if bsub in bdata:
        return True
    else:
        print('slave console:')
        printbytes(bdata)
        return False


class master_spi(SPI):
    def __init__(self, clock, mode, bitlen):
        SPI.__init__(self, b'Single RS232-HS')
        self.spi_config(clock, mode, bitlen)

    def spi_package_write(self, bdata):
        self.SPI_Write(bdata)

    def spi_package_read(self, inlen):
        return self.SPI_Read(inlen)

    def close_master(self):
        self.mmpsse_close()

class master_spi_bit(SPI):
    def __init__(self, clock, mode, bitlen):
        SPI.__init__(self, b'Single RS232-HS')
        self.spi_config(clock, mode, bitlen)

    def spi_package_write(self, bdata):
        self.SPI_Write_bits(bdata)

    def spi_package_read(self, inlen):
        return self.SPI_Read_bits(inlen)

    def close_master(self):
        self.mmpsse_close()


def mdelay(msecs):
    time.sleep(msecs/1000)


def generate_spi_cmd(bitlen, cmd, tid, rid, length):
    if bitlen <= 8:
        Bcmd = bytes([cmd & 0x03,
                    tid & 0x03 | (rid & 0x03) << 2,
                    (length >> 20) & 0x0f,
                    (length >> 16) & 0x0f,
                    (length >> 12) & 0x0f,
                    (length >> 8) & 0x0f,
                    (length >> 4) & 0x0f,
                    (length >> 0) & 0x0f,
                    ])

    elif bitlen <= 16:
        Bcmd = bytes([0,
                    (cmd & 0x03) | ((tid&3)<<2) | ((rid&3)<<4),
                    0,
                    (length >> 16) & 0xff,
                    0,
                    (length >> 8) & 0xff,
                    0,
                    (length >> 0) & 0xff,
                    ])
    else:
        Bcmd = bytes([0,
                    0,
                    (length >> 16) & 0xff,
                    (cmd & 0x03) | ((tid&3)<<2) | ((rid&3)<<4),                    
                    0,
                    0,
                    (length >> 0) & 0xff,
                    (length >> 8) & 0xff,
                    ])
    return Bcmd


def spi_master(clock, mode, length, repeat=1):
    master = master_spi(clock, mode, bitlen=8)
    for i in range(repeat):
        # Bdata = bytes([random.randint(0, 0xff) for i in range(length)])
        Bdata = bytes([0xAA for i in range(length)])
        outcmd = generate_spi_cmd(8, 1, 0, 0, len(Bdata))
        master.spi_package_write(outcmd)
        mdelay(3)
        master.spi_package_write(Bdata)
        mdelay(3)
        incmd = generate_spi_cmd(8, 0, 0, 0, len(Bdata))
        master.spi_package_write(incmd)
        mdelay(5)
        Bindata = master.spi_package_read(len(Bdata))
        # print(Bindata)
        if Bdata != Bindata:

            print('Bdata:')
            printbytes(Bdata)
            print('Bindata:')
            printbytes(Bindata)
            print('%s repeat :%d test fail' %
                  (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), i))
            master.close_master()
            return i+1
        else:
            if (i+1) % 100 == 0:
                print(i+1)
    print()
    master.close_master()
    return repeat

def spi_master2(clock, mode, bus_width, length, repeat=1):
    master = master_spi_bit(clock, mode, bus_width)
    if bus_width <= 8:
        word_width = 1
    elif bus_width <= 16:
        word_width = 2
    else:
        word_width = 4
    for i in range(repeat):
        Bdata = bytes([random.randint(0, 0xff) for i in range(length * word_width)])
        # Bdata = bytes([0x11, 0x11, 0x22, 0x22, 0x33, 0x33, 0x44, 0x44])
        outcmd = generate_spi_cmd(bus_width, 1, 0, 0, len(Bdata))
        master.spi_package_write(outcmd)
        mdelay(3)
        
        master.spi_package_write(Bdata)
        
        mdelay(3)
        incmd = generate_spi_cmd(bus_width, 0, 0, 0, len(Bdata))
        master.spi_package_write(incmd)
        mdelay(5)
        Bindata = master.spi_package_read(length)

        if bytesToSPI(Bdata, master.bus_width) != Bindata:

            print('Bdata:')
            printbytes(Bdata)
            print('Bindata:')
            printbytes(Bindata)
            print('%s repeat :%d test fail' %
                  (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), i))
            master.close_master()
            return i+1
        else:
            if (i+1) % 100 == 0:
                print(i+1)
    print()
    master.close_master()
    return repeat
def spi_send(clock, mode, bitlen, bdata):
    master = master_spi(clock, mode, bitlen)
    master.SPI_Write_bits(bdata)
    master.close_master()

