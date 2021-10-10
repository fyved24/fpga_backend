import threading

import websocket


def on_message(ws, message):
    print(f"Received: {message}")


def on_open(ws):
    def process():
        while True:
            s = input('输入: ')
            if s == '':
                break
            ws.send(s)
        ws.close()
        print('ws closed!')
    threading.Thread(target=process).start()


ws = websocket.WebSocketApp('ws://localhost:8765',
                            on_message=on_message,
                            on_open=on_open)
ws.run_forever()
