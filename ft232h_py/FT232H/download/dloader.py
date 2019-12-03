import time
import logging
import sys
from download import header
from download import crc16
DEV = 0x12
REGADDR = 0x55
MAJOR_VER = 0
MINOR_VER = 1


def mdelay(ms):
    time.sleep(ms / 1000)


class Dloader:

    def __init__(self, infile, downloader, speed):
        self.infile = infile
        self.downloader = downloader
        self.speed = speed
        self.downloadstage = ''
        self.progress = 0
        self.callback = lambda self, x: x

    def inProgress(self, *args):
        self.callback(*args)

    def configProgFunc(self, callback):
        self.callback = callback

    def send_setconfig(self, **kwargs):
        pass

    def send_handshake(self):
        shakecmd = 0x7e010000a55a
        cmdcrc16 = crc16.crc_ccitt(0x0000, shakecmd.to_bytes(6, 'big'))
        bcrc = cmdcrc16.to_bytes(2, 'little')
        shakebytes = shakecmd.to_bytes(6, 'big') + bcrc
        logging.debug('handshake send:' + shakebytes.hex().upper())
        self.downloader.write(shakebytes)

    def send_datapkt(self, buff, pkt_id):
        print('buff_high', len(buff) >> 8, 'buff_low', len(buff) & 0xff)
        pkg_start = bytes([0x7e, 0x02, len(buff) & 0xff, len(buff) >> 8])
        pkg_end = bytes([pkt_id & 0xff, pkt_id >> 8, 0, 0])
        pkg_mem = buff
        pkg = pkg_start + pkg_mem + (pkg_end)
        self.downloader.write(pkg)
        logging.info('pkg start:' + pkg_start.hex())
        logging.info('pkg end:' + pkg_end.hex())

    def get_status(self):
        recvbytes = self.downloader.read(8)
        # print(recvbytes)
        if not recvbytes:
            logging.error('no recv data')
            sys.exit()
        status = hex(int.from_bytes(recvbytes[4:6], 'little'))
        logging.info('status:' + status)
        logging.info('data received:' + recvbytes.hex())
        return status

    def setconfig(self):
        pass

    def boot(self):
        self.downloader.start()
        logging.info('baudrate %d', self.downloader.realclk)
        try:
            self.fwbin = open(self.infile, 'rb').read()
            self.bheader = header.BytesAnalyse(self.fwbin)
            self.bmem = self.fwbin[header.IMG_HDR_SIZE:]
        except FileNotFoundError:
            logging.error('file not found')
            self.downloader.close()
            sys.exit()

        self.send_handshake()
        mdelay(800)
        para = self.get_status()
        if int(para, 16) != 0x1:
            logging.error('handshake fail')
            self.downloader.stop()
            sys.exit()
        logging.info("device version:{}".format(para))
        # re-configurate
        self.setconfig()

        self.send_datapkt(self.fwbin[:header.IMG_HDR_SIZE], 0)
        mdelay(10)
        para = self.get_status()
        if int(para, 16):
            logging.error('image header')
            self.downloader.stop()
            sys.exit()
        mdelay(2)

        area_num = int.from_bytes(self.bheader.bimage_numofmemarea, 'little')
        logging.debug('area_num: %d\narea_num_bytes:%s' %
                      (area_num, repr(self.bheader.bimage_numofmemarea)))

        if not area_num:
            logging.error('invalid area_num')
            sys.exit()

        for i in range(area_num):
            logging.info('sec:{}'.format(i))
            # for GUI
            self.stage = 'dsp0 sec:{}'.format(i)
            bisec = self.bheader.blmemarea[i]
            len_bytes = header.getmembytes(bisec, header.img_memarea, 'length')
            sec_len = int.from_bytes(len_bytes, 'little')

            logging.info('section len:%d' % sec_len)
            total_send = sec_len
            while sec_len > 0:
                pkt_len = sec_len if sec_len < header.IMG_PKT_MAXLEN else header.IMG_PKT_MAXLEN
                bsec_mem, self.bmem = self.bmem[:pkt_len], self.bmem[pkt_len:]
                self.send_datapkt(bsec_mem, i)
                mdelay(10)
                para = self.get_status()

                logging.debug('sec num:%d' % (i))
                logging.debug('pkt_len:%d' % (pkt_len))

                logging.debug('dsp0 total send:0x%x' % (total_send))
                if int(para, 16) != i:
                    logging.error('send pkt {} fail'.format(i))
                    sys.exit()
                    logging.info('.')
                sec_len -= pkt_len
                # for GUI
                self.progress = (total_send - sec_len) / total_send * 100
                self.inProgress(self.stage, self.progress)
        mdelay(100)
        dsp1_addr = int.from_bytes(self.bheader.dsp1_load_addr, 'little')
        dsp1_len = int.from_bytes(self.bheader.dsp1_load_len, 'little')
        if dsp1_addr and dsp1_len:
            logging.info('dsp1_load_addr:' + hex(dsp1_addr) + '\t'
                         'dsp1_load_len:' + hex(dsp1_len))
            if len(self.fwbin) < dsp1_len:
                self.bdsp1mem = self.fwbin + bytes(dsp1_len - len(self.fwbin))
            else:
                self.bdsp1mem = self.fwbin
            # for GUI
            self.stage = 'dsp1'
            total_send = dsp1_len

            while dsp1_len > 0:
                pkt_len = dsp1_len if dsp1_len < header.IMG_PKT_MAXLEN else header.IMG_PKT_MAXLEN
                bsec_mem, self.bdsp1mem = self.bdsp1mem[
                    :pkt_len], self.bdsp1mem[pkt_len:]
                self.send_datapkt(bsec_mem, area_num)
                mdelay(2)
                para = self.get_status()

                logging.debug('sec num:%d' % (area_num))
                logging.debug('pkt_len:%d' % (pkt_len))
                total_send += pkt_len
                logging.info('dsp1 total send:0x%x' % (total_send))
                if int(para, 16) != area_num:
                    logging.error('send pkt {} fail'.format(area_num))
                    sys.exit()
                    logging.info('.')
                dsp1_len -= pkt_len
                # for GUI
                self.progress = (total_send - dsp1_len) / total_send * 100
                self.inProgress(self.stage, self.progress)

        self.downloader.stop()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s')
    f = 'dsp_cdl.nonsec.bin'
    downloader = Dloader(DEV, 100000, f)
    downloader.boot()
