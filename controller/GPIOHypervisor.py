import platform
from ruamel.yaml import YAML
from queue import LifoQueue as STACK
import asyncio
if platform.system().upper() == "WINDOWS":
    #DEVELOPMENT AND DEGUGGING FOR GPIO SYSTEM ON WINDOWS
    import RPiSim.GPIO as GPIO
else:
    #TESTING AND DEPLOY
    import RpiGPIO as GPIO

def load(cfg_path):
    cfg = YAML()
    with open(cfg_path, 'r') as f:
        cfg.load(f)
        return cfg["control_variables"]

class GPIOHypervisor:

    COMMAND_BUFFER = STACK(max=2048)
    DATA_BUFFER    = STACK(max=2048)

    def __init__(self, cfg_path:str):
        self.cfg = load(cfg_path)
        self.status = dict.fromkeys(
            ["gpio_status", "data_status", "system_status"]
        )
    def cmd(self, cmd:dict):
        pass

    def _push_data(self, data):
        pass

    def get_Latest_data(self):
        pass

    def get_status(self):
        return self.status

    def _EMERGENCY_FAILSAFE(self):
        pass

    async def GPIO_loop(self):
        while True:
            self._push_data(self.get_Latest_data())
            if not self.COMMAND_BUFFER.empty():
                pass


if __name__ == "__main__":
    #testing
    pass

