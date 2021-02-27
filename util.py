from ruamel.yaml import YAML
import logging
import asyncio
import os
from queue import LifoQueue as stack
import json
from sys import getsizeof as sizeof

def load_config(cfg = "config.yaml"):
    y = YAML()
    with open(cfg, "r") as f:
        y.load(f)
        return y

def init_logger(logfile:str, level = logging.INFO):
    logging.basicConfig(filename=logfile, level=level)
    logging.getLogger("init_logger").info(f"Logger initialized, logging to {logfile} @level={level}")

class DataBackup:

    buffer = stack(maxsize=2048)

    def __init__(self, config:dict):
        self.cfg = config["data"]
        self.cnt = 0
        self.logger = logging.getLogger("DataLogging")

    def dump(self, data:dict):
        self.buffer.put_nowait(data)

    def backup(self, data:dict):
        fname = f"{self.cnt}-{self.cfg['prefix']}.{self.cfg['postfix']}"
        data = json.dumps(data, indent=4)
        with open(fname, "w") as f:
            f.write(data)
            f.close()
        self.logger.debug(f"Wrote {sizeof(data)} bytes to {fname}")

    async def BackupLoop(self):
        while 1:
            if not self.buffer.empty():
                self.backup(self.buffer.get_nowait())
