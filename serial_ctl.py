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
        self.clock = 1
        self._hook = None
        self.mode = 1

    def set_hook(self, hook):
        self._hook = hook

    def set_mode(self, mode):
        if self.mode != mode:
            self.segment1 = []
            self.segment2 = []
            print(f'current mode {self.mode}')
            print(f'mode changed to {mode}')
            self.mode = mode
            if mode == 1:
                self.send('0ff0')
            elif mode == 2:
                self.send('0fff')

    def send(self, data):
        bdata = bytes.fromhex(data)
        print(f'writing data {bdata}')
        self.port.write(bdata)

    def set_clock(self, clock):
        print(f'clock changed to {clock}')
        self.clock = clock
        clock = float(clock) * 1000
        frequency_divider = 2.5e7 / clock
        frequency_divider_str = hex(round(frequency_divider))[2:].zfill(6)
        command = f"f{frequency_divider_str[:3]}0{frequency_divider_str[-3:]}"
        self.send(command)

    def set_voltage(self, voltage):
        print(f'set_voltage{hex(round(voltage*1000))}')
        voltage = hex(round(voltage*1000))[2:].zfill(3)
        command = f"1{voltage}"
        print(f'voltage changed to {command}')
        self.send(command)

    def send_ch_msg(self, ch, msg):
        data = {
            'type': self.mode,
            'ch': ch,
            'data': msg[:1024]
        }
        z = fft(msg)
        z = np.abs(z[:round(len(z) / 2)]) / len(z)
        z = z.tolist()
        data['fft'] = z
        if self._hook is not None:
            self._hook(data)

    def recv(self):
        while True:
            if len(self.segment1) >= 2000 :
                self.send_ch_msg(1, self.segment1)
                self.segment1 = []
            if len(self.segment2) >= 2000:
                self.send_ch_msg(2, self.segment2)
                self.segment2 = []
            if self.clock < 1:
                msg = self.segment1 + [0 for i in range(1024 - len(self.segment1))]
                self.send_ch_msg(1, msg)
                msg = self.segment2 + [0 for i in range(1024 - len(self.segment2))]
                self.send_ch_msg(2, msg)
                if len(self.segment1) > 1023:
                    self.segment1 = []
                if len(self.segment2) > 1023:
                    self.segment2 = []
            frame = self.read_available_2byte()
            # print(frame)
            head1, head2, raw_data = self.parse(frame)
            if self.is_available(head1, head2, raw_data):
                binary_num = int(raw_data, 2)
                if self.mode == 1:
                    dd = resize(binary_num)
                    if head1[0] == '0':
                        self.segment1.append(dd)
                    else:
                        self.segment2.append(dd)
                else:
                    if head1[0] == '0':
                        for x in raw_data:
                            self.segment1.append(int(x))
                            self.segment1.append(int(x))
                    else:
                        for x in raw_data:
                            self.segment2.append(int(x))
                            self.segment2.append(int(x))

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
        :return: ???????????????????????????
        """
        # ??????????????????????????????
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
