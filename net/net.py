import socketserver
import asyncio
from queue import LifoQueue as STACK
import pickle
import socket
import logging
import datetime

recvBuffer = STACK(max=512)
sendBuffer = STACK(max=512)
global recvBuffer
global sendBuffer

port = 9000
target = "192.168.1.2"
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", port))
global port
global client
global server
global target

dt = lambda : datetime.datetime.strftime("%y:%m:d--%H:%M:%S-")

def serialize(data):
    return pickle.dumps(data)

def deserialize(data):
    return pickle.loads(data)

def basicsave(data):
    with open(dt() + "packet.serialized", "r") as f:
        f.write(serialize(data))

def send(data):
    global sendBuffer
    sendBuffer.put_nowait(serialize(data))

def recv():
    global recvBuffer
    return recvBuffer.get_nowait()

async def server_loop():
    global server
    global recvBuffer
    server.listen()
    while 1:
        conn, addr = server.accept()
        logging.info(f"Connected to {addr}")
        while 1:
            with conn:
                data = conn.recv(1024)
                basicsave(data)
                recvBuffer.put_nowait(deserialize(data))

async def client_loop():
    global client
    global sendBuffer
    while 1:
        client.connect((target, port))
        while 1:
            if not sendBuffer.empty():
                client.sendall(serialize(sendBuffer.get_nowait()))


corountines = [client_loop, server_loop]

