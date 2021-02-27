import logging
import asyncio
from p2pnet import Net
from HardwareManager import HardwareManager

class RPiManager(HardwareManager):

    def __init__(self, cfg, net: Net):
        super().__init__(self, cfg, net=net)
        self.logger = logging.getLogger("RPiManager")

    async def Control(self):
        while 1:
            r = super().net.recv()
            if r != None:
                super().cmd(r["cmd"])

    async def Report(self):
        while 1:
            super().net.to_send(
                {
                    "Type": "States",
                    "States": super().report_states()
                }
            )
            super().net.to_send(
                {
                    "Type": "Data",
                    "Data": super().report_data()
                }
            )
