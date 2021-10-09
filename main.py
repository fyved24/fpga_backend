import matplotlib

from serial_ctl import SerialPort
from db_ctrl import DbCtl
import math
import matplotlib.pyplot as plt  # 导入
import seaborn as sns
# matplotlib.use('Agg')

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
    if ch == 1:
        Y.append(num)
        Y = Y[-1000:]
        plt.figure(1)
        plt.clf()
        plt.plot(Y)
        plt.pause(0.01)
    else:
        Y2.append(num)
        Y2 = Y2[-1000:]
        plt.figure(2)
        plt.clf()
        plt.plot(Y2)
        plt.pause(0.01)


if __name__ == '__main__':
    # a buf used for data from com5

    ser = SerialPort('COM5', 115200, 2)
    buf = ser.buf
    db = DbCtl(buf)
    ser.loop_recv()
    db.loop_save(send_to_frontend)