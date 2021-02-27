from p2pnet import Net
import logging
import asyncio
if __name__ == "__main__":
    logging.basicConfig(filename="net_test_rpi.log", level=logging.INFO)
    net = Net(
        "",
        4444,
        node_type=False
    )
    async def main():
        while 1:
            net.to_send(net.recv())

    asyncio.get_event_loop() \
        .run_until_complete(
        asyncio.gather(*[
            net.send(),
            main()
        ])
    )