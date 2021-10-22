import json
import threading

import websocket


class WebSocketCtrl(object):
    def __init__(self, ip, port):
        self.ws = websocket.WebSocketApp(f'ws://{ip}:{port}',
                                         on_message=self.on_message)
        self._serial = None

    def send(self, message):
        self.ws.send(json.dumps(message))

    def on_message(self, ws, message):
        print(f"Received: {message}")
        msg = json.loads(message)
        if msg['type'] == 'model':
            mode = msg['data']
            self._serial.set_mode(mode)
        elif msg['type'] == 'voltage':
            voltage = msg['data']
            self._serial.set_clock(voltage)
        elif msg['type'] == 'clock':
            clock =  int(msg['data'])
            self._serial.set_clock(clock)


    def set_serial(self, serial):
        self._serial = serial

    def start(self):
        print('ws ctl start')
        t = threading.Thread(target=self.ws.run_forever)
        t.start()
