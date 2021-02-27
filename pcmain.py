from p2pnet import Net
from util import DataBackup, init_logger, load_config
import asyncio

async def main():
    config = load_config()
    init_logger("pc.log")
    #setup networking
    datalogging = DataBackup(config=config)
    net = Net(
        target=config["net"]["target"],
        port=config["net"]["port"],
        node_type=True,
        data_backup=datalogging
    )

    async_methods = [
        net.send(),
        datalogging.BackupLoop(),
    ]
    return asyncio.gather(*async_methods)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())