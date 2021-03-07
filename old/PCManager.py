from tkinter import *
from old.p2pnet import Net
import matplotlib.pyplot as plt
import logging

plt.style.use('ggplot')

class PCManager:

    time = []
    pressure = []
    thrust = []

    def __init__(self, net: Net):
        self.net = net
        self.logger = logging.getLogger("Manager")



    async def main(self):
        window = Tk()







