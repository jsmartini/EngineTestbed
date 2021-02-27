from asyncio import streams
import asyncio
import socket
import datetime
import pickle
import logging
import select
from queue import LifoQueue as stack



class hardwareNetwork:

    recvbuffer = stack(maxsize=2048)
    sendbuffer = stack(maxsize=2048)

    def __init__(self, addr):
        self.addr = addr
        self.logger = logging.getLogger()
        self.svr = socket.create_server(self.addr)
        self.svr.listen(5)
        self.logger.info("Successfully Created Server")
        self.conn, self.caddr = self.svr.accept()
        self.logger.info(f"Connected to {self.caddr}")


    async def net_send_loop(self):
        while 1:

            await asyncio.sleep(0.1)

    async def net_recv_loop(self):
        while 1:

            await asyncio.sleep(0.1)



if __name__ == "__main__":
    logging.basicConfig(filename="t.log", level=logging.INFO)
    hardwareNetwork(("", 999))