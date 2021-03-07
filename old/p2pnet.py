from py2p import MeshSocket
from queue import LifoQueue as stack
import logging
from time import sleep
import asyncio
import json
from util import DataBackup
import socket
from uuid import uuid4

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
        try:
            self.logger = logging.getLogger("Networking")
            if node_type:
                i = 0
                while not self.socket.routing_table and i < tries:
                    try:
                        self.socket.connect(target, port)
                        self.logger.info(f"Connected to {target}:{port}")
                        break
                    except BaseException as e:
                        self.logger.info(f"\rFailed to Connect to {target}:{port} ({i}/{tries})")
                        i+=1
                if not self.socket.routing_table:
                    exit(-1)
            else:

                while not self.socket.routing_table:
                    self.logger.info("Waiting for Connection")
                    sleep(1)
                self.logger.info("Connected")
        except BaseException as e:
            print(e)
            print(self.socket.status)
        if isinstance(data_backup, DataBackup):
            self.data_backup = data_backup
        else:
            self.data_backup = None







