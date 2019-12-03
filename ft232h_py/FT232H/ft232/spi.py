from ft232.mpsse import MPSSE
from ft232.dll_h import *
import logging
import time
from columbus.data_format import bytesToSPI


class SPI(MPSSE):

    def __init__(self, description):
        MPSSE.__init__(self, description)
        self.config_to_mmse()

    def set_clock(self, clock):
        # <=6M
        if clock <= 1000000:
            self.FT_Write(bytes([ENABLE_CLOCK_DIVIDE]))
            self.check_status()
            div = int(6000000 / clock) - 1
            self.realclk = 6000000 / (1 + div)
        # >6M
        else:
            self.FT_Write(bytes([DISABLE_CLOCK_DIVIDE]))
            self.check_status()
            div = int(30000000 / clock) - 1
            self.realclk = 30000000 / (1 + div)
        setclkcmd = bytes([
            SET_CLOCK_FREQUENCY_CMD,
            div & 0xff,
            div >> 8,
        ])
        self.FT_Write(setclkcmd)
        self.check_status()

    def spi_config(self, clock, mode, bus_width):
        self.mode = mode
        self.bus_width = bus_width
        self.set_clock(clock)
        if self.mode not in [0, 1, 2, 3] or self.bus_width not in range(1, 33):
            logging.error('invalid mode')
        self.polarity = (mode & 0x03) >> 1
        self.phase = (mode & 0x01)
        # disable i2c clock phase
        self.FT_Write(bytes([MPSSE_CMD_DISABLE_3PHASE_CLOCKING]))
        # set dirction
        # cs out 1, DI input 0, DO output 0, SK output low when mode is 0 / 1,
        # high when mode is 2 / 3
        if self.polarity == 0:
            gpio_set = bytes([
                SET_LOW_BYTE_DATA_BITS_CMD,
                0x08,
                0x0B,
            ])
        elif self.polarity == 1:
            gpio_set = bytes([
                SET_LOW_BYTE_DATA_BITS_CMD,
                0x09,
                0x0B,
            ])
        self.FT_Write(gpio_set * 10)

    def spi_ToggleCS(self, state, send=True):
        if state:
            if self.polarity == 0:
                gpio_value = 0x08
            elif self.polarity == 1:
                gpio_value = 0x09
        else:
            if self.polarity == 0:
                gpio_value = 0x00
            elif self.polarity == 1:
                gpio_value = 0x01
        gpio_set = bytes([
            SET_LOW_BYTE_DATA_BITS_CMD,
            gpio_value,
            SPI_DIRECTION,
        ])
        self.FT_Write(gpio_set)

    def spi_Write8bits(self, data, datalen, send=True):
        if self.mode == 0:
            outcmd = MPSSE_CMD_DATA_OUT_BITS_NEG_EDGE
        elif self.mode == 1:
            outcmd = MPSSE_CMD_DATA_OUT_BITS_POS_EDGE
        elif self.mode == 2:
            outcmd = MPSSE_CMD_DATA_OUT_BITS_POS_EDGE
        elif self.mode == 3:
            outcmd = MPSSE_CMD_DATA_OUT_BITS_NEG_EDGE
        write_cmd = bytes([
            outcmd,
            datalen - 1,
            data,
        ])
        if send:
            self.FT_Write(write_cmd)
            self.check_status()
        else:
            return write_cmd

    def spi_Read8bits(self, datalen, send=True):
        if self.mode == 0:
            incmd = MPSSE_CMD_DATA_IN_BITS_POS_EDGE
        elif self.mode == 1:
            incmd = MPSSE_CMD_DATA_IN_BITS_NEG_EDGE
        elif self.mode == 2:
            incmd = MPSSE_CMD_DATA_IN_BITS_NEG_EDGE
        elif self.mode == 3:
            incmd = MPSSE_CMD_DATA_IN_BITS_POS_EDGE
        read_cmd = bytes([
            incmd,
            datalen - 1,
        ])
        if send:
            self.FT_Write(read_cmd)
            self.check_status()
            self.mmpsse_read(1, 10)
        else:
            return read_cmd

    def spi_writeBit_cmd(self, data, bitlen):
        if self.mode == 0:
            outcmd = MPSSE_CMD_DATA_OUT_BITS_NEG_EDGE
        elif self.mode == 1:
            outcmd = MPSSE_CMD_DATA_OUT_BITS_POS_EDGE
        elif self.mode == 2:
            outcmd = MPSSE_CMD_DATA_OUT_BITS_POS_EDGE
        elif self.mode == 3:
            outcmd = MPSSE_CMD_DATA_OUT_BITS_NEG_EDGE
        if bitlen == 0:
            write_cmd = bytes([])
        else:
            write_cmd = bytes([
                outcmd,
                bitlen - 1,
                (data << (8 - bitlen)) & 0xff,
            ])
        return write_cmd

    def spi_readBit_cmd(self, datalen):
        if self.mode == 0:
            incmd = MPSSE_CMD_DATA_IN_BITS_POS_EDGE
        elif self.mode == 1:
            incmd = MPSSE_CMD_DATA_IN_BITS_NEG_EDGE
        elif self.mode == 2:
            incmd = MPSSE_CMD_DATA_IN_BITS_NEG_EDGE
        elif self.mode == 3:
            incmd = MPSSE_CMD_DATA_IN_BITS_POS_EDGE
        read_cmd = bytes([
            incmd,
            datalen - 1,
        ])
        return read_cmd

    def SPI_Write_bits(self, bdata, burst=None, send=True):
        bits_pattern = []
        write_cmd = bytes([])
        if self.bus_width <= 8:
            bits_pattern = [self.bus_width]
        elif self.bus_width <= 16:
            bits_pattern = [self.bus_width - 8, 8]
        elif self.bus_width <= 24:
            bits_pattern = [0, self.bus_width - 16, 8, 8]
        else:
            bits_pattern = [self.bus_width - 24, 8, 8, 8]

        bits_patterns = bits_pattern * int(len(bdata)/len(bits_pattern))

        for i in range(len(bits_patterns)):
            write_cmd += self.spi_writeBit_cmd(bdata[i], bits_patterns[i])

        clk_set_high = bytes([
            SET_LOW_BYTE_DATA_BITS_CMD,
            0x01,
            0x0B,
        ])
        clk_set_low = bytes([
            SET_LOW_BYTE_DATA_BITS_CMD,
            0x00,
            0x0B,
        ])
        self.spi_ToggleCS(0)
        if self.mode == 1:
            self.FT_Write(clk_set_high + write_cmd + clk_set_low)
        elif self.mode == 3:
            self.FT_Write(clk_set_low + write_cmd + clk_set_high)
        else:
            self.FT_Write(write_cmd)
        self.check_status()
        self.spi_ToggleCS(1)

    def SPI_Read_bits(self, wordlen, burst=None, send=True, timeout=100):
        bit_mode = self.bus_width

        self.spi_ToggleCS(0)
        read_cmd = bytes([])
        cmd_pattern = bytes([])
        cmd_pattern_list = []
        while bit_mode:
            if bit_mode >= 8:
                bit_recv = 8
            else:
                bit_recv = bit_mode
            bit_mode -= bit_recv
            cmd_pattern_list.append(self.spi_readBit_cmd(bit_recv))
        cmd_pattern_list.reverse()
        for i in cmd_pattern_list:
            cmd_pattern += i 
        
        read_cmd = cmd_pattern * wordlen

        Send_Immediate = bytes([
            MPSSE_CMD_SEND_IMMEDIATE,
        ])
        clk_set_high = bytes([
            SET_LOW_BYTE_DATA_BITS_CMD,
            0x01,
            0x0B,
        ])
        clk_set_low = bytes([
            SET_LOW_BYTE_DATA_BITS_CMD,
            0x00,
            0x0B,
        ])
        if self.mode == 1:
            self.FT_Write(clk_set_high + read_cmd +
                          Send_Immediate + clk_set_low)
        elif self.mode == 3:
            self.FT_Write(clk_set_low + read_cmd +
                          Send_Immediate + clk_set_high)
        else:
            self.FT_Write(read_cmd + Send_Immediate)
        
        if self.bus_width <= 8:
            bytesIn = 1
        elif self.bus_width <= 16:
            bytesIn = 2
        elif self.bus_width <= 24:
            bytesIn = 3
        else:
            bytesIn = 4
        self.mmpsse_read(bytesIn * wordlen, timeout)
        
        if self.bus_width in range(17, 25):
            # add high byte
            result = bytes([])
            inbytes_tmp = self.inbytes
            while inbytes_tmp:
                wordbytes, inbytes_tmp = inbytes_tmp[:3], inbytes_tmp[3:]
                result += b'\x00' + wordbytes
        else:
            result = self.inbytes
        self.spi_ToggleCS(1)
        
        return bytesToSPI(result, self.bus_width)

    def SPI_Write(self, bdata, burst=None, send=True):
        if self.mode == 0:
            outcmd = MPSSE_CMD_DATA_OUT_BYTES_NEG_EDGE
        elif self.mode == 1:
            outcmd = MPSSE_CMD_DATA_OUT_BYTES_POS_EDGE
        elif self.mode == 2:
            outcmd = MPSSE_CMD_DATA_OUT_BYTES_POS_EDGE
        elif self.mode == 3:
            outcmd = MPSSE_CMD_DATA_OUT_BYTES_NEG_EDGE
        len_out_cmd = len(bdata) - 1

        write_cmd = bytes([
            outcmd,
            len_out_cmd & 0xff,
            (len_out_cmd >> 8) & 0xff,
        ])
        # work around so the mode 1 and 3 will work?
        clk_set_high = bytes([
            SET_LOW_BYTE_DATA_BITS_CMD,
            0x01,
            0x0B,
        ])
        clk_set_low = bytes([
            SET_LOW_BYTE_DATA_BITS_CMD,
            0x00,
            0x0B,
        ])
        Send_Immediate = bytes([
            MPSSE_CMD_SEND_IMMEDIATE,
        ])
        self.spi_ToggleCS(0)
        if self.mode == 1:
            self.FT_Write(clk_set_high + write_cmd + bdata + clk_set_low)
        elif self.mode == 3:
            self.FT_Write(clk_set_low + write_cmd + bdata + clk_set_high)
        else:
            self.FT_Write(write_cmd + bdata)
        self.check_status()
        self.spi_ToggleCS(1)

    def SPI_Read(self, inlen, burst=None, timeout=100):
        self.spi_ToggleCS(0)
        if self.mode == 0:
            incmd = MPSSE_CMD_DATA_IN_BYTES_POS_EDGE
        elif self.mode == 1:
            incmd = MPSSE_CMD_DATA_IN_BYTES_NEG_EDGE
        elif self.mode == 2:
            incmd = MPSSE_CMD_DATA_IN_BYTES_NEG_EDGE
        elif self.mode == 3:
            incmd = MPSSE_CMD_DATA_IN_BYTES_POS_EDGE
        len_in_cmd = inlen - 1
        read_cmd = bytes([
            incmd,
            len_in_cmd & 0xff,
            (len_in_cmd >> 8) & 0xff,
        ])
        Send_Immediate = bytes([
            MPSSE_CMD_SEND_IMMEDIATE,
        ])
        clk_set_high = bytes([
            SET_LOW_BYTE_DATA_BITS_CMD,
            0x01,
            0x0B,
        ])
        clk_set_low = bytes([
            SET_LOW_BYTE_DATA_BITS_CMD,
            0x00,
            0x0B,
        ])
        if self.mode == 1:
            self.FT_Write(clk_set_high + read_cmd +
                          Send_Immediate + clk_set_low)
        elif self.mode == 3:
            self.FT_Write(clk_set_low + read_cmd +
                          Send_Immediate + clk_set_high)
        else:
            self.FT_Write(read_cmd + Send_Immediate)
        self.mmpsse_read(inlen, timeout)
        self.spi_ToggleCS(1)
        return self.inbytes

    def SPI_WriteRead(self, bdata, inlen, timeout=10):
        if self.mode == 0:
            outcmd = MPSSE_CMD_DATA_OUT_BYTES_NEG_EDGE
            incmd = MPSSE_CMD_DATA_IN_BYTES_POS_EDGE
        elif self.mode == 1:
            outcmd = MPSSE_CMD_DATA_OUT_BYTES_POS_EDGE
            incmd = MPSSE_CMD_DATA_IN_BYTES_NEG_EDGE
        elif self.mode == 2:
            outcmd = MPSSE_CMD_DATA_OUT_BYTES_POS_EDGE
            incmd = MPSSE_CMD_DATA_IN_BYTES_NEG_EDGE
        elif self.mode == 3:
            outcmd = MPSSE_CMD_DATA_OUT_BYTES_NEG_EDGE
            incmd = MPSSE_CMD_DATA_IN_BYTES_POS_EDGE
        len_out_cmd = len(bdata) - 1
        len_in_cmd = inlen - 1

        if bdata:
            write_cmd = bytes([
                outcmd,
                len_out_cmd & 0xff,
                (len_out_cmd >> 8) & 0xff,
            ])
        else:
            write_cmd = b''
        if inlen:
            read_cmd = bytes([
                incmd,
                len_in_cmd & 0xff,
                (len_in_cmd >> 8) & 0xff,
            ])
        else:
            read_cmd = b''

        # work around so the mode 1 and 3 will work?
        clk_set_high = bytes([
            SET_LOW_BYTE_DATA_BITS_CMD,
            0x01,
            0x0B,
        ])
        clk_set_low = bytes([
            SET_LOW_BYTE_DATA_BITS_CMD,
            0x00,
            0x0B,
        ])
        self.spi_ToggleCS(0)
        if self.mode == 1:
            self.FT_Write(clk_set_high + write_cmd +
                          bdata + read_cmd + clk_set_low)
        elif self.mode == 3:
            self.FT_Write(clk_set_low + write_cmd +
                          bdata + read_cmd + clk_set_high)
        else:
            self.FT_Write(write_cmd + bdata + read_cmd)
        self.check_status()
        self.spi_ToggleCS(1)
        self.mmpsse_read(inlen, timeout)
        return self.inbytes


if __name__ == '__main__':
    pass
