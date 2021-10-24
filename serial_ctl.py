import json
import threading
import time
import asyncio
import numpy as np
import serial
from scipy.fftpack import fft


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
        self.mode = 1

    def set_hook(self, hook):
        self._hook = hook

    def set_mode(self, mode):
        self.mode = mode
        self.send('0fff')

    """
    给示串口发送: 
    前端发送个0fff进入逻辑分析模式/示波器模式，然后发送f___和0___表示时钟分频的倍数，例如f123 0456 那么时钟分频为十六进制123456

    如果发送1___,低12位代表阈值电压，不发送的话就是默认电压
    从串口接收: 
    000_____ 010_____ 代表通道一，100_____ 110_____代表通道二,但是每一个0/1都代表一个数据.

    意思就是说一次发送10个数据，发两个通道


    """

    def send(self, data):
        bdata = bytes.fromhex(data)
        print(f'writing data {bdata}')
        self.port.write(bdata)

    def set_clock(self, clock):
        clock = int(clock) * 1000
        frequency_divider = 2.5e7 / clock
        frequency_divider_str = hex(round(frequency_divider))[2:].zfill(6)
        command = f"f{frequency_divider_str[:3]}0{frequency_divider_str[-3:]}"
        self.send(command)

    def set_voltage(self, voltage):
        voltage = hex(voltage)[2:].zfill(3)
        command = f"1{voltage}"
        self.send(command)

    def recv(self):
        while True:
            if len(self.segment1) >= 100:

                data = {
                    'type': self.mode,
                    'ch': 1,
                    'data': self.segment1
                }
                if self.mode == 1:
                    z = fft(self.segment1)
                    z = np.abs(z[:round(len(z) / 2)]) / len(z)
                    z = z.tolist()
                    data['fft'] = z
                if self._hook is not None:
                    self._hook(data)
                self.segment1 = []
            if len(self.segment2) >= 100:
                data = {
                    'type': self.mode,
                    'ch': 2,
                    'data': self.segment2
                }
                if self.mode == 1:
                    z = fft(self.segment2)
                    z = np.abs(z[:round(len(z) / 2)]) / len(z)
                    z = z.tolist()
                    data['fft'] = z
                if self._hook is not None:
                    self._hook(data)
                self.segment2 = []
            frame = self.read_available_2byte()
            print(frame)
            head1, head2, raw_data = self.parse(frame)
            if self.is_available(head1, head2, raw_data):
                binary_num = int(raw_data, 2)
                if self.mode == 1:
                    dd = resize(binary_num)
                else:
                    dd = raw_data
                if head1[0] == '0':
                    self.segment1.append(dd)
                else:

                    self.segment2.append(dd)

    def read_available_2byte(self):
        frame = self.read_str_bytes()
        while frame[:3] not in ('100', '000'):
            frame = self.read_str_bytes()

        frame += self.read_str_bytes()
        return frame

    def read_str_bytes(self, num=1):
        frame = self.port.read(num).hex()
        str_frame = int(frame, 16)
        str_frame = bin(str_frame)[2:].zfill(8 * num)
        return str_frame

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
        :return: 数据帧是否是有效的
        """
        # 判断数据帧是否有效的
        if head1[0] == head2[0]:
            if head1[1] == '0' and head2[1] == '1':
                # print(f"head1: {head1}, head2: {head2}, data: {data}")
                return True
        return False

    def parse(self, frame):
        head1 = frame[:3]
        head2 = frame[8:11]
        data = frame[3:8] + frame[11:]
        return head1, head2, data

    def loop_recv(self):
        print('serial listening')
        t = threading.Thread(target=self.recv)
        t.start()


if __name__ == '__main__':
    ser = SerialPort('COM6', 115200, 2)
    ser.loop_recv()
