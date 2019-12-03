# coding=utf-8
from ctypes import *
from ft232.dll_h import *
import time
import logging


class FT232:

    def __init__(self, description):
        self.description = description
        self.ft232 = windll.LoadLibrary('ftd2xx.dll')
        self.handle = None

    def open(self):
        self.FT_OpenEx_ByDesc(self.description)
        if not self.status:
            logging.debug('device %s open successfully' % (self.description))
        else:
            raise FT_Exception('FT_Open fail', STATUS(self.status))

    def close(self):
        self.FT_Close()
        if not self.status:
            logging.debug('device %s close successfully' % self.description)
        else:
            raise FT_Exception('FT_Close fail', STATUS(self.status))

    def FT_ListDevices(self):
        num = c_int()
        self.status = self.ft232.FT_ListDevices(
            byref(num), None, FT_LIST_NUMBER_ONLY)
        return (self.status, num.value)

    def FT_CreateDeviceInfoList(self):
        num = c_int()
        self.status = self.ft232. FT_CreateDeviceInfoList(byref(num))
        return num

    def FT_GetDeviceInfoList(self):
        infos = []
        num = c_int()
        nodes = (FT_DEVICE_LIST_INFO_NODE * 8)()
        pDest = nodes
        self.status = self.ft232. FT_GetDeviceInfoList(
            pDest, byref(num))
        for i in range(num.value):
            infos.append(pDest[i])
        return infos

    def FT_Open(self, iDevice):
        handle = FT_HANDLE()
        self.status = self.ft232.FT_Open(iDevice, byref(handle))
        self.handle = handle

    def FT_Close(self):
        self.status = self.ft232.FT_Close(self.handle)

    def FT_OpenEx_ByDesc(self, Desc):
        handle = FT_HANDLE()
        self.status = self.ft232.FT_OpenEx(
            Desc, FT_OPEN_BY_DESCRIPTION, byref(handle))
        self.handle = handle

    def FT_SetBaudRate(self, speed):
        self.status = self.ft232.FT_SetBaudRate(self.handle, speed)

    def FT_SetDataCharacteristics(self, uWordLength, uStopBits, uParity):
        uWordLength = c_char(uWordLength)
        uStopBits = c_char(uStopBits)
        uParity = c_char(uParity)
        self.status = self.ft232.FT_SetDataCharacteristics(self.handle,
            uWordLength, uStopBits, uParity)

    def FT_GetQueueStatus(self):
        amountInRxQueue = c_int()
        self.status = self.ft232.FT_GetQueueStatus(
            self.handle, byref(amountInRxQueue))
        return amountInRxQueue.value

    def FT_GetComPortNumber(self):
        ComPortNumber = c_int()
        self.status = self.ft232.FT_GetComPortNumber(
            self.handle, byref(ComPortNumber))
        return ComPortNumber.value

    def echostruct(self, tar):
        for name, value in tar._fields_:
            if name == 'ftHandle':
                if getattr(tar, name):
                    print(name, hex(getattr(tar, name)), end=';')
                else:
                    print(name, getattr(tar, name), end=';')
            else:
                print(name, getattr(tar, name), end=';')
        print()

    def FT_GetDeviceInfo(self):
        fttype = c_int()
        devid = c_int()
        serialnum = (c_char * 16)()
        description = (c_char * 64)()
        dummy = None
        self.status = self.ft232.FT_GetDeviceInfo(self.handle, byref(
            fttype), byref(devid), serialnum, description, dummy)
        # print(fttype.value, devid.value, serialnum.value, description.value)
        return (fttype.value, devid.value, serialnum.value, description.value)

    def FT_GetStatus(self):
        AmountInRxQueue = c_int()
        AmountInTxQueue = c_int()
        EventStatus = c_int()
        self.status = self.ft232.FT_GetStatus(self.handle, byref(
            AmountInRxQueue), byref(AmountInTxQueue), byref(EventStatus))
        return AmountInRxQueue.value, AmountInTxQueue.value, EventStatus.value

    def FT_ResetDevice(self):
        self.status = self.ft232.FT_ResetDevice(self.handle)

    def FT_SetTimeouts(self, ReadTimeout, WriteTimeout):
        # timeout in ms
        self.status = self.ft232.FT_SetTimeouts(
            self.handle, ReadTimeout, WriteTimeout)

    def FT_SetUSBParameters(self, InTransferSize, wOutTransferSize):
        self.status = self.ft232.FT_SetUSBParameters(
            self.handle, InTransferSize, wOutTransferSize)

    def FT_SetLatencyTimer(self, ucTimer):
        ucTimer = c_char(ucTimer)
        self.status = self.ft232.FT_SetLatencyTimer(self.handle, ucTimer)

    def FT_GetLatencyTimer(self, ucTimer):
        # ucTimer 2-255 (ms)
        self.status = self.ft232.FT_GetLatencyTimer(self.handle, ucTimer)

    def FT_SetFlowControl(self, usFlowControl, uXon, uXoff):
        uXon = c_char(uXon)
        uXoff = c_char(uXoff)
        self.status = self.ft232.FT_SetFlowControl(
            self.handle, usFlowControl, uXon, uXoff)

    def FT_SetBitMode(self, ucMask, ucMode):
        # print(ucMask, ucMode)
        # ucMask c_char
        # ucMode c_char
        ucMask = c_char(ucMask)
        ucMode = c_char(ucMode)
        self.status = self.ft232.FT_SetBitMode(self.handle, ucMask, ucMode)
        logging.debug('FT_SetBitMode :' + str(ucMask) + str(ucMode))

    # def FT_GetBitMode(self):
    #     mode = c_char()
    #     self.status = self.ft232.FT_GetBitmode(self.handle, bref(mode))
    #     return mode.value

    def FT_SetChars(self, uEventCh, uEventChEn, uErrorCh, uErrorChEn):
        uEventCh = c_char(uEventCh)
        uEventChEn = c_char(uEventChEn)
        uErrorCh = c_char(uErrorCh)
        uErrorChEn = c_char(uErrorChEn)
        self.status = self.ft232.FT_SetChars(self.handle, uEventCh, uEventChEn,
                                             uErrorCh, uErrorChEn)

    def FT_Read(self, dwBytesToRead):
        lpBuffer = create_string_buffer(dwBytesToRead)
        BytesReturned = c_int()
        self.ft232.FT_Read(self.handle, lpBuffer, dwBytesToRead,
                           byref(BytesReturned))
        self.inbytes = lpBuffer.raw
        return BytesReturned.value

    def FT_Write(self, outbytes):
        BytesWritten = c_int()
        self.status = self.ft232.FT_Write(self.handle, outbytes, len(outbytes),
                                          byref(BytesWritten))
        logging.debug('FT_Write :' + str(outbytes))
        return BytesWritten.value

    def check_status(self, msg=''):
        if self.status:
            logging.warning(str(msg) + str(STATUS(self.status)))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s')