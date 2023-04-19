from ft232h.wrapper import FT232
from ft232h.dll_h import *
from ft232h.spi import SPI
from ft232h.i2c import I2C


def list_info():
    dev = FT232(None)
    infos = dev.get_devinfos()
    for i in infos:
        if i['Type'] == 8:
            print(i)


def spi_test():
    spi = SPI()
    #spi speed 1M
    # spi config to mode 3
    spi.spi_open(1000000, 3, serialnum='FT0B0UCU')
    # spi write b'1234' and read back 4 bytes
    spi.SPI_WriteRead(b'1234',4)

def i2c_test():
    i2c = I2C()
    #speed 400k
    i2c.i2c_open(400000)
    # i2c write b'1234' and read back 4 bytes to slave7bitaddr 0x82
    i2c.i2c_FastWrite(0x82>>1, b'1234')
    rec = i2c.i2c_FastRead(0x82>>1, 4)
    print(rec)

if __name__ == '__main__':
    #list_info()
    #spi_test()
    i2c_test()
