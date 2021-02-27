from py2p import mesh
import socket
from queue import LifoQueue as stack
import asyncio
import pickle
import threading

def get_ip_address():
    #from stackoverflow cause Im lazy
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

class P2P:

    def __init__(self, target, port, szbuff=2048):
        self.wbuff = stack(maxsize=szbuff)
        self.rbuff = stack(maxsize=szbuff)
        self.socket = mesh.MeshSocket(get_ip_address(), port)
        self.t, self.p = target, port
        self.loop1 = asyncio.new_event_loop()
        threading.Thread(target=self.loop1.run_forever).start()
        f1 = asyncio.run_coroutine_threadsafe(self._send_thread(), self.loop1)
        self.loop2 = asyncio.new_event_loop()
        threading.Thread(target=self.loop2.run_forever).start()
        f2 = asyncio.run_coroutine_threadsafe(self._recv_thread(), self.loop2)

    def __del__(self):
        #absolute fucking trainwreck
        self.loop1.call_soon_threadsafe(self.loop1.stop)
        self.loop2.call_soon_threadsafe(self.loop2.stop)

    def connect(self):
        try:
            self.socket.connect(self.t, self.p)
        except BaseException as e:
            print(e)

    async def _recv_thread(self):
        while 1:
            msg = self.socket.recv()
            if msg != None:
                self.rbuff.put(pickle.loads(msg.packets[1]))

    async def _send_thread(self):
        while 1:
            if not self.wbuff.empty():
                self.socket.send(
                    pickle.dumps(self.wbuff.get())
                )

    def send(self, data):
        self.wbuff.put_nowait(data)

    def recv(self):
        if not self.rbuff.empty():
            return self.rbuff.get_nowait()
        return None

if __name__ == "__main__":
    net = P2P("192.168.1.215", 4444)
    while 1:
        msg = input(">>")
        net.send(msg)
        r = net.recv()
        if r != None:
            print(r)

