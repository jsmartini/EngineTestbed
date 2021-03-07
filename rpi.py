from .p2p2 import P2P2 as NET
import platform
from .util import load_config
import asyncio
from queue import LifoQueue as Stack
import pandas as pd
from Phidget22 import *
from Phidget22.Devices.VoltageRatioInput import VoltageRatioInput
import threading

if platform.system().upper() == "WINDOWS":
    #windows testing
    import RPiSim.GPIO as GPIO
else:
    #real hardware
    import RPi.GPIO as GPIO

global CONFIGURATION
global GPIOCFG
global GPIOVALVES
global GPIOPRESSURE
global GPIOLOADCELL
CONFIGURATION = load_config()
GPIOCFG = CONFIGURATION["GPIO"]
GPIOVALVES = GPIOCFG["valves"]
GPIOPRESSURE = GPIOCFG["pressure"]
GPIOLOADCELL = GPIOCFG["loadcell"]
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


#initialize gpio to either GPIO.HIGH (valves)
# the NO side of the 3-way solendoids defaults to a closed
# position when given a GPIO.HIGH voltage. Changing,
# the RPI gpio pin to low will signal the NC side
# of the 3-way solendoid valve to it's NC position
# opening the fluid valve

for system in GPIOVALVES.keys():
    GPIO.setup(GPIOVALVES[system], GPIO.OUT)
    GPIO.output(GPIOVALVES[system], GPIO.HIGH)


from abc import ABC, abstractmethod

class CMD:

    def __init__(self, cmd_dict:dict):
        self.cmd = cmd_dict

    def get_pins(self):
        return self.cmd["pins"]

    def get_new_states(self):
        return self.cmd["states"]

class GPIOHandler(ABC):
    states = {}
    LOX_Vent = False
    KEROSENE_Vent = False

    def __init__(self):
        pass

    @abstractmethod
    async def handler(self):
        while 1:
            pass

class PressureMonitor(GPIOHandler):

    """
    All pressure-based I/O will solely be
    Managed by this class (venting)
    """

    def __init__(self):
        super(PressureMonitor, self).__init__()
        self.logger = logging.getLogger("Pressure Monitor")

    async def handler(self):
        while 1:
            pass

class GPIOHypervisor(GPIOHandler):

    """
    All operation specific I/O will
    be managed by this class
    """

    def __init__(self):
        super(GPIOHypervisor, self).__init__()
        self.cmd = Stack(maxsize=4)
        self.logger = logging.getLogger("GPIO Hypervisor")

    def put(self, cmd: CMD):
        self.cmd.put_nowait()

    def get_new_cmd(self):
        return self.cmd.get_nowait()

    async def handle(self):
        pass

class LoadCell(object):

    def __init__(self):
        pass

    async def log(self):
        pass

class HyperVisor(object):

    def __init__(self):
        self.net = NET(auto_start_threading=False)
        self.PressureMonitor = PressureMonitor()
        self.GPIOHypervisor = GPIOHypervisor()
        self.LoadCell = LoadCell()
        self.start_pressure_monitor()

    async def handler(self):
        while 1:
            pass

    def start_pressure_monitor(self):
        self.pressure_loop = asyncio.new_event_loop()
        threading.Thread(target=self.pressure_loop).start()
        self.pressure = asyncio.run_coroutine_threadsafe(self.PressureMonitor.handler(), self.pressure_loop)

    async def main(self):
        return asyncio.gather(*[
            self.LoadCell.log(),
            self.handler(),
            self.GPIOHypervisor.handler(),
            self.net._send_thread(),
            self.net._recv_thread()
        ])

def main():
    hype = HyperVisor()

    loop_default = asyncio.get_event_loop()
    loop_default.run_until_complete(hype.main())

import logging

if __name__ == "__main__":
    logging.basicConfig(filename="Test.log", level=logging.INFO)

    main()


