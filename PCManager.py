from tkinter import *
import asyncio
from p2pnet import Net
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    FigureCanvasTk,
    FigureManagerTk
)
from matplotlib.figure import Figure
import logging

plt.style.use('ggplot')

class PCManager:

    time = []
    pressure = []
    thrust = []

    def __init__(self, net: Net):
        self.net = net
        self.logger = logging.getLogger("Manager")

    def pressure_animation(self, i):
        pass

    def load_anmiate(self, i):
        pass


    async def main(self):
        window = Tk()







