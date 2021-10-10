import asyncio
import json
import websockets
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK

users = []


async def register(ws):
    print(f"{ws} register ")
    message = f" hello {ws}"
    await ws.send(message)
    users.append(ws)
    print(users)


async def heartbeat(ws):
    message = json.dumps({"type": "heartbeat", "value": "pong"})
    while True:
        await ws.send(message)
        print("ping")
        hb_response = None
        hb_response = await asyncio.wait_for(ws.recv(), timeout=10)
        try:
            print(hb_response)
        except:
            raise Exception("Heartbeat break down")
        await asyncio.sleep(5)


async def send_data(ws):
    for i in range(6):
        data = json.dumps({"type": "data", "value": i})
        await ws.send(data)
        print("sent data: ", i)
        await asyncio.sleep(i)


async def recv_msg(ws):
    while True:
        try:
            msg = await ws.recv()
            await dispatch(ws, msg)
        except (ConnectionClosedOK, ConnectionClosedError, ConnectionResetError) as e:
            print(e)
            users.remove(ws)
            break


async def close_ws(ws):
    users.remove(ws)


async def dispatch(ws, message):
    for user in users:
        if ws != user:
            await user.send(message)


async def serve(ws, path):
    await register(ws)
    # await dispatch(ws, message)
    task1 = asyncio.create_task(recv_msg(ws))
    # task2 = asyncio.create_task(close_ws(ws))
    # task2 = asyncio.create_task(send_data(ws))
    # await task1
    await task1
    # await task2


def server():
    start_server = websockets.serve(serve, "localhost", 8765, ping_timeout=None)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

