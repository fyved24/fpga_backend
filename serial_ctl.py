import threading
from queue import Queue
import asyncio

import serial


class SerialPort(object):
    def __init__(self, port, baudrate, size):
        self.size = size
        self.buf = Queue()
        self.segment = []
        self.port = serial.Serial(port, baudrate, bytesize=8)
        self._hook = None

    def set_hook(self, hook):
        self._hook = hook

    def recv(self):
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        while True:
            frame = self.port.read(2).hex()
            if frame == 'ffff' and len(self.segment) > 0:
                self._hook(self.segment)
                self.segment = []
            head1, head2, data = self.parse(frame)
            if self.is_available(head1, head2, data):
                # 是ch1的话
                if head1[0] == '0':
                    data = {
                        'ch': 1,
                        'data': data
                    }
                else:
                    data = {
                        'ch': 2,
                        'data': data
                    }
                self.buf.put(data)
                self.segment.append(data)
            else:
                # 无效的话就丢弃一帧，继续读
                self.port.read().hex()

    def is_available(self, head1, head2, data):
        """
        ch1 000_____ 010_____
        ch2 100_____ 110_____
        :param head1: _00
        :param head2: _10
        :param data:
        :return:
        """
        # 判断数据帧是否有效的
        print(f"head1: {head1}, head2: {head2}, data: {data}")
        if head1[0] == head2[0]:
            if head1[1] == '0' and head2[1] == '1':
                return True
        return False

    def parse(self, frame):
        num = int(frame, 16)
        b_num = bin(num)[2:].zfill(16)
        head1 = b_num[:3]
        head2 = b_num[8:11]
        data = b_num[3:8] + b_num[11:]
        return head1, head2, data

    def loop_recv(self):
        print('serial listening')
        t = threading.Thread(target=self.recv)
        t.start()


if __name__ == '__main__':
    ser = SerialPort('COM5', 115200, 2)
    ser.loop_recv()
