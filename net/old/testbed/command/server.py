import asyncio
import asyncio.streams
import os


global read_dir
global sent_list
sent_list = []
read_dir = os.getcwd() + "/command_data/"

async def server():
    async def handle(reader, writer):
        global sent_list
        global read_dir
        while 1:
            for f in os.listdir(read_dir):
                if f not in sent_list:
                    with open(read_dir + f, "r") as data:
                        msg = data.read()
                        msg+= "\n"
                        msg = msg.encode()
                        writer.write(msg)
                        print(f"wrote {msg}")
                        await writer.drain()
                        sent_list.append(f)
            await asyncio.sleep(0.1)
    svr = await asyncio.start_server(handle, "localhost", 999)
    async with svr:
        await svr.serve_forever()



if __name__ == "__main__":
    print(os.listdir(read_dir))
    asyncio.run(server())