import serial.tools.list_ports
import serial


def listCom():
    comlist = []
    for ser in serial.tools.list_ports.comports():
        comlist.append(ser[0])
    return comlist
if __name__ == '__main__':
    print(11)
