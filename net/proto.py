import asyncio
import pickle
from queue import LifoQueue as Stack
import logging
from time import sleep
import socket
import sys

def pack(data, status:str):
    pickled = pickle.dumps(data)
    return bytearray(f"ZZZ{str(status)}BBB{len(pickled)}C".encode()) + pickled

class CommunicationDaemon(object):
    """
    z9c structure           ||              socket server/client for cat5 wired communication adapted from z9c class @ deimos II avionics

    z9c.send -> non async send
    z9c._send -> send function for async processes
    z9c.to_send -> puts data packet into send buffer for auto_run to process
    z9c.recv -> base receiving and packet processing algorithm
    z9c.from_recv -> grabs latest data from recv buffer for async processes
    z9c.auto_run -> processes both requests for send and recv buffers with nowait for LIFO queue data structures (stack) asynchronouslys
    """


    #instance wide shared memory variables
    recv_buffer = Stack(maxsize=200)
    send_buffer = Stack(maxsize=200)

    def __init__(self, server, target):
        self.target_addr, self.server_addr = target, server
        self.logger = logging.getLogger()
        self.connection = False
        self.try_timeout = 50
        self.running = True
        self.logger.info(f"Connection Daemon Initialized @ client{target} @ server{server}")
        self.server = socket.create_server(address=self.server_addr, family=socket.AF_INET)

        self.logger.info(f"Server Created on {self.server_addr}")

    def send(self, data, status="CON"):
        """
        sends data to serial port
        :param data: python object
        :param status: connection status
        :return: bytes written
        """
        return self.c.sendall(pack(data, status=status))

    def _send(self, data: bytearray):
        return self.c.sendall(data)

    def to_send(self, data, status="CON"):
        self.send_buffer.put(pack(data, status))

    def recv(self, conn):
        """
        unpack algo for serial buffers

        slow algorithm

        originally made for asyncio; pyserial doesn't support asyncio; lots of unnecessary code
        :return:
        """
        flags = {"Z": 0, "B": 0}
        meta = {"status": "", "length": ""}
        def reset():
            """
            resets if data corruption detected via mis-matches
            :return: None
            """
            for i in flags.keys(): flags[i] = 0
            for i in meta.keys(): meta[i] = ""
            return (None, "CON")
        while True:
            if not len(conn.recv(1, socket.MSG_PEEK)) > 0: return (None, "CON")
            i = conn.recv(1)
            if chr(i) == "Z" and flags["Z"] < 3:
                flags["Z"] += 1
                continue
            elif flags["Z"] < 3 and chr(i) != "Z": reset()  #corruption condition
            # puts everything between Z & B into status string
            if flags["Z"] == 3 and chr(i) != "B" and len(meta["status"]) < 3:
                meta["status"] += chr(i)
                continue
            # cycles through B's until length
            if chr(i) == "B" and flags["B"] < 3:
                flags["B"] += 1
                continue
            elif flags["B"] < 3 and chr(i) != "B": reset() #corruption condition
            if flags["B"] == 3 and chr(i) != "C":
                meta["length"] += chr(i)
                continue
            if flags["B"] == 3 and chr(i) == "C":
                # return tuple (py object, status)
                #super().read(1) #kick "C" out of the serial buffer
                self.logger.debug(f"Attempting to load packet of size {meta['length']}")
                packet = (
                    pickle.loads(conn.recv(int(meta["length"]))),
                    meta["status"]
                )
                self.logger.debug(f"Received Packet of size {sys.getsizeof(packet[0])} Bytes with Network Status {packet[1]}")
                if packet[1] == "FIN":
                    self.logger.warning("Lost Connection, looking for devices")
                    self.connection = False
                elif packet[1] == "ACK" and self.connection:
                    #clear buffer of residual ACK packets
                    return self.recv()
                return packet

    async def auto_run(self):
        while 1:
            if (r := self.recv())[1] != "ACK" and r != (None, "CON"):
                self.recv_buffer.put(r)
            if not self.send_buffer.empty():
                self._send(self.send_buffer.get_nowait())
            await asyncio.sleep(0.15)


###########################################################################################

    #main program loops for cat5 I/O

    async def server_loop(self):
        self.server.listen()
        while self.running:
            self.logger.info(f"Attempting to Accept Connection")
            conn, addr = self.server.accept()
            self.logger.info(f"Connected to {addr}")
            with conn as c:
                if (r := self.recv(c))[1] != "ACK" and r != (None, "CON"):
                    self.recv_buffer.put_nowait(r)
            await asyncio.sleep(0.1)

    async def client_loop(self):
        tries = 50
        i = 0
        while i < tries:
            try:
                client = socket.create_connection(self.target_addr)
                client.setblocking(0)
                self.logger.info(f"Connected Successfully to {self.target_addr}")
                break
            except ConnectionRefusedError as e:
                self.logger.info(f"Tried Connecting to {self.target_addr}\t{i+1}/{tries} {str(e)[:16]}")
                if i == 49:
                    raise("Could Not Connect")
                i+=1

        while self.running:
            if not self.send_buffer.empty():
                pkt = pack(self.send_buffer.get_nowait())
                client.sendall(pkt)
                self.logger.info(f"Sent {self.target[0]}:{self.target[1]} {len(pkt)} bytes.")

            await asyncio.sleep(0.1)

#####################################################################################################
    def from_recv(self):
        #manual recv
        if self.recv_buffer.empty():
            return (None, "CON")
        else:
            return self.recv_buffer.get_nowait()

    def close_with_FIN(self):
        self.send("BYE!",status= "FIN")

async def main(methods:list):
    await asyncio.gather(*methods)

if __name__ == "__main__":
    logging.basicConfig(filename="test.log", level=logging.INFO, filemode="w")
    c = CommunicationDaemon(target=("127.0.0.1", 999), server=("127.0.0.1", 999))
    loop = asyncio.get_event_loop()
    async def main():
        coros = [c.client_loop(), c.server_loop()]
        res = await asyncio.gather(*coros)
    loop.run_until_complete(main())



