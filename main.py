from serial_ctl import SerialPort
from db_ctrl import DbCtl
import math
import matplotlib.pyplot as plt  # 导入

import seaborn as sns

sns.set(color_codes=True)  # 导入seaborn包设定颜色

Y = []
plt.ion()


def send_to_frontend(data):
    global Y
    print('send_to_frontend')
    num = int(data, 2)
    print(num)
    Y.append(num)
    Y = Y[-1000:]
    plt.clf()
    plt.plot(Y)
    plt.pause(0.01)
    plt.ioff()


if __name__ == '__main__':
    # a buf used for data from com5

    ser = SerialPort('COM5', 115200, 2)
    buf = ser.buf1
    db = DbCtl(buf)
    ser.loop_recv()
    db.loop_save(send_to_frontend)
