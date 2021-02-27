from py2p import MeshSocket
from queue import LifoQueue as stack
import logging
from time import sleep
import asyncio
import json
from util import DataBackup
import socket

def get_ip_address():
    #from stackoverflow cause Im lazy
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

class Net:

    recvbuff = stack(maxsize=512)
    sendbuff = stack(maxsize=512)

    socket = MeshSocket(
        get_ip_address(),
        port=4444,
    )

    def __init__(self, target, port, tries = 100, node_type = True, data_backup = None):
        """

        py2p documentation (p2p-project)
        https://dev-docs.p2p.today/python/tutorial/mesh.html

        :param target: target computer
        :param port: target port
        :param tries: timeout
        :param node_type: True -> initially connecting, False -> initially listening
                -if both try to connect at once it disconnects both

        """

        self.logger = logging.getLogger("Networking")
        if node_type:
            for i in range(tries):
                try:
                    self.socket.connect(target, port)
                    self.logger.info(f"Connected to {target}:{port}")
                except BaseException as e:
                    self.logger.info(f"\rFailed to Connect to {target}:{port} ({i}/{tries})")
            if not self.socket.routing_table:
                raise("Could Not Connect")
        else:
            while not self.socket.routing_table:
                self.logger.info("Waiting for Connection")
                sleep(1)
            self.logger.info("Connected")
        if isinstance(data_backup, DataBackup):
            self.data_backup = data_backup
        else:
            self.data_backup = None

    @socket.on("connect")
    def connection(self):
        self.logger.info(f"Connected to {self.socket.routing_table.keys()}")

    @socket.on("message")
    def handle_msg(self, conn):
        msg = conn.recv()
        self.logger.debug(f"Received {msg}")
        if msg is not None:
            assert len(msg) == 2
            self.recvbuff.put_nowait(msg.packets[1])

    def recv(self):
        if not self.recvbuff.empty():
            data = json.loads(self.recvbuff.get_nowait())
            if self.data_backup != None:
                self.data_backup.dump(data)
            return data
        return None

    def to_send(self, data:dict):
        data = json.dumps(data)
        self.sendbuff.put_nowait(data)

    async def send(self):
        while True:
            if not self.sendbuff.empty():
                data = self.sendbuff.get_nowait()
                assert type(data) == str
                self.socket.send(data)
                self.logger.debug(f"Sent {data}")
            await asyncio.sleep("0.01")






