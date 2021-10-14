import json
import threading
import time
import asyncio

import serial


def resize(num):
    return round((num - 511) / (511 / 5), 2)


class SerialPort(object):
    def __init__(self, port, baudrate, size):
        self.size = size
        self.segment1 = []
        self.segment2 = []
        self.maximum = [0, 0]
        self.minimum = [1024, 1024]
        self.jump_flag = [False, False]
        self.cnt = [0, 0]
        self.period = [0.0, 0.0]
        self.port = serial.Serial(port, baudrate, bytesize=8)
        self._hook = None

    def set_hook(self, hook):
        self._hook = hook

    def send(self, data):
        bdata = bytes.fromhex(data)
        print(f'writing data {bdata}')
        self.port.write(bdata)

    def recv(self):

        pre_time = None
        while True:
            if len(self.segment1) > 3:
                data = {
                    'type': 'data',
                    'data': self.segment1
                }
                self._hook(data)
                self.segment1 = []
            if len(self.segment2) > 3:
                data = {
                    'type': 'data',
                    'data': self.segment2
                }

                self._hook(data)
                self.segment2 = []

            frame = self.port.read(2).hex()
            if pre_time is None:
                pre_time = round(time.time() * 1000)
            head1, head2, data = self.parse(frame)

            if self.is_available(head1, head2, data):
                binary_num = int(data, 2)
                resized_num = resize(binary_num)
                if head1[0] == '0':
                    data = {
                        'ch': 1,
                        'num': resized_num
                    }
                    self.segment1.append(data)
                    self.jumped_check(0, binary_num)
                else:
                    data = {
                        'ch': 2,
                        'num': resized_num
                    }
                    self.segment2.append(data)
                    self.jumped_check(1, binary_num)
            else:
                # 无效的话就丢弃一帧，继续读
                self.port.read().hex()
            now = round(time.time() * 1000)
            if now - pre_time >= 50000:
                self.period[0] = len(self.segment1) * 10 / self.cnt[0]
                self.period[1] = len(self.segment2) * 10 / self.cnt[1]
                print(json.dumps({
                    'type': 'info',
                    'data': {
                        'label': 'period',
                        'period': [self.period[0], self.period[1]]
                    }
                }))

    def jumped_check(self, ch, current_binary_num):
        if current_binary_num >= self.maximum[ch]:
            self.maximum[ch] = current_binary_num * 0.9
        if current_binary_num <= self.minimum[ch]:
            self.minimum[ch] = 1024 - (1024 - current_binary_num) * 0.9
            self.jump_flag[ch] = True
        elif current_binary_num >= self.maximum[ch] and self.jump_flag[ch]:
            self.cnt[ch] += 1

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
