import os
import sys
from PyQt5 import QtWidgets, uic
import serial.tools.list_ports

from app.ui.connect import UsbPortsTableDialog
from app.ui.flow_layout import FlowLayout
from app.ui.built_in_program_dialog import ToggleValveDialog, FivePhasePumpDialog
from app.valve_control import ValveControlDevice, ToggleValveCycle, FivePhasePumpCycle

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
Ui_MainWindow, QMainWindow = uic.loadUiType(os.path.join(ROOT_DIR, 'ui', 'main.ui'))


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.flowLayoutValveControl = FlowLayout(parent=self.frameValveControl)
        with open(os.path.join(ROOT_DIR, 'ui', 'style_sheet.txt'), 'r') as f:
            styleSheet = f.read()
        self.setStyleSheet(styleSheet)

        self.actionGroupSR = QtWidgets.QActionGroup(self.menuShift_Register)
        for i in range(1, 7):
            self.actionGroupSR.addAction(self.__dict__[f'actionSR{i}'])

        self.toolButtonProgram.clicked.connect(self.uploadProgram)
        self.pushButtonStart.clicked.connect(self.start)
        self.pushButtonStop.clicked.connect(self.stop)
        self.pushButtonLoadBuiltIn.clicked.connect(self.loadBuiltInProgram)
        self.actionOpen.triggered.connect(self.uploadProgram)
        self.actionClose.triggered.connect(self.closeEvent)
        self.actionRestart_Device.triggered.connect(self.restartDevice)
        self.actionTurn_Off_All.triggered.connect(self.clear)
        self.actionStart.triggered.connect(self.start)
        self.actionStop.triggered.connect(self.stop)
        self.actionGroupSR.triggered.connect(self.changeSR)
        self.actionReset_Input.triggered.connect(self.serialResetInput)
        self.actionReset_Input.triggered.connect(self.serialResetOutput)

        self.dir = ROOT_DIR

    def getUsbPort(self):
        ports = serial.tools.list_ports.comports()
        dialog = UsbPortsTableDialog(ports=ports)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            index = dialog.tableViewUsbPorts.selectedIndexes()[0]
            if index:
                port = ports[index.row()].device
                self.setDevice(port=port)
            else:
                QtWidgets.QMessageBox.critical(
                    self,
                    'Warning!',
                    'Please select a USB port\n',
                    QtWidgets.QMessageBox.Ok)
                self.getUsbPort()
        else:
            sys.exit()

    def setDevice(self, port):
        self.device = ValveControlDevice(port=port)
        regNum = self.device.settings['REG_NUM']
        for i in range(1, 8*regNum+1):
            checkBox = QtWidgets.QCheckBox(str(i))
            self.flowLayoutValveControl.addWidget(checkBox)
            checkBox.toggled[bool].connect(self.addValveControl(i))
            self.__dict__[f'checkBoxValve{i}'] = checkBox
        self.__dict__[f'actionSR{regNum}'].setChecked(True)
        self.menuSerial.setTitle(f'Port: "{port}"')

    def addValveControl(self, i):
        def func(valveOn):
            self.device.controlSingleValve(i, valveOn)
        return func

    def uploadProgram(self):
        fn, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', self.dir, 'text (*.txt)')
        self.dir = os.path.dirname(fn)
        if fn:
            wrongLines = self.device.makeProgrammableCycle(fn)
            if wrongLines:
                wrongLines = ', '.join(list(map(str, self.device.programmableCycle.wrongLines)))
                QtWidgets.QMessageBox.critical(
                    self, 'Error!',
                    'Error at line ' + wrongLines,
                    QtWidgets.QMessageBox.Ok)
            else:
                self.lineEditProgram.setText(fn)
                self.device.uploadProgram()

    def start(self):
        if self.lineEditProgram.text():
            cycles = self.spinBoxCycles.value()
            phaseIntervalMillis = self.spinBoxIntervalMillis.value()
            self.device.start(cycles, phaseIntervalMillis)

    def stop(self):
        self.device.stop()

    def loadBuiltInProgram(self):
        valveNum = 8 * self.device.settings['REG_NUM']
        index = self.comboBoxBuiltIn.currentIndex()
        if index == 0:
            dialog = ToggleValveDialog(valveNum=valveNum)
            if dialog.exec_() == QtWidgets.QDialog.Accepted:
                valve = dialog.spinBoxValve.value()
                self.device.loadToggleValveProgram(valve)
                self.lineEditProgram.setText(f'Built-in Prgram: Toggle Valve {valve}')

        elif index == 1:
            dialog = FivePhasePumpDialog(valveNum=valveNum)
            while True:
                if dialog.exec_() == QtWidgets.QDialog.Accepted:
                    inputValve = dialog.spinBoxInputValve.value()
                    DC = dialog.spinBoxDC.value()
                    outputValve = dialog.spinBoxOutputValve.value()

                    # Check if all 3 valves are different.
                    if len(set([inputValve, DC, outputValve])) != 3:
                        QtWidgets.QMessageBox.critical(
                            self, 'Error!',
                            'You must choose 3 different valves!',
                            QtWidgets.QMessageBox.Ok)
                    else:
                        self.device.load5PhasePumpProgram(inputValve, DC, outputValve)
                        self.lineEditProgram.setText(f'Built-in Prgram: 5 Phase Pump ({inputValve}, {DC}, {outputValve})')
                        break
                else:
                    break

    def restartDevice(self):
        self.device.restart()

    def clear(self):
        self.device.clearShiftRegister()

    def changeSR(self):
        regNum = int(self.menuShift_Register.checkedAction.text())
        if regNum == self.device.settings['REG_NUM']:
            return

        # clear valve controls
        while self.flowLayoutValveControl.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.setRegNum(regNum)
        regNum = self.device.settings['REG_NUM']
        for i in range(1, 8*regNum+1):
            checkBox = QtWidgets.QCheckBox(str(i))
            layout.addWidget(checkBox)
            checkBox.toggled[bool].connect(self.addValveControl(i))
            self.__dict__[f'checkBoxValve{i}'] = checkBox

    def serialResetInput(self):
        self.device.reset_input_buffer()

    def serialResetOutput(self):
        self.device.reset_output_buffer()

    def show(self):
        super().show()
        self.getUsbPort()

    def closeEvent(self, event):
        self.clear()
        self.device.close()
        self.close()
        event.accept()


if __name__ == '__main__':
    application = QtWidgets.QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(application.exec_())
