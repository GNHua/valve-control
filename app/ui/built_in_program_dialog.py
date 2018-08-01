from PyQt5 import uic
import os

__path = os.path.dirname(os.path.abspath(__file__))


Ui_Dialog_toggle_valve, QDialog_toggle_valve = uic.loadUiType(
    os.path.join(__path, 'toggle_valve.ui'))

class ToggleValveDialog(Ui_Dialog_toggle_valve, QDialog_toggle_valve):

    def __init__(self, valveNum):
        super().__init__()
        self.setupUi(self)

        self.spinBoxValve.setMaximum(valveNum)


Ui_Dialog_5_phase_pump, QDialog_5_phase_pump = uic.loadUiType(
    os.path.join(__path, '5_phase_pump.ui'))

class FivePhasePumpDialog(Ui_Dialog_5_phase_pump, QDialog_5_phase_pump):

    def __init__(self, valveNum):
        super().__init__()
        self.setupUi(self)

        self.spinBoxInputValve.setMaximum(valveNum)
        self.spinBoxDC.setMaximum(valveNum)
        self.spinBoxOutputValve.setMaximum(valveNum)


