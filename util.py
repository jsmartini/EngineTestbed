from ruamel.yaml import YAML
import logging
import asyncio
import os
from queue import LifoQueue as stack
import json
from sys import getsizeof as sizeof
import threading
import pickle

def load_config(cfg = "config.yaml"):
    y = YAML()
    with open(cfg, "r") as f:
        config = y.load(f)
        return config

def init_logger(logfile:str, level = logging.INFO):
    logging.basicConfig(filename=logfile, level=level)
    logging.getLogger("init_logger").info(f"Logger initialized, logging to {logfile} @level={level}")

class DataBackup:

    buffer = stack(maxsize=2048)

    def __init__(self, config:dict):
        self.cfg = config["data"]
        self.cnt = 0
        self.logger = logging.getLogger("DataLogging")
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.loop.run_until_complete).start()
        f1 = asyncio.run_coroutine_threadsafe(self.BackupLoop(), self.loop)


    def dump(self, data):
        self.buffer.put_nowait(pickle.dumps(data))

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
