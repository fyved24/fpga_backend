import multiprocessing
from serial_ctl import SerialPort
import matplotlib.pyplot as plt  # 导入
import seaborn as sns
import json

from ws_server import server as ws_server
from ws_ctrl import WebSocketCtrl

sns.set(color_codes=True)  # 导入seaborn包设定颜色

Y = []
Y2 = []


def send_to_frontend(frame):
    global Y
    global Y2
    data_list = frame.get('data')
    print('send_to_frontend')
    print(frame)

    for data in data_list:
        ch = data.get('ch')
        num = data.get('num')
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
        plt.pause(0.001)


def save_to_file(frame):
    data = frame.get('data')
    num = int(data, 2)
    num = round((num - 511) / (511 / 5), 2)
    frame['data'] = num
    with open('file.json', 'a+') as f:
        print(frame)
        f.write(json.dumps(frame) + '\n')


if __name__ == '__main__':
    ser = SerialPort('COM5', 115200, 2)
    # db = DbCtl(buf)
    ser.loop_recv()
    # db.loop_save()
    # 开启websocket 服务
    t = multiprocessing.Process(target=ws_server)
    t.start()
    ws = WebSocketCtrl('localhost', 8765)
    ws.set_serial(ser)
    ws.start()
    # db.set_hook(ws.send)
    ser.set_hook(send_to_frontend)
    t.join()
