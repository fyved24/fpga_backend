import threading
from queue import Queue

import serial


class SerialPort(object):
    def __init__(self, port, baudrate, size):
        self.size = size
        self.buf = Queue()
        self.port = serial.Serial(port, baudrate, bytesize=8)

    def recv(self):
        pre_ff = False
        read_flag = False
        while True:
            if read_flag:
                frame = self.port.read(2).hex()
                flag, data = self.parse(frame)
                print(f"frame: {frame}, flag: {flag}, data: {data}")
                if flag == '000000':
                    self.buf.put(data)
                else:
                    if frame == 'ffff':
                        print('end of a paragraph')
                    else:
                        read_flag = False
            else:
                t = self.port.read().hex()
                if t == 'ff' and pre_ff:
                    read_flag = True
                else:
                    read_flag = False
                if t == 'ff':
                    pre_ff = True
                else:
                    pre_ff = False

    def parse(self, frame):
        num = int(frame, 16)
        b_num = bin(num)[2:].zfill(16)
        flag = b_num[:6]
        data = b_num[-10:]
        return flag, data

    def loop_recv(self):
        t = threading.Thread(target=self.recv)
        t.start()


if __name__ == '__main__':
    ser = SerialPort('COM5', 115200, 2)
    ser.loop_recv()
