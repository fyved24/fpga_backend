import json

from websocket import create_connection


class WebSocketCtrl(object):
    def __init__(self, ip, port):
        self.ws = create_connection(f"ws://{ip}:{port}")

    def send(self, message):
        self.ws.send(json.dumps(message))
