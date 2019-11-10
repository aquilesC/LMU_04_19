import os
import time
import numpy as np
import yaml
from model.daq.analog_daq import AnalogDaq
from model.daq.dummy_daq import dummyDaq

from datetime import datetime

from model import ur


class IVExperiment:
    def __init__(self):
        self.scan_running = False

    def load_config(self, filename):
        with open(filename, 'r') as f:
            self.params = yaml.load(f)

    def load_daq(self):
        port = self.params['Params']['port']
        resistance = ur(self.params['Params']['resistance'])
        if self.params['Params']['device_type'] == 'real':
            self.daq = AnalogDaq(port, resistance)
        elif self.params['Params']['device_type'] == 'dummy':
            self.daq = dummyDaq(port, resistance)
        else:
            raise Exception('Daq device not recognized')


    def do_scan(self):
        if self.scan_running:
            print('Scan already running')
            return
            # raise Exception("Scan already running")

        self.scan_running = True
        start = ur(self.params['Scan']['start'])
        stop = ur(self.params['Scan']['stop'])
        step = ur(self.params['Scan']['step'])
        self.voltages = np.arange(start.m_as('V'), stop.m_as('V')+step.m_as('V'), step.m_as('V'))
        self.currents = np.zeros((len(self.voltages)))

        for i in range(len(self.voltages)):
            channel = self.params['Scan']['channel_out']
            self.daq.set_voltage(channel, self.voltages[i]*ur('V'))

            channel_in = self.params['Scan']['channel_in']
            current = self.daq.read_current(channel_in)
            self.currents[i] = current.m_as('A')

            delay = ur(self.params['Scan']['delay'])
            time.sleep(delay.m_as('s'))
        self.scan_running = False

    def plot_data(self):
        pass

    def save_data(self, filename=None):
        if not hasattr(self, 'currents'):
            print('Still no currents acquired')
            return

        if not isinstance(filename, str):

            folder_name = '{:%Y-%m-%d}'.format(datetime.now())
            final_folder = os.path.join(self.params['Saving']['path'], folder_name)

            if not os.path.isdir(final_folder):
                os.makedirs(final_folder)

            fname = self.params['Saving']['filename']
            i = 0
            while os.path.exists(os.path.join(final_folder, fname)):
                fname = self.params['Saving']['filename'] + str(i)
                i = i+1

            filename = os.path.join(final_folder, fname)
        np.savetxt(filename, self.currents)

    def save_plot(self, filename):
        pass

    def save_metadata(self, filename):
        with open(filename, 'w') as f:
            yaml.dump(self.params, f)