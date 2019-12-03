class NOR_flash_command:
    RDID = 0x9F


class Command_MX(NOR_flash_command):
    RDID = 0x9F
    READ = 0x03
    SECTOR_ERASE = 0x20
    BLOCK_ERASE_32K = 0x52
    BLOCK_ERASE_64K = 0xD8
    CHIP_ERASE1 = 0x60
    CHIP_ERASE2 = 0xC7
    WRITE_ENABLE = 0x06
    WRITE_DISABLE = 0x04
    RD_STATUS_REG = 0x05
    WR_STATUS_REG = 0x01
    RD_SECURITY_REG = 0x2B
    shift_E_FAIL = 6
    shift_P_FAIL = 5
    WR_SECURITY_REG = 0x2F
    PAGE_PROGRAM = 0x02
    shift_WIP = 0
    shift_WEL = 1

    PAGESIZE = 0x100

