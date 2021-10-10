from websocket import create_connection

ws = create_connection("ws://localhost:8765")


def send(message):
    ws.send(message)
