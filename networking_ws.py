import websockets as ws
import asyncio
from queue import LifoQueue as Stack
import logging
import pickle

global LOGGER
LOGGER = logging.getLogger()

def fcmd(mode):
    return {"cmd":mode}

class NetworkClient(object):

    def __init__(self, target):
        self.target = target
        self.RECV = Stack(maxsize=256)
        self.SEND = Stack(maxsize=256)

    def cmd(self, CMD):
        """
        send a cmd object to send buffer
        :param CMD:
        :return:
        """
        self.SEND.put_nowait(pickle.dumps(CMD))

    def data(self):
        if not self.RECV.empty():
            return pickle.loads(self.RECV.get_nowait())
        else:
            return None

    async def _data(self, websocket):
        data = await websocket.recv()
        self.RECV.put_nowait(data)

    async def _cmd(self, websocket):
        if not self.SEND.empty():
            await websocket.send(self.SEND.get_nowait())
        await asyncio.sleep(0.1)

    async def clienthandler(self):
        while 1:
            async with ws.connect(self.target) as websocket:
                while 1:
                    recv = asyncio.ensure_future(self._cmd(websocket))
                    send = asyncio.ensure_future(self._data(websocket))
                    done, pending = await asyncio.wait(
                        [send, recv],
                        return_when=asyncio.FIRST_COMPLETED
                    )
                    for task in pending:
                        task.cancel()
            await asyncio.sleep(0.1)


class NetworkServer(object):
    """
    sends data and listens for commands
    """
    def __init__(self):
        LOGGER.debug(f"{self}")
        self.SEND = Stack(maxsize=256)
        self.CMD = Stack(maxsize=256)

    def data(self, data):
        self.SEND.put_nowait(pickle.dumps(data))

    def cmd(self):
        if not self.CMD.empty():
            return pickle.loads(self.CMD.get_nowait())
        return None

    async def _cmd(self, websocket, path):
        cmd = await websocket.recv()
        self.CMD.put_nowait(cmd)

    async def _data(self, websocket, path):
        if not self.SEND.empty():
            await websocket.send(self.SEND.get_nowait())

    async def handler(self, websocket, path):
        recv = asyncio.ensure_future(self._cmd(websocket, path))
        send = asyncio.ensure_future(self._data(websocket, path))
        done, pending = await asyncio.wait(
            [send, recv],
            return_when=asyncio.FIRST_COMPLETED
        )
        for task in pending:
            task.cancel()

if __name__ == "__main__":

    v = input("server?")
    if v == "y":
        n = NetworkServer()
        l = asyncio.get_event_loop()
        l.run_until_complete(ws.serve(n.handler, "localhost", 4444))
        l.run_forever()
    if v == "n":
        uri = "ws://127.0.0.1:4444"
        n = NetworkClient(uri)
        l = asyncio.get_event_loop()
        l.run_until_complete(asyncio.gather(n.clienthandler()))
