import logging
import time
from ft232.spi import SPI
from spi_flash.command import NOR_flash_command, Command_MX
MX25V8025F = 0xC22314


class Flash_spi(SPI):

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

    def WriteRead(self, bdata=b'', inlen=0):
        if self.isOpen():
            inbytes = self.SPI_WriteRead(bdata, inlen)
            return inbytes
        else:
            logging.error('device off line')


class Flash(Flash_spi):

    def __init__(self, speed, mode):
        Flash_spi.__init__(self, speed, mode)
        self.start()

    def flash_probe(self):
        bid = self.WriteRead(bytes([NOR_flash_command.RDID]), inlen=5)
        # print(bid.hex())
        # print([hex(i) for i in bid])
        if bid[:3] == bytes([0xc2, 0x23, 0x14]):
            self.command_set = Command_MX
            self.flashtype = 'MX25V8035'
        else:
            self.flashtype = None
        logging.info('flash detected : %s' % self.flashtype)

    def flash_read_status(self):
        bstatus = self.WriteRead(bytes([self.command_set.RD_STATUS_REG]), 1)
        logging.debug('status: %d' % bstatus[0])
        return bstatus[0]

    def flash_read_security_register(self):
        bstatus = self.WriteRead(bytes([self.command_set.RD_SECURITY_REG]), 1)
        logging.debug('security status: %d' % bstatus[0])
        return bstatus[0]

    def write_enable(self):
        self.WriteRead(bytes([self.command_set.WRITE_ENABLE]))

    def write_disable(self):
        self.WriteRead(bytes([self.command_set.WRITE_DISABLE]))

    def write_isenabled(self):
        return self.flash_read_status() & (1 << self.command_set.shift_WEL)

    def write_in_progress(self):
        return self.flash_read_status() & (1 << self.command_set.shift_WIP)

    def erase_fail(self):
        return self.flash_read_security_register() & (1 << self.command_set.shift_E_FAIL)

    def program_fail(self):
        return self.flash_read_security_register() & (1 << self.command_set.shift_P_FAIL)

    def flash_write_status(self, status):
        pass

    def flash_read(self, start, length):
        burst_limit = 0x400
        inlist = []
        while length:
            logging.info('read: 0x%0x' % (start))
            burst = burst_limit if length > burst_limit else length
            bread_cmd = bytes([self.command_set.READ]) + \
                start.to_bytes(3, 'big')
            inbytes = self.WriteRead(bread_cmd, burst)
            start += burst
            length -= burst
            inlist.append(inbytes)
        return b''.join(inlist)

    def write_page(self, address, bdata, timeout=100):
        logging.info('program: 0x%0x' % (address))
        bdata = bdata[:self.command_set.PAGESIZE]
        self.write_enable()
        if not self.write_isenabled():
            return False
        write_cmd = bytes([self.command_set.PAGE_PROGRAM]) + \
            address.to_bytes(3, 'big') + bdata
        self.WriteRead(write_cmd)
        t = time.time()
        while time.time() - t < timeout / 1000:
            if not self.write_in_progress():
                break
        if self.program_fail():
            logging.error('program page fail : 0x%x' % address)
            return False
        else:
            return True

    def flash_write(self, address, bdata, timeout=100):
        address = address & 0xffffff & ~(self.command_set.PAGESIZE - 1)
        erase_addr = address & 0xff000
        erase_end = (address + len(bdata) - 1) & 0xff000
        while erase_end >= erase_addr:
            if self.flash_sector_erase(erase_addr):
                erase_addr += 0x1000
            else:
                return False
        while bdata:
            bpage, bdata = bdata[:self.command_set.PAGESIZE], bdata[
                self.command_set.PAGESIZE:]
            if not self.write_page(address, bpage):
                return False
            address += 0x100
        return True

    def flash_random_write(self, address, bdata):
        page_address = address & 0xffffff & ~(self.command_set.PAGESIZE - 1)
        page_end = (address + len(bdata) -
                    1) & 0xffffff & ~(self.command_set.PAGESIZE - 1)

        bflashdata = self.flash_read(page_address, (page_end - page_address) +
                                     self.command_set.PAGESIZE)
        bnewdata = bflashdata[:address - page_address] +\
            bdata +\
            bflashdata[address - page_address + len(bdata):]
        if not self.flash_write(page_address, bnewdata):
            return False
        breadpages = self.flash_read(page_address, len(bnewdata))
        if bnewdata != breadpages:
            logging.error('random write fail')
            return False

    def flash_sector_erase(self, address, timeout=1000):
        logging.info('sector erase...')
        return self.flash_erase(address, self.command_set.SECTOR_ERASE, timeout)

    def flash_32kblock_erase(self, address, timeout=500):
        logging.info('32kblock erase...')
        return self.flash_erase(address, self.command_set.BLOCK_ERASE_32K, timeout)

    def flash_block_erase(self, address, timeout=1000):
        logging.info('block erase...')
        return self.flash_erase(address, self.command_set.BLOCK_ERASE_64K, timeout)

    def flash_erase(self, address, erase_cmd, timeout):
        logging.info('erase : 0x%X' % address)
        self.write_enable()
        if not self.write_isenabled():
            return False
        self.WriteRead(bytes([erase_cmd]) + address.to_bytes(3, 'big'))
        t = time.time()
        while time.time() - t < timeout / 1000:
            if not self.write_in_progress():
                break
        if self.erase_fail():
            logging.error('erase fail')
            return False
        else:
            return True
