from serial_ctl import SerialPort
from db_ctrl import DbCtl
import threading
from queue import Queue


def send_to_frontend(data):
    print('send_to_frontend')
    print(data)


if __name__ == '__main__':
    # a buf used for data from com5

    ser = SerialPort('COM5', 115200, 2)
    buf = ser.buf
    db = DbCtl(buf)
    ser.loop_recv()
    db.loop_save(send_to_frontend)
