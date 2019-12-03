# coding=utf-8
from download.dloader import Dloader
from download.serdloader import serDloader
from download.interface import I2C_downloader
from download.interface import SPI_downloader
from download.interface import UART_downloader
from download.pyser import UART_downloader as ser_downloader
from ui.downloadGUI import DownloadFrame, UartSetFrame, AutoDownload
from tkinter import *

from ft232.uart import UART
import logging
import time
from ft232.spi import SPI
# dev = I2C_downloader(1000000, 0x12, 0x55)
# spi = SPI(b'Single RS232-HS')
# spi.set_clock(1000000)
# spi.spi_config(mode=1)
# # res = spi.SPI_Read(1)
# res = spi.SPI_Write(b'\x12')

# print(res)
# spi.close()


def spi_boot():
    dev = SPI_downloader(speed=200000, mode=1)
    f = 'dsp_cdl.nonsec.bin'
    dl = Dloader(f, dev)
    t1 = time.time()
    dl.boot()
    t = time.time() - t1
    print('total %0.2fs' % t)


def tmp():
    spi = SPI(b'Single RS232-HS')
    spi.set_clock(100000)
    spi.spi_config(mode=1)
    # res = spi.SPI_Read(1)
    res = spi.SPI_Write(b'\x12')
    print(spi.realclk)
    print(res)
    spi.close()


def uart_test():
    uart = UART(b'Single RS232-HS', 1000000, 'n', 7, 1)
    uart.uart_write(b'\x55\x11\x22\x33\x44\x55\xaa\xaa\xaa')
    uart.uart_close()
# uart_test()


def uart_boot():
    dev = UART_downloader(speed=1000000)
    f = 'dsp_cdl.nonsec.bin'
    dl = Dloader(f, dev)
    t1 = time.time()
    dl.boot()
    t = time.time() - t1
    print('total %0.2fs' % t)


def pyser_boot():
    dev = ser_downloader(COM='com20')
    f = 'dsp_cdl_v2_1.nonsec.bin'
    dl = serDloader(f, dev, 3000000)
    t1 = time.time()
    dl.boot()
    t = time.time() - t1
    logging.info('total %0.2fs' % t)


def ui_boot():
    root = Tk()
    dl = DownloadFrame(root)
    logging.basicConfig(level=logging.ERROR, stream=dl.textIO,
                        format='%(asctime)s - %(message)s')
    mainloop()


def test():
    root = Tk()
    AutoDownload(root).mainloop()
if __name__ == '__main__':
    ui_boot()
