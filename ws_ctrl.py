import json
import threading

import websocket


class WebSocketCtrl(object):
    is_open = False
    _serial = None

    def __init__(self, ip, port):
        self.ws = websocket.WebSocketApp(f'ws://{ip}:{port}',
                                         on_message=WebSocketCtrl.on_message,
                                         on_open=WebSocketCtrl.on_open,
                                         on_close=WebSocketCtrl.on_close
                                         )
        WebSocketCtrl.is_open = False

    def send(self, message):
        if WebSocketCtrl.is_open:
            self.ws.send(json.dumps(message))

    @staticmethod
    def on_open(ws):
        print('ws connection opened')
        WebSocketCtrl.is_open = True

    @staticmethod
    def on_close(ws):
        WebSocketCtrl.is_open = False

    @staticmethod
    def on_message(ws, message):
        print(f"Received: {message}")
        msg = json.loads(message)
        if msg['type'] == 'model':
            print('set mode')
            mode = msg['data']
            WebSocketCtrl._serial.set_mode(mode)
        elif msg['type'] == 'voltage':
            print('set voltage')
            voltage = msg['data']
            WebSocketCtrl._serial.set_clock(voltage)
        elif msg['type'] == 'clock':
            print('set clock')
            clock = int(msg['data'])
            WebSocketCtrl._serial.set_clock(clock)

    def set_serial(self, serial):
        WebSocketCtrl._serial = serial

    def start(self):
        print('ws ctl start')
        t = threading.Thread(target=self.ws.run_forever)
        t.start()
