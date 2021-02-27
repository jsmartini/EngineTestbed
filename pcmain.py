from p2pnet import Net
from util import DataBackup, init_logger, load_config

def main():
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


if __name__ == "__main__":
    main()