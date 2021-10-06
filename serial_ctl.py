import threading
import serial


class SerialPort(object):
    def __init__(self, port, baudrate, size, buf):
        self.size = size
        self.buf = buf
        self.port = serial.Serial(port, baudrate, bytesize=8)

    def recv(self):
        while True:
            t = self.port.read(self.size).hex()
            self.buf.put(t)

    def loop_recv(self):
        t = threading.Thread(target=self.recv)
        t.start()
