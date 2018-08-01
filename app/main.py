import os
import sys
from PyQt5 import QtWidgets, uic
import serial.tools.list_ports
import urllib.request
import glob
import shutil
import zipfile
import webbrowser

from app import __version__
from app.ui.connect import UsbPortsTableDialog
from app.ui.flow_layout import FlowLayout
from app.ui.built_in_program_dialog import ToggleValveDialog, FivePhasePumpDialog
from app.valve_control import ValveControlDevice, ToggleValveCycle, FivePhasePumpCycle

APP_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(APP_DIR, '..'))
Ui_MainWindow, QMainWindow = uic.loadUiType(os.path.join(APP_DIR, 'ui', 'main.ui'))


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.flowLayoutValveControl = FlowLayout(parent=self.frameValveControl)
        with open(os.path.join(APP_DIR, 'ui', 'style_sheet.txt'), 'r') as f:
            styleSheet = f.read()
        self.setStyleSheet(styleSheet)

        self.dir = APP_DIR

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
        self.connectUi()

    def addValveControl(self, i):
        def func(valveOn):
            self.device.controlSingleValve(i, valveOn)
        return func

    def connectUi(self):
        self.actionGroupSR = QtWidgets.QActionGroup(self.menuShift_Register)
        for i in range(1, 7):
            self.actionGroupSR.addAction(self.__dict__[f'actionSR{i}'])

        self.toolButtonProgram.clicked.connect(self.uploadProgram)
        self.pushButtonStart.clicked.connect(self.start)
        self.pushButtonStop.clicked.connect(self.stop)
        self.pushButtonLoadBuiltIn.clicked.connect(self.loadBuiltInProgram)
        self.actionOpen.triggered.connect(self.uploadProgram)
        self.actionClose.triggered.connect(self.close)
        self.actionRestart_Device.triggered.connect(self.restartDevice)
        self.actionTurn_Off_All.triggered.connect(self.clear)
        self.actionStart.triggered.connect(self.start)
        self.actionStop.triggered.connect(self.stop)
        self.actionGroupSR.triggered.connect(self.changeSR)
        self.actionReset_Input.triggered.connect(self.serialResetInput)
        self.actionReset_Input.triggered.connect(self.serialResetOutput)
        self.actionDocumentation.triggered.connect(self.openGithubRepo)
        self.actionUpdate.triggered.connect(self.update)

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
        cycleCompleted, valveStates = self.device.stop()
        regNum = self.device.settings['REG_NUM']
        for i in range(1, 8*regNum+1):
            self.__dict__[f'checkBoxValve{i}'].blockSignals(True)
            self.__dict__[f'checkBoxValve{i}'].setChecked(valveStates[i-1])
            self.__dict__[f'checkBoxValve{i}'].blockSignals(False)

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
        regNum = self.device.settings['REG_NUM']
        for i in range(1, 8*regNum+1):
            self.__dict__[f'checkBoxValve{i}'].blockSignals(True)
            self.__dict__[f'checkBoxValve{i}'].setChecked(False)
            self.__dict__[f'checkBoxValve{i}'].blockSignals(False)

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

    def openGithubRepo(self):
        webbrowser.open_new('https://github.com/GNHua/valve-control')

    def update(self):
        currentVersion = __version__

        # check the latest version number
        link = 'https://raw.githubusercontent.com/GNHua/valve-control/master/app/__init__.py'
        with urllib.request.urlopen(link) as f:
            _code = f.read()
            exec(_code, globals())
            latestVersion = __version__

        if currentVersion == latestVersion:
            QtWidgets.QMessageBox.information(
                self, 'Info',
                'This is the latest version.',
                QtWidgets.QMessageBox.Ok)
            return

        # clean root directory
        for f in glob.glob(os.path.join(ROOT_DIR, '*')):
            if os.path.isdir(f):
                shutil.rmtree(f)
            else:
                os.remove(f)

        # download the new version of code
        dwn_link = 'https://github.com/GNHua/valve-control/archive/master.zip'
        filename = os.path.join(ROOT_DIR, 'update.zip')
        urllib.request.urlretrieve(dwn_link, filename)

        # unzip downloaded file and extract them to root directory
        with zipfile.ZipFile(filename, 'r') as zf:
            folder = zf.namelist()[0]
            zf.extractall(path=ROOT_DIR)
            for f in glob.glob(os.path.join(ROOT_DIR, folder, '*')):
                if os.path.isdir(f):
                    shutil.copytree(f, os.path.join(ROOT_DIR, os.path.basename(f)))
                else:
                    shutil.copy(f, ROOT_DIR)
            # remove downloaded files
            shutil.rmtree(os.path.join(ROOT_DIR, folder))
            os.remove(filename)

        QtWidgets.QMessageBox.information(
            self, 'Info',
            'The program will be closed.\n'
            'Restart it to run the latest vesion.',
            QtWidgets.QMessageBox.Ok)
        self.close()

    def show(self):
        super().show()
        self.getUsbPort()

    def closeEvent(self, event):
        self.clear()
        self.device.close()
        event.accept()


if __name__ == '__main__':
    application = QtWidgets.QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(application.exec_())
