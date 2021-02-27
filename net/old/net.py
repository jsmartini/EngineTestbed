from asyncio import streams
import asyncio
import socket
import datetime
import pickle
import logging
from queue import LifoQueue as stack

def pack(data, status:str):
    pickled = pickle.dumps(data)
    return pickled + b'\n'  #for streamReader.readline() : Read one line, where “line” is a sequence of bytes ending with \n.

class terminalNetwork:

    #tcp client

    recvbuffer = stack(maxsize=2048)
    sendbuffer = stack(maxsize=2048)

    def __init__(self, server):
        self.addr = server
        self.logger = logging.getLogger()

    async def conn(self):
        self.logger.info("Trying to Create Connection")

        self.r, self.w = await asyncio.open_connection(
            host=self.addr[0],
            port=self.addr[1]
        )
        self.logger.info(f"[terminalNetwork] Established Reader and Writer streams to server:\t{self.addr}")

    def read(self):
        if not self.recvbuffer.empty(): return self.recvbuffer.get_nowait()
        return None

    def write(self, data):
       self.sendbuffer.put_nowait(data)

    async def net_send_loop(self):
        self.logger.info("net_send_loop started")
        while 1:
            if not self.sendbuffer.empty():
                msg = self.sendbuffer.get_nowait()
                msg = pack(msg)
                self.w.write(msg)
                await self.w.drain()
                self.logger.info(f"[terminalNetwork] wrote {len(msg)} bytes to {self.w}")

    async def net_recv_loop(self):
        self.logger.info("net_recv_loop started")
        while 1:
            data = await self.r.readline()
            self.logger.info(f"[terminalNetwork] read {len(data)} bytes from {self.r}")
            data = pickle.loads(data)
            self.recvbuffer.put_nowait(data)


if __name__ == "__main__":
    logging.basicConfig(filename="terminalNetwork/t.log", level=logging.INFO)
    loop = asyncio.get_event_loop()
    conn = terminalNetwork(("127.0.0.1", 999))
    methods = [
        conn.conn(),
        conn.net_recv_loop(),
        conn.net_send_loop(),
    ]
    loop.run_until_complete(asyncio.gather(*methods))