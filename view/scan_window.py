from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5 import uic
import os
import threading

import pyqtgraph as pg


class ScanWindow(QMainWindow):
    def __init__(self, experiment):
        super().__init__()

        self.experiment = experiment
        this_dir = os.path.dirname(os.path.abspath(__file__))
        scan_file = os.path.join(this_dir, 'scan_window.ui')
        uic.loadUi(scan_file, self)

        self.start_button.clicked.connect(self.start_pressed)
        self.stop_button.clicked.connect(self.stop_pressed)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_start_button)
        self.timer.start(100)  # In milliseconds

        self.outStartLine.setText(self.experiment.params['Scan']['start'])
        self.outStepLine.setText(self.experiment.params['Scan']['step'])
        self.outStopLine.setText(self.experiment.params['Scan']['stop'])
        self.inDelayLine.setText(self.experiment.params['Scan']['delay'])

        self.outChannelLine.setText(str(self.experiment.params['Scan']['channel_out']))
        self.inChannelLine.setText(str(self.experiment.params['Scan']['channel_in']))

        self.plot_widget = pg.PlotWidget()
        self.plot = self.plot_widget.plot([0], [0])

        layout = self.centralwidget.layout()
        layout.addWidget(self.plot_widget)

        self.action_Save.triggered.connect(self.save_clicked)

    def save_clicked(self):
        if not hasattr(self.experiment, 'currents'):
            message_box = QMessageBox()
            message_box.setText('No currents to save')
            message_box.exec()
        else:
            self.experiment.save_data()

    def update_start_button(self):
        if self.experiment.scan_running:
            self.start_button.setEnabled(False)
            self.plot.setData(self.experiment.voltages, self.experiment.currents)
        else:
            self.start_button.setEnabled(True)

    def start_pressed(self):
        start = self.outStartLine.text()
        stop = self.outStopLine.text()
        step = self.outStepLine.text()
        channel_in = int(self.inChannelLine.text())
        channel_out = int(self.outChannelLine.text())

        self.experiment.params['Scan'].update({
            'start': start,
            'stop': stop,
            'step': step,
            'channel_in': channel_in,
            'channel_out': channel_out
        })

        t = threading.Thread(target=self.experiment.do_scan)
        t.start()
        self.start_button.setEnabled(False)

    def stop_pressed(self):
        self.experiment.stop_scan = True

if __name__ == "__main__":
    app = QApplication([])
    win = ScanWindow()
    win.show()
    app.exec()