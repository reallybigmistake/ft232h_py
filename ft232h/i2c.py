from ft232.mpsse import MPSSE
from ft232.dll_h import *
import logging


class I2C(MPSSE):

    def __init__(self, **kwargs):
        MPSSE.__init__(self)

    def i2c_open(self, clock, **kwargs):
        self.mpsse_open(**kwargs)
        self.set_clock(clock)
        self.i2c_config()

    def set_clock(self, clock):
        clock = clock * 3 / 2
        # <=6M
        if clock <= 6000000:
            self.FT_Write(bytes([ENABLE_CLOCK_DIVIDE]))
            self.check_status()
            div = int(6000000 / clock) - 1
            self.realclk = 6000000 / (1 + div) / 3 * 2
        # >6M
        else:
            self.FT_Write(bytes([DISABLE_CLOCK_DIVIDE]))
            self.check_status()
            div = int(30000000 / clock) - 1
            self.realclk = 30000000 / (1 + div) / 3 * 2
        setclkcmd = bytes([
            SET_CLOCK_FREQUENCY_CMD,
            div & 0xff,
            div >> 8,
        ])
        self.FT_Write(setclkcmd)
        self.check_status()

    def i2c_config(self):
        # set i2c clock phase
        self.FT_Write(bytes([MPSSE_CMD_ENABLE_3PHASE_CLOCKING]))
        # enable tristate
        sda_in_out_set = bytes([
            MPSSE_CMD_ENABLE_DRIVE_ONLY_ZERO,
            0x02,
            0x00,
        ])
        self.FT_Write(sda_in_out_set)
        # set dirction
        gpio_set = bytes([
            SET_LOW_BYTE_DATA_BITS_CMD,
            VALUE_SCLHIGH_SDAHIGH,
            DIRECTION_SCLOUT_SDAOUT,
        ])
        self.FT_Write(gpio_set)

    def i2c_start(self, send=True):
        scl_high_sda_high = bytes([
            MPSSE_CMD_SET_DATA_BITS_LOWBYTE,
            VALUE_SCLHIGH_SDAHIGH,
            DIRECTION_SCLOUT_SDAOUT,
        ])
        scl_high_sda_low = bytes([
            MPSSE_CMD_SET_DATA_BITS_LOWBYTE,
            VALUE_SCLHIGH_SDALOW,
            DIRECTION_SCLOUT_SDAOUT,
        ])
        scl_low_sda_low = bytes([
            MPSSE_CMD_SET_DATA_BITS_LOWBYTE,
            VALUE_SCLLOW_SDALOW,
            DIRECTION_SCLOUT_SDAOUT,
        ])
        start_cmd = scl_high_sda_high * START_DURATION_1 + \
            scl_high_sda_low * START_DURATION_2 + scl_low_sda_low
        if send:
            self.FT_Write(start_cmd)
            self.check_status()
        else:
            return start_cmd

    def i2c_stop(self, send=True):
        scl_low_sda_low = bytes([
            MPSSE_CMD_SET_DATA_BITS_LOWBYTE,
            VALUE_SCLLOW_SDALOW,
            DIRECTION_SCLOUT_SDAOUT,
        ])
        scl_high_sda_low = bytes([
            MPSSE_CMD_SET_DATA_BITS_LOWBYTE,
            VALUE_SCLHIGH_SDALOW,
            DIRECTION_SCLOUT_SDAOUT,
        ])
        scl_high_sda_high = bytes([
            MPSSE_CMD_SET_DATA_BITS_LOWBYTE,
            VALUE_SCLHIGH_SDAHIGH,
            DIRECTION_SCLOUT_SDAOUT,
        ])
        stop_cmd = scl_low_sda_low * STOP_DURATION_1 + \
            scl_high_sda_low * STOP_DURATION_2 + \
            scl_high_sda_high * STOP_DURATION_3
        if send:
            self.FT_Write(stop_cmd)
            self.check_status()
        else:
            return stop_cmd

    def i2c_restart(self, send=True):
        RESTART_1 = bytes([
            MPSSE_CMD_SET_DATA_BITS_LOWBYTE,
            VALUE_SCLHIGH_SDALOW,
            DIRECTION_SCLOUT_SDAOUT,
        ])
        RESTART_2 = bytes([
            MPSSE_CMD_SET_DATA_BITS_LOWBYTE,
            VALUE_SCLHIGH_SDAHIGH,
            DIRECTION_SCLOUT_SDAOUT,
        ])
        RESTART_3 = bytes([
            MPSSE_CMD_SET_DATA_BITS_LOWBYTE,
            VALUE_SCLLOW_SDAHIGH,
            DIRECTION_SCLOUT_SDAOUT,
        ])
        RESTART_4 = bytes([
            MPSSE_CMD_SET_DATA_BITS_LOWBYTE,
            VALUE_SCLHIGH_SDAHIGH,
            DIRECTION_SCLOUT_SDAOUT,
        ])
        RESTART_5 = bytes([
            MPSSE_CMD_SET_DATA_BITS_LOWBYTE,
            VALUE_SCLHIGH_SDALOW,
            DIRECTION_SCLOUT_SDAOUT,
        ])
        # tristate before read
        # RESTART_6 = bytes([
        #     MPSSE_CMD_SET_DATA_BITS_LOWBYTE,
        #     VALUE_SCLLOW_SDAHIGH,
        #     DIRECTION_SCLOUT_SDAOUT,
        # ])
        RESTART_6 = bytes([
            MPSSE_CMD_SET_DATA_BITS_LOWBYTE,
            VALUE_SCLLOW_SDALOW,
            DIRECTION_SCLOUT_SDAOUT,
        ])
        RESTART_7 = bytes([
            MPSSE_CMD_SET_DATA_BITS_LOWBYTE,
            VALUE_SCLLOW_SDAHIGH,
            DIRECTION_SCLOUT_SDAOUT,
        ])
        # restart_cmd = RESTART_1 * RESTART_DURATION + RESTART_2 * RESTART_DURATION + \
        #     RESTART_3 * RESTART_DURATION + RESTART_4 * RESTART_DURATION + \
        #     RESTART_5 * RESTART_DURATION + RESTART_6
        # restart_cmd = RESTART_1 * RESTART_DURATION + RESTART_2 * RESTART_DURATION + \
        #     RESTART_4 * RESTART_DURATION + \
        #     RESTART_5 * RESTART_DURATION + RESTART_6 * \
        #     RESTART_DURATION + RESTART_7 * RESTART_DURATION
        restart_cmd = RESTART_3 * RESTART_DURATION + RESTART_2 * RESTART_DURATION + \
            RESTART_1 * RESTART_DURATION + RESTART_6 * RESTART_DURATION
        if send:
            self.FT_Write(restart_cmd)
            self.check_status()
        else:
            return restart_cmd

    def i2c_Write8bitsAndGetAck(self, data, send=True):
        tristateoff = bytes([
            MPSSE_CMD_ENABLE_DRIVE_ONLY_ZERO,
            0x00,
            0x00,
        ])
        tristateon = bytes([
            MPSSE_CMD_ENABLE_DRIVE_ONLY_ZERO,
            0x02,
            0x00,
        ])
        setdirection = bytes([
            MPSSE_CMD_SET_DATA_BITS_LOWBYTE,
            # tristate
            VALUE_SCLLOW_SDALOW,  # 1212
            DIRECTION_SCLOUT_SDAOUT,
        ])
        # out, MSB, 8bits, negetive edge out
        transfermode = bytes([
            MPSSE_CMD_DATA_OUT_BITS_NEG_EDGE,
            DATA_SIZE_8BITS,
            data,
        ])
        # Set SDA to input mode before reading ACK bit
        preparetoread = bytes([
            MPSSE_CMD_SET_DATA_BITS_LOWBYTE,
            VALUE_SCLLOW_SDAHIGH,  # FT232 tristate set
            DIRECTION_SCLOUT_SDAOUT,
        ])
        getack = bytes([
            MPSSE_CMD_DATA_IN_BITS_POS_EDGE,
            DATA_SIZE_1BIT,
        ])
        # Command MPSSE to send data to PC immediately
        Send_Immediate = bytes([
            MPSSE_CMD_SEND_IMMEDIATE,
        ])
        write_8bit_cmd = tristateoff + setdirection + transfermode + \
            Send_Immediate + tristateon + preparetoread + getack + Send_Immediate

        if send:
            self.FT_Write(write_8bit_cmd + Send_Immediate)
            self.check_status()
            self.FT_Read(1)
            self.check_status()
            nack = self.inbytes[0] & 0x01
            if nack:
                logging.error('no ack')
                return False
            else:
                logging.info('slave ack')
                return True
        else:
            return write_8bit_cmd

    def i2c_Read8bitsAndGiveAck(self, ack=True, send=True):
        setdirection = bytes([
            MPSSE_CMD_SET_DATA_BITS_LOWBYTE,
            VALUE_SCLLOW_SDAHIGH,
            DIRECTION_SCLOUT_SDAOUT,
        ])
        tristateoff = bytes([
            MPSSE_CMD_ENABLE_DRIVE_ONLY_ZERO,
            0x00,
            0x00,
        ])
        tristateon = bytes([
            MPSSE_CMD_ENABLE_DRIVE_ONLY_ZERO,
            0x02,
            0x00,
        ])
        # in, MSB, 8bits, positive edge in
        # transfermode = bytes([
        #     MPSSE_CMD_DATA_IN_BITS_POS_EDGE,
        #     DATA_SIZE_8BITS,
        # ])
        transfermode = bytes([
            MPSSE_CMD_DATA_IN_BITS_POS_EDGE,
            DATA_SIZE_8BITS,
        ])
        # Command MPSSE to send data to PC immediately
        Send_Immediate = bytes([
            MPSSE_CMD_SEND_IMMEDIATE,
        ])
        # proposal 2 ???
        afterread = SEND_ACK if ack else SEND_NACK
        proposal2 = bytes([
            # MPSSE_CMD_SET_DATA_BITS_LOWBYTE,
            # VALUE_SCLLOW_SDAHIGH,  # tristate
            # DIRECTION_SCLOUT_SDAOUT,
            # MPSSE_CMD_DATA_OUT_BITS_NEG_EDGE,
            # 0,
            # afterread,
            MPSSE_CMD_DATA_OUT_BITS_NEG_EDGE,
            0,
            afterread,
        ])
        read_8bits_cmd = tristateon + setdirection + transfermode + \
            Send_Immediate + tristateoff + proposal2 + tristateon + Send_Immediate
        if send:
            self.FT_Write(read_8bits_cmd)
            self.mmpsse_read(1, 10)
        else:
            return read_8bits_cmd

    def i2c_FastWrite_EEPROM(self, slave7bit, regaddr, bdata, burst=None):
        startcmd = self.i2c_start(send=False)
        stopcmd = self.i2c_stop(send=False)
        addresscmd = self.i2c_Write8bitsAndGetAck(
            slave7bit << 1 | 0, send=False)
        regaddrcmd = self.i2c_Write8bitsAndGetAck(regaddr, send=False)
        wrdatacmd = b''
        datalen = len(bdata)
        if not burst:
            burst = datalen
        while bdata:
            onetime, bdata = bdata[:burst], bdata[burst:]
            # makeup data cmd for one burst
            for i in range(len(onetime)):
                wrdatacmd += self.i2c_Write8bitsAndGetAck(
                    onetime[i], send=False)

            self.FT_Write(startcmd + addresscmd +
                          regaddrcmd + wrdatacmd + stopcmd)
            wrdatacmd = b''
            # read acks
            self.mmpsse_read(len(onetime) + 2, 10)
            ackbytes = self.inbytes
            cnt = 0
            for i in ackbytes:
                if i & 0x01:
                    cnt += 1
            if cnt > 0:
                logging.warning('except %d acks, miss %d' %
                                (len(ackbytes), cnt))

            self.flushinbuff()

    def i2c_FastWrite(self, slave7bit, bdata, burst=None):
        print(f'i2c write addr {slave7bit<<1:02x}, data {bdata.hex()}')
        startcmd = self.i2c_start(send=False)
        stopcmd = self.i2c_stop(send=False)
        addresscmd = self.i2c_Write8bitsAndGetAck(
            slave7bit << 1 | 0, send=False)
        wrdatacmd = b''
        datalen = len(bdata)
        if not burst:
            burst = datalen
        while bdata:
            onetime, bdata = bdata[:burst], bdata[burst:]
            # makeup data cmd for one burst
            for i in range(len(onetime)):
                wrdatacmd += self.i2c_Write8bitsAndGetAck(
                    onetime[i], send=False)

            self.FT_Write(startcmd + addresscmd + wrdatacmd + stopcmd)
            wrdatacmd = b''
            # read acks
            self.mmpsse_read(len(onetime) + 1, 10)
            ackbytes = self.inbytes
            # if any([i & 0x01 for i in ackbytes]):
            # logging.warning('seem lose some ack')
            cnt = 0
            for i in ackbytes:
                if i & 0x01:
                    cnt += 1
            if cnt > 0:
                logging.warning('except %d acks, miss %d' %
                                (len(ackbytes), cnt))

            self.flushinbuff()

    def i2c_FastRead_EEPROM(self, slave7bit, regaddr, inlen, burst=None, timeout=10):
        startcmd = self.i2c_start(send=False)
        stopcmd = self.i2c_stop(send=False)
        restcmd = self.i2c_restart(send=False)
        addresscmd0 = self.i2c_Write8bitsAndGetAck(
            slave7bit << 1 | 0, send=False)
        addresscmd1 = self.i2c_Write8bitsAndGetAck(
            slave7bit << 1 | 1, send=False)
        regaddrcmd = self.i2c_Write8bitsAndGetAck(regaddr, send=False)
        # slave data prepare may not ready when master read, so delay
        rddelay = bytes([
            MPSSE_CMD_SET_DATA_BITS_LOWBYTE,
            VALUE_SCLLOW_SDAHIGH,
            DIRECTION_SCLOUT_SDAOUT,
        ])
        inbytes = b''
        rddatacmd = b''
        if not burst:
            burst = inlen
        while inlen:
            if inlen < burst:
                burst = inlen
            for i in range(burst):
                # no ack after the last bytes
                if i == burst - 1:
                    t = self.i2c_Read8bitsAndGiveAck(ack=False, send=False)
                else:
                    t = self.i2c_Read8bitsAndGiveAck(send=False)

                rddatacmd += t
            # send read cmd
            self.FT_Write(startcmd + addresscmd0 + regaddrcmd +
                          restcmd + addresscmd1 + rddelay * SLAVE_PREPARE_DURATION + rddatacmd + stopcmd)
            self.mmpsse_read(burst + 3, timeout)
            inbytes += self.inbytes
            inlen -= burst
            rddatacmd = b''
        return inbytes[3:] #3 acks should be ignored

    def i2c_FastRead(self, slave7bit, inlen, burst=None, timeout=10):
        startcmd = self.i2c_start(send=False)
        stopcmd = self.i2c_stop(send=False)
        addresscmd1 = self.i2c_Write8bitsAndGetAck(
            slave7bit << 1 | 1, send=False)
        # slave data prepare may not ready when master read, so delay
        rddelay = bytes([
            MPSSE_CMD_SET_DATA_BITS_LOWBYTE,
            VALUE_SCLLOW_SDAHIGH,
            DIRECTION_SCLOUT_SDAOUT,
        ])
        inbytes = b''
        rddatacmd = b''
        if not burst:
            burst = inlen
        while inlen:
            if inlen < burst:
                burst = inlen
            for i in range(burst):
                # no ack after the last bytes
                if i == burst - 1:
                    t = self.i2c_Read8bitsAndGiveAck(ack=False, send=False)
                else:
                    t = self.i2c_Read8bitsAndGiveAck(send=False)

                rddatacmd += t
            # send read cmd
            self.FT_Write(startcmd + addresscmd1 + rddelay *
                          SLAVE_PREPARE_DURATION + rddatacmd + stopcmd)
            self.mmpsse_read(burst + 1, timeout)
            inbytes += self.inbytes
            inlen -= burst
            rddatacmd = b''
        print(f'i2c read bytes {inbytes[1:].hex()}')
        return inbytes[1:] #1 acks should be ignored

