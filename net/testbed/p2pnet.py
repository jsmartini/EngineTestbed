from py2p import MeshSocket
from queue import LifoQueue as stack
import logging
from time import sleep
import asyncio
import json

class Net:

    recvbuff = stack(maxsize=512)
    sendbuff = stack(maxsize=512)

    socket = MeshSocket(
        '127.0.0.1',
        port=4444,
    )

    def __init__(self, target, port, tries = 100, node_type = True):
        """

        py2p documentation (p2p-project)
        https://dev-docs.p2p.today/python/tutorial/mesh.html

        :param target: target computer
        :param port: target port
        :param tries: timeout
        :param node_type: True -> initially connecting, False -> initially listening
                -if both try to connect at once it disconnects both

        """
        self.logger = logging.getLogger("Network")
        if node_type:
            for i in range(tries):
                try:
                    self.socket.connect(target, port)
                    self.logger.info(f"Connected to {target}:{port}")
                except BaseException as e:
                    self.logger.info(f"\rFailed to Connect to {target}:{port} ({i}/{tries})")
        else:
            while not self.socket.routing_table:
                sleep(1)

    @socket.on("connect")
    def connection(self):
        self.logger.info(f"Connected to {self.socket.routing_table.keys()}")

    @socket.on("message")
    def handle_msg(self, conn):
        msg = conn.recv()
        if msg is not None:
            assert len(msg) == 2
            self.recvbuff.put_nowait(msg.packets[1])

    def _recv(self):
        if not self.recvbuff.empty():
            return json.loads(self.recvbuff.get_nowait())
        return None

    def _send(self, data:dict):
        data = json.dumps(data)
        self.sendbuff.put_nowait(data)

    async def send(self):
        while True:
            if not self.sendbuff.empty():
                data = self.sendbuff.get_nowait()
                assert type(data) == str
                self.socket.send(data)
            await asyncio.sleep("0.01")






