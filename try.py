import serial
from datapackage import DataPackageConverter


# 初始化串口
def initialize_serial():
    try:
        ser = serial.Serial('/dev/ttyAMA0', 115200)
        if not ser.isOpen():
            ser.open()
        return ser
    except serial.SerialException:
        raise Exception("Failed to initialize serial connection.")

ser = initialize_serial()
movements = DataPackageConverter("1.bin").hex_output
ser.write(bytearray(movements))
