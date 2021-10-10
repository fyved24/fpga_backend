import asyncio
import websockets
import json
import time


async def dispatcher(ws):
    while True:
        try:
            msg = await ws.recv()
            print(msg)
        except Exception as e:
            print(e)


async def heartbeat(ws):
    while True:
        await ws.send("pong")
        await asyncio.sleep(5)


# async def foo(ws):
#     global data_pool
#     while True:
#         if len(data_pool):
#             data = data_pool.pop(0)  # 从数据池中去数据
#             print("start", time.time() - start_time)
#             await asyncio.sleep(5)
#             print("end", time.time() - start_time)
#             print(data)
#         await asyncio.sleep(5)  # 每5秒尝试从数据池中取一次数据
#

async def connect_server():
    url = "ws://localhost:8765"

    try:
        print("Initiate a connection")
        async with websockets.connect(url) as ws:
            task1 = asyncio.create_task(dispatcher(ws))
            task2 = asyncio.create_task(heartbeat(ws))
            await task1
            await task2
    except Exception as e:
        print(e)
        print("Connection break!")


asyncio.get_event_loop().run_until_complete(connect_server())
