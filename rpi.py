from .p2p2 import P2P2 as NET
import platform
from .util import load_config
import asyncio
from queue import LifoQueue as Stack
import pandas as pd
from Phidget22 import *
from Phidget22.Devices.VoltageRatioInput import VoltageRatioInput
import threading
from time import sleep
import logging
import pickle

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
global DUMP
CONFIGURATION = load_config()
GPIOCFG = CONFIGURATION["GPIO"]
GPIOVALVES = GPIOCFG["valves"]
GPIOPRESSURE = GPIOCFG["pressure"]
GPIOLOADCELL = GPIOCFG["loadcell"]
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
DUMP = pickle.dumps

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
        self.name = cmd_dict["directive"]

    def get_pins(self):
        return self.cmd["pins"]

    def get_new_states(self):
        return self.cmd["states"]

    def __str__(self):
        return self.name

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

    data = pd.DataFrame(["time", "pressure_lox", "pressure_kerosene"])

    def vent(self, valve, time_ms:float):
        GPIO.output(valve, GPIO.LOW)
        super().states[f"pin{valve}"] = 0
        self.logger.info(f"VENTING {valve}, time:{time_ms}ms")
        sleep(time_ms/1000)
        GPIO.output(valve, GPIO.HIGH)
        self.logger.info(f"FINISHED VENTING {valve}")
        super().states[f"pin{valve}"] = 1

    def __init__(self):
        super(PressureMonitor, self).__init__()
        self.logger = logging.getLogger("Pressure Monitor")

    async def handler(self):
        while 1:
            pass

    def backup(self):
        pass

    def report(self):
        self.backup()
        return self.data.iloc[-20:-1] #return last 20 entries


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

    def execute(self, cmd:CMD):
        newStates = cmd.get_new_states()
        pins = cmd.get_pins()
        GPIO.output(pins, list([GPIO.LOW if i == 0 else GPIO.HIGH for i in newStates]))
        for pin_states in self.states:
            for idx, pin in enumerate(pins):
                if pin_states == str(pin):
                    self.states[pin_states] = newStates[idx]

    def update_states(self, pin, output):
        self.states[str(pin)] = output

    async def handle(self):
        while 1:
            if not self.cmd.empty():
                cmd = self.get_new_cmd()
                if str(cmd) == "ENGINESTART":
                    GPIO.output(GPIOVALVES["lox_dump"]["pin"], GPIO.LOW)
                    self.update_states(GPIOVALVES["lox_dump"]["pin"], 0)
                    self.logger.info("DUMPING LOX")
                    sleep(GPIOVALVES["engine_start_delay"]["time_ms"])
                    GPIO.output(GPIOVALVES["kerosene_dump"]["pin"], GPIO.LOW)
                    self.update_states(GPIOVALVES["kerosene_dump"]["pin"], 0)
                    self.logger.info("DUMPING KEROSENE")
                    GPIO.output(GPIOVALVES["igniter"]["pin"], GPIO.HIGH)
                elif str(cmd) == "ENGINESTOP":
                    GPIO.output(GPIOVALVES["lox_dump"]["pin"], GPIO.HIGH)
                    self.update_states(GPIOVALVES["lox_dump"]["pin"], 1)
                    self.logger.info("STOPPING LOX")
                    GPIO.output(GPIOVALVES["kerosene_dump"]["pin"], GPIO.HIGH)
                    self.update_states(GPIOVALVES["kerosene_dump"]["pin"], 1)
                    self.logger.info("STOPPING KEROSENE")
                else:
                    #general non-mission critical gpio commands
                    self.execute(cmd)
            else:
                await asyncio.sleep(0.1)

    def report(self):
        return self.states

class LoadCell(object):

    data = pd.DataFrame(["time", "load"])

    def __init__(self):
        pass

    async def log(self):
        pass

    def backup(self):
        pass

    def report(self):
        self.backup()
        return self.data


class HyperVisor(object):

    def __init__(self):
        self.net = NET(auto_start_threading=False)  #not mission critical
        self.PressureMonitor = PressureMonitor()    #mission critical
        self.GPIOHypervisor = GPIOHypervisor()  #not mission critical
        self.LoadCell = LoadCell()  #not mission critical
        self.start_pressure_monitor() #mission critical

    async def handler(self):
        global DUMP
        while 1:
            statistics = {
                "pressure":DUMP(self.PressureMonitor.report()),
                "gpio": DUMP(self.GPIOHypervisor.report()),
                "loadcell": DUMP(self.LoadCell.report())
            }
            self.net.send(statistics)
            if (r := self.net.recv()) != None:
                if "cmd" in r.keys():
                    self.GPIOHypervisor.put(r["cmd"])
            await asyncio.sleep(0.1)

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


if __name__ == "__main__":
    logging.basicConfig(filename="Test.log", level=logging.INFO)
    main()


