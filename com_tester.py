import serial
import time

file_path = 'C:\\Users\\pc\\Desktop\\Rec211007181154.txt'
ser = serial.Serial('COM4', 115200, bytesize=8)
with open(file_path, 'r') as file:
    data = file.readline()
    hex_list = data.split(' ')
    print(hex_list)
    for hex_code in hex_list:
        byte_array = bytes.fromhex(hex_code)
        print(byte_array)
        ser.write(byte_array)
        # time.sleep(0.1)
    ser.close()
