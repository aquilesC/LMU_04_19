import numpy as np

from model import ur


class dummyDaq:
    def __init__(self, port, resistance):
        self.resistance = resistance

    def read_current(self, channel):
        current = np.random.randn()*ur('A')
        return current

    def set_voltage(self, channel, voltage):
        pass

    def finish(self):
        pass

