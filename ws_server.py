import asyncio
import json
import threading

from websockets import serve


class WsServer(object):
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.ws = None

    def start(self):
        print('websocket server started')

        async def echo(websocket, path):
            self.ws = websocket
            async for message in websocket:
                print(self)
                await websocket.send(message)

        async def main(ip, port):
            async with serve(echo, ip, port):
                await asyncio.Future()  # run forever

        asyncio.run(main(self.ip, self.port))

    def loop(self):
        t = threading.Thread(target=self.start)
        t.start()
        t.join()

    def send(self, message):
        print(f'send {message}')
        message = json.dumps(message)

        asyncio.get_event_loop().run_until_complete(self.ws.send(message))


if __name__ == '__main__':
    server = WsServer('localhost', 8765)
    server.loop()
