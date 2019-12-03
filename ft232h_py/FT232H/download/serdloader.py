import logging
import sys
from download import header
from download import crc16
from download.dloader import Dloader, mdelay


class serDloader(Dloader):

    def __init__(self, infile, downloader, speed):
        Dloader.__init__(self, infile, downloader, speed)

    def send_setconfig(self, **kwargs):
        bsetcmd = 0x7e030010.to_bytes(4, 'big')
        bspeed = kwargs['speed'].to_bytes(4, 'little')

        bblank = bytes(14)
        cmdcrc16 = crc16.crc_ccitt(0x0000, bsetcmd + bspeed + bblank)
        bcrc = cmdcrc16.to_bytes(2, 'little')
        cmdbytes = bsetcmd + bspeed + bblank + bcrc
        logging.debug('set config send:' + cmdbytes.hex().upper())
        self.downloader.write(cmdbytes)

    def setconfig(self):
        self.send_setconfig(speed=self.speed)
        mdelay(10)
        para = self.get_status()
        if int(para, 16) != 0x0:
            logging.error('setconfig fail')
            self.downloader.stop()
            sys.exit()
        logging.info("device version:{}".format(para))

        self.downloader.reconfig(baudrate=self.speed)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s')
    f = 'dsp_cdl.nonsec.bin'
    downloader = Dloader(DEV, 100000, f)
    downloader.boot()
