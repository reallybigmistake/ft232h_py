IMG_HDR_MAX_SECT = 29
IMG_PKT_MAXLEN = 4096
IMG_HDR_SIZE = 512


class img_memarea:
    length = 0, 4
    deployment_addr = 4, 4
    crc16 = 8, 2
    devid = 10, 1
    name = 11, 5
    total = 16


class img_header:
    fw_marker = 0, 4
    image_len = 4, 4
    image_ver = 8, 1
    image_reversion = 9, 1
    rev0 = 10, 2
    image_appentrypointaddress = 12, 4
    image_appvecttableaddress = 16, 4
    image_numofmemarea = 20, 4
    memarea = 24, img_memarea.total * IMG_HDR_MAX_SECT
    rsv1 = memarea[0] + memarea[1], 12
    dsp1_load_addr = rsv1[0] + rsv1[1], 4
    dsp1_load_len = dsp1_load_addr[0] + dsp1_load_addr[1], 4
    rsv2 = dsp1_load_len[0] + dsp1_load_len[1], 2
    header_crc16 = rsv1[0] + rsv1[1], 2
    total = 512


class BytesAnalyse:

    def __init__(self, binbytes):
        self.binbytes = binbytes
        self.phrase()

    def phrase(self):
        self.bfw_marker = getmembytes(
            self.binbytes, img_header, 'fw_marker')
        self.bimage_len = getmembytes(
            self.binbytes, img_header, 'image_len')
        self.bimage_ver = getmembytes(
            self.binbytes, img_header, 'image_ver')
        self.bimage_reversion = getmembytes(
            self.binbytes, img_header, 'image_reversion')
        self.brev0 = getmembytes(self.binbytes, img_header, 'rev0')
        self.bimage_appentrypointaddress = getmembytes(
            self.binbytes, img_header, 'image_appentrypointaddress')
        self.bimage_appvecttableaddress = getmembytes(
            self.binbytes, img_header, 'image_appvecttableaddress')
        self.bimage_numofmemarea = getmembytes(
            self.binbytes, img_header, 'image_numofmemarea')
        self.brsv1 = getmembytes(self.binbytes, img_header, 'rsv1')
        self.dsp1_load_addr = getmembytes(self.binbytes, img_header, 'dsp1_load_addr')
        self.dsp1_load_len = getmembytes(self.binbytes, img_header, 'dsp1_load_len')
        self.brsv2 = getmembytes(self.binbytes, img_header, 'rsv2')
        self.bheader_crc16 = getmembytes(
            self.binbytes, img_header, 'header_crc16')

        self.bmemarea = getmembytes(self.binbytes, img_header, 'memarea')
        self.blmemarea = []
        for i in range(IMG_HDR_MAX_SECT):
            self.blmemarea.append(
                self.bmemarea[i * img_memarea.total:(i + 1) * img_memarea.total])


def getmembytes(bdata, cls, mem):
    start = getattr(cls, mem)[0]
    end = start + getattr(cls, mem)[1]
    return bdata[start:end]

if __name__ == '__main__':
    fwbin = open('dsp_cdl.nonsec.bin', 'rb')
    print(bytes(fwbin)[:10])
    # b = BytesAnalyse(bytes([i % 0x100 for i in range(512)]))
    # print(b.blmemarea)
