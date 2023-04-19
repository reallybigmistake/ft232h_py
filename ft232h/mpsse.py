from ft232.wrapper import FT232
import logging
import time
from ft232.dll_h import *


class MPSSE(FT232):

    def __init__(self):
        FT232.__init__(self)

    def mpsse_open(self, **kargs):
        self.open(**kargs)
        self.config_to_mmse()

    def config_to_mmse(self):
        self.FT_ResetDevice()
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
        self.FT_SetTimeouts(100, 5000)
        self.check_status()
        self.FT_SetLatencyTimer(1)
        self.check_status()
        self.FT_SetFlowControl(FT_FLOW_RTS_CTS, 0, 0)
        self.check_status()
        self.FT_SetBitMode(0, FT_BITMODE_RESET)
        self.check_status()
        self.FT_SetBitMode(0, FT_BITMODE_MPSSE)
        self.check_status()

    def mpsse_config(self):
        pass

    def mmpsse_close(self):
        self.flushinbuff()
        self.FT_SetBitMode(0, FT_BITMODE_RESET)
        self.check_status()
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
            logging.info('flush' + self.inbytes.hex())

    def mmpsse_read(self, num, mtimeout):
        start = time.time()
        while(time.time() - start < mtimeout / 1000):
            num_in_queue = self.FT_GetQueueStatus()

            # print(num_in_queue)
            if num_in_queue >= num:
                self.FT_Read(num)
                self.check_status()
                return num
        logging.warning(f'read {num} but {num_in_queue} in queue')
        if num_in_queue:
            self.FT_Read(num_in_queue)
            self.check_status()
        else:
            logging.warning('no data in queue')
        return num_in_queue
