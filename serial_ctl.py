import threading
from queue import Queue

import serial


class SerialPort(object):
    def __init__(self, port, baudrate, size):
        self.size = size
        self.buf = Queue()
        self.port = serial.Serial(port, baudrate, bytesize=8)

    def recv(self):
        while True:
            t = self.port.read(self.size).hex()
            print(t)
            num = int(t, 16)
            b_num = bin(num)[2:].zfill(16)
            flag = b_num[:6]
            data = b_num[-10:]
            print(b_num)
            self.buf.put(t)

    def loop_recv(self):
        t = threading.Thread(target=self.recv)
        t.start()


if __name__ == '__main__':
    ser = SerialPort('COM5', 115200, 2)
    ser.loop_recv()
