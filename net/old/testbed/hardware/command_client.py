from queue import LifoQueue as stack
import asyncio


global recv
global svr
recv = stack(maxsize=2048)
svr = ("staic", 999)

async def client():
    global recv
    r, w = await asyncio.open_connection()