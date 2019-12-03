def bytesToSPI(bdata, bus_width):
    # print('in data format\n', bdata)
    if bus_width <= 8:
        spi_data = bytes([i & (0xff >> (8 - bus_width)) for i in bdata])
    elif bus_width <= 16:
        spi_data = b''
        while bdata:
            bytes2, bdata = bdata[:2], bdata[2:]
            spi_data += bytes([bytes2[0] & (0xff >> (16 - bus_width))]) +\
                        bytes([bytes2[1]])
    elif bus_width <= 24:
        spi_data = b''
        while bdata:
            bytes4, bdata = bdata[:4], bdata[4:]
            spi_data += bytes([0x00]) +\
                        bytes([bytes4[1] & (0xff >> (24 - bus_width))]) +\
                        bytes4[2:]
    else:
        spi_data=b''
        while bdata:
            bytes4, bdata=bdata[:4], bdata[4:]
            spi_data += bytes([bytes4[0] & (0xff >> (32 - bus_width))]) +\
                        bytes4[1:]
    return spi_data
