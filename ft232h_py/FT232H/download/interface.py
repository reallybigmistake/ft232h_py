from ft232.i2c import I2C
from ft232.spi import SPI
from ft232.uart import UART
import logging
import time


class I2C_downloader(I2C):

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

    def write(self, bdata, isHex=False):
        if self.isOpen():
            self.i2c_FastWrite(self.slave, self.regaddr, bdata)
        else:
            logging.error('device off line')


class SPI_downloader(SPI):

    def __init__(self, speed, mode):
        self.description = b'Single RS232-HS'
        self.speed = speed
        self.mode = mode

    def start(self):
        SPI.__init__(self, self.description)
        self.spi_config(self.mode)
        self.set_clock(self.speed)

    def stop(self):
        if self.isOpen():
            self.close()

    def isOpen(self):
        return self.mmpsse_loopback()

    def read(self, inlen, timeout=100):
        if self.isOpen():
            return self.SPI_Read(inlen, timeout=timeout)
        else:
            logging.error('device off line')

    def write(self, bdata, isHex=False):
        if self.isOpen():
            self.SPI_Write(bdata)
        else:
            logging.error('device off line')


class UART_downloader(UART):

    def __init__(self, speed, Parity='n', ByteSize=8, Stopbits=1):
        self.description = b'Single RS232-HS'
        self.BaudRate = speed
        self.Parity = Parity
        self.ByteSize = ByteSize
        self.Stopbits = Stopbits
        self.realclk = speed

    def start(self):
        UART.__init__(self, self.description, self.BaudRate,
                      self.Parity, self.ByteSize, self.Stopbits)

    def stop(self):
        if self.isOpen():
            self.close()

    def isOpen(self):
        self.FT_GetDeviceInfo()
        if self.status:
            return False
        else:
            return True

    def read(self, inlen, timeout=100):
        if self.isOpen():
            return self.uart_read(inlen, mtimeout=timeout)
        else:
            logging.error('device off line')
            

    def write(self, bdata, isHex=False):
        if self.isOpen():
            self.uart_write(bdata)
        else:
            logging.error('device off line')
