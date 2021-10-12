import json
import threading

import websocket


class WebSocketCtrl(object):
    def __init__(self, ip, port):
        self.ws = websocket.WebSocketApp(f'ws://{ip}:{port}',
                                         on_message=self.on_message)
        self._hook = None

    def send(self, message):
        self.ws.send(json.dumps(message))

    def on_message(self, ws, message):
        print(f"Received: {message}")
        if self._hook is not None:
            self._hook(message)

    def set_hook(self, hook):
        self._hook = hook

    def start(self):
        print('ws ctl start')
        t = threading.Thread(target=self.ws.run_forever)
        t.start()
