from p2p2 import P2P2
import logging
import asyncio
if __name__ == "__main__":
    logging.basicConfig(filename="net_test_rpi.log", level=logging.INFO)
    net = P2P2(
        "192.168.1.213",
        4444,
    )
    print(net.socket.routing_table)
    async def main():
        while 1:
            net.send(net.recv())
    asyncio.get_event_loop() \
        .run_until_complete(
        asyncio.gather(*[
            net.send(),
            main()
        ])
    )