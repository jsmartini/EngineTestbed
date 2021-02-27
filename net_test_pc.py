from p2pnet import Net
import logging
import asyncio

if __name__ == "__main__":
    logging.basicConfig(filename="net_test_pc.log", level=logging.INFO)
    net = Net(
        "192.168.1.215",
        4444
    )

    async def main():
        while 1:
            msg = input("PC>>")
            net.to_send(msg)
            msg = net.recv()
            print(f"RPI:{msg}")
    asyncio.get_event_loop()\
        .run_until_complete(
        asyncio.gather(*[
            net.send(),
            main()
        ])
    )
