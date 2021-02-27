import platform
import logging
from p2pnet import Net
from smbus2 import SMBus, i2c_msg
from RPiManager import RPiManager
from Phidget22.Phidget import *
from Phidget22.Devices import VoltageRatioInput
from queue import LifoQueue as stack

if platform.system().upper() == "WINDOWS":
    #debugging virtual hardware
    import RPiSim.GPIO as GPIO
if platform.system().upper() == "LINUX":
    #hardware specific
    try:
        import RPi.GPIO as GPIO
    except RuntimeError:
        print("Run as Super User")

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

class HardwareManager:

    cmdbuffer = stack(max=64)

    #true -> on
    #false -> off
    states = {
        "pressurize_tanks": False,
        "lox_vent": False,
        "kerosene_vent": False,
        "lox_dump": False,
        "kerosene_dump": False,
        "shutdown": False,
        "emergency_shutdown":False
    }
    current_pressures = {
        "p1": 0,
        "p2": 0,
        "p3": 0,
        "p4": 0
    }

    def init_load_cell(self, cfg):
        self.lc = VoltageRatioInput()
        self.lc.setDeviceSerialNumber(cfg["serialnumber"])
        self.lc.setChannel(cfg["channel"])

    def __init__(self, cfg, net:Net):
        self.hcfg = cfg["rpi"]["GPIO"]
        self.net = net
        self.logger = logging.getLogger("Hardware")
        #init gpio
        for valve in self.hcfg["valves"].keys():
            GPIO.setup(self.hcfg[valve]["v"], GPIO.OUT, initial=GPIO.LOW)
        for sensor in self.hcfg["pressure"].keys():
            pass
        self.init_load_cell(self.hcfg["loadcell"])
        self.logger.info("Hardware Initialized")

    def report_states(self):
        return self.states

    def report_data(self) -> dict:
        pass

    async def collect_data(self):
        while 1:
            pass

    def cmd(self, cmd):
        self.cmdbuffer.put_nowait(cmd)

    def exec(self, cmd: str):
        """
        executes necessary hardware changes to cause system change
        :param cmd: string for selected hardware sequence
        :return: nothing
        """
        if cmd == "lox_vent":
            self.states["lox_vent"] = True
        elif cmd == "kerosene_vent":
            self.states["kerosene_vent"] = True
        elif cmd == "ignition":
            self.states["kerosene_dump"] = True
            self.states["lox_dump"] = True
        elif cmd == "kerosene_dump":
            self.states["kerosene_dump"] = True
        elif cmd == "lox_dump":
            self.states["lox_dump"] = True
        elif cmd == "pressurize":
            self.states["pressurize"] = True
        elif cmd == "shutdown":
            pass




