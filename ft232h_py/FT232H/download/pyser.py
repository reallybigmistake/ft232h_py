import serial
import sys
import logging
import time


class UART_downloader:

    def __init__(self, COM, baudrate=115200, stopbits=1, bytesize=8, parity='N', rtscts=False):
        self.COM = COM
        self.baudrate = baudrate
        self.stopbits = stopbits
        self.bytesize = bytesize
        self.parity = parity
        self.rtscts = rtscts
        self.realclk = baudrate
        self.timeout = 0.2

    def start(self):
        self.ser = serial.Serial(self.COM, baudrate=self.baudrate,
                                 stopbits=self.stopbits, bytesize=self.bytesize,
                                 parity=self.parity, rtscts=self.rtscts,
                                 timeout=self.timeout)

    def stop(self):
        if self.ser and isinstance(self.ser, serial.Serial):
            self.ser.close()

    def reconfig(self, baudrate):
        self.stop()
        self.ser = serial.Serial(self.COM, baudrate=baudrate,
                                 stopbits=self.stopbits, bytesize=self.bytesize,
                                 parity=self.parity, rtscts=self.rtscts,
                                 timeout=self.timeout)
        # print(self.ser)

    def isOpen(self):
        if self.ser:
            return self.ser.isOpen()
        else:
            return False

    def read(self, inlen, timeout=None):
        if self.isOpen():
            return self.ser.read(size=inlen)
        else:
            logging.error('device off line')
    def readall(self, timeout=0):
        if self.isOpen():
            t1 = time.time()
            bdata = self.ser.readall()
            while time.time() < t1 + timeout:
                bdata += self.ser.readall()
            return bdata
        else:
            logging.error('device off line')

    def write(self, bdata, isHex=False):
        if self.isOpen():
            self.ser.write(bdata)
        else:
            logging.error('device off line')
