from serial_ctl import SerialPort
from db_ctrl import DbCtl
import matplotlib.pyplot as plt  # 导入
import seaborn as sns
import json

from ws_server import WsServer

sns.set(color_codes=True)  # 导入seaborn包设定颜色

Y = []
Y2 = []


def send_to_frontend(frame):
    global Y
    global Y2
    ch = frame.get('ch')
    data = frame.get('data')
    print(frame)
    print('send_to_frontend')
    num = int(data, 2)
    num = (num - 511) / (511 / 5)
    if ch == 1:
        Y.append(num)
        Y = Y[-1000:]

    else:
        Y2.append(num)
        Y2 = Y2[-1000:]

    plt.clf()
    plt.plot(Y, label='ch1')
    plt.plot(Y2, label='ch2')
    plt.xlabel('frame')
    plt.ylabel('num')
    plt.legend()
    plt.pause(0.01)


def save_to_file(frame):
    data = frame.get('data')
    num = int(data, 2)
    num = round((num - 511) / (511 / 5), 2)
    frame['data'] = num
    with open('file.json', 'a+') as f:
        print(frame)
        f.write(json.dumps(frame) + '\n')


if __name__ == '__main__':
    ws = WsServer('localhost', 8765)
    ser = SerialPort('COM5', 115200, 2)
    buf = ser.buf
    ser.set_hook(ws.send)
    db = DbCtl(buf)
    ser.loop_recv()
    db.loop_save()
    ws.loop()
