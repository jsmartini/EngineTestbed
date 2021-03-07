from p2p2 import P2P2
import logging
import asyncio

if __name__ == "__main__":
    logging.basicConfig(filename="../net_test_pc.log", level=logging.INFO)
    net = P2P2(
        "192.168.1.215",
        4444
    )
    net.connect()
    print(net.socket.routing_table)
    async def main():
        while 1:
            msg = input("PC>>")
            net.send(msg)
            msg = net.recv()
            print(f"RPI:{msg}")
    asyncio.get_event_loop()\
        .run_until_complete(
        asyncio.gather(*[
            main()
        ])
    )
