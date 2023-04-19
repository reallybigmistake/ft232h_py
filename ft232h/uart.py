from ft232.wrapper import FT232
import logging
import time
from ft232.dll_h import *


class UART(FT232):

    def __init__(self, description, BaudRate, Parity, ByteSize, Stopbits):
        FT232.__init__(self, description)
        self.BaudRate = BaudRate
        self.Parity = Parity
        self.ByteSize = ByteSize
        self.Stopbits = Stopbits
        self.open()
        self.config_to_uart()
        self.uart_config()

    def config_to_uart(self):
        self.FT_ResetDevice()
        self.check_status()
        self.FT_SetBitMode(0, FT_BITMODE_RESET)       
        self.check_status()

        self.FT_SetUSBParameters(65536, 65536)
        self.check_status()
        number_to_read = self.FT_GetQueueStatus()
        self.check_status()
        if number_to_read:
            number_read = self.FT_Read(number_to_read)
            logging.debug('FT_Read, %d, %d, %d' %
                          (number_read, self.status, self.inbytes))
        self.FT_SetChars(0, 0, 0, 0)
        self.check_status()
        self.FT_SetTimeouts(100, 100)
        self.check_status()
        self.FT_SetLatencyTimer(1)
        self.check_status()
        self.FT_SetFlowControl(FT_FLOW_NONE, 0, 0)
        self.check_status()

    def uart_config(self):
        self.FT_SetBaudRate(self.BaudRate)
        if self.ByteSize not in [7, 8]:
            logging.error('invalid data width')
            return False
        if self.Stopbits == 1:
            ftstopbit = FT_STOP_BITS_1
        elif self.Stopbits == 2:
            ftstopbit = FT_STOP_BITS_2
        else:
            logging.error('invalid Stopbits')
            return False
        if self.Parity in ['n', 'N']:
            ftparity = FT_PARITY_NONE
        elif self.Parity in ['O', 'o']:
            ftparity = FT_PARITY_ODD
        elif self.Parity in ['e', 'E']:
            ftparity = FT_PARITY_EVEN
        else:
            logging.error('invalid Parity')
            return False
        self.FT_SetDataCharacteristics(self.ByteSize, ftstopbit, ftparity)
        self.check_status()

    def uart_close(self):
        self.close()

    def flushinbuff(self):
        number_to_read = self.FT_GetQueueStatus()
        self.check_status()
        if number_to_read:
            number_read = self.FT_Read(number_to_read)
            if number_to_read != number_read:
                logging.warning('buffer free may fail %d in buff, but %d read' % (
                    number_to_read, number_read))
            self.check_status()
            logging.info('flush', str(self.inbytes))

    def uart_read(self, num, mtimeout=100):
        start = time.time()
        while(time.time() - start < mtimeout / 1000):
            num_in_queue = self.FT_GetQueueStatus()
            # print(num_in_queue)
            if num_in_queue >= num:
                self.FT_Read(num)
                self.check_status()
        if num_in_queue:
            self.FT_Read(num_in_queue)
            self.check_status()
        else:
            logging.warning('no data in queue')
        return self.inbytes

    def uart_readall(self):
        num_in_queue = self.FT_GetQueueStatus()
        if num_in_queue:
            self.FT_Read(num_in_queue)
            self.check_status()
        return self.inbytes

    def uart_write(self, bdata):
        num_wirtten = self.FT_Write(bdata)
        if num_wirtten != len(bdata):
            logging.warning('TX %d, %d wanted' % (num_wirtten, len(bdata)))
        self.check_status()
