from PyQt5 import QtCore, QtWidgets, uic
import serial.tools.list_ports
import os

DEFAULT_PORT_FILE = 'port.txt'
_path = os.path.dirname(os.path.abspath(__file__))


class UsbPortsTableModel(QtCore.QAbstractTableModel):
    def __init__(self, ports):
        '''`params` is a list of print parameter values.'''
        super().__init__()
        self._headers = ['USB port', 'Detail']
        self.ports = ports

        try:
            with open(os.path.join(_path, '..', DEFAULT_PORT_FILE), 'r') as f:
                self.defaultPort = f.read()
        except FileNotFoundError:
            self.defaultPort = ''

    def flags(self, index):
        flags = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        return flags

    def rowCount(self, parent):
        return len(self.ports)
        
    def columnCount(self, parent):
        return 2

    def data(self, index, role):
        if not index.isValid():
            return None

        if role == QtCore.Qt.DisplayRole:
            if index.column() == 0:
                port = self.ports[index.row()].device
                if port == self.defaultPort:
                    port += ' (default)'
                    self.defaultPortIndex = index.row()
                return port
            elif index.column() == 1:
                return self.ports[index.row()].description
        elif role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignCenter

        else:
            return None

    def setData(self, index, value, role):
        return False

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self._headers[section]
            else:
                return section+1


Ui_Dialog, QDialog = uic.loadUiType(os.path.join(_path, 'connect.ui'))

class UsbPortsTableDialog(QDialog, Ui_Dialog):
    def __init__(self, ports):
        super().__init__()
        self.setupUi(self)

        self.model = UsbPortsTableModel(ports=ports)
        self.tableViewUsbPorts.setModel(self.model)
        self.tableViewUsbPorts.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableViewUsbPorts.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableViewUsbPorts.resizeColumnsToContents()
        self.pushButtonRefresh.clicked.connect(self.refresh)
        self.pushButtonSetDefault.clicked.connect(self.setDefault)

        try:
            self.tableViewUsbPorts.selectRow(self.model.defaultPortIndex)
        except AttributeError:
            pass
        
    def refresh(self):
        self.model.ports = serial.tools.list_ports.comports()
        self.model.layoutChanged.emit()

    def setDefault(self):
        selected = self.tableViewUsbPorts.selectedIndexes()[0]
        if selected:
            port = selected.data()
            with open(os.path.join(_path, '..', DEFAULT_PORT_FILE), 'w') as f:
                f.write(port)
            self.model.defaultPort = port
            self.refresh()
        else:
            QtWidgets.QMessageBox.critical(
                self,
                'Warning!',
                'Please select a port!\n',
                QtWidgets.QMessageBox.Ok)


if __name__ == '__main__':
    import sys
    from flow_layout import FlowLayout

    class SerialPort:
        def __init__(self, device, description):
            self.device = device
            self.description = description


    def findArduino():
        return [SerialPort('COM1', 'Arduino 1'), SerialPort('COM2', 'Arduino 2')]
    
    
    Ui_MainWindow, QMainWindow = uic.loadUiType(os.path.join(_path, 'main.ui'))
    class MainWindow(QMainWindow, Ui_MainWindow):
        def __init__(self):
            super().__init__()
            self.setupUi(self)

            layout = FlowLayout(parent=self.frameValveControl)
            for i in range(1, 30):
                checkBox = QtWidgets.QCheckBox(f'{i}')
                layout.addWidget(checkBox)
                self.__dict__[f'checkBoxValve{i}'] = checkBox

            self.checkBoxValve1.setEnabled(False)
            
            with open(os.path.join(_path, 'style_sheet.txt'), 'r') as f:
                styleSheet = f.read()
            self.setStyleSheet(styleSheet)

            # while layout.count():
            #     child = layout.takeAt(0)
            #     if child.widget():
            #         child.widget().deleteLater()

            # for i in range(1, 9):
            #     checkBox = QtWidgets.QCheckBox(f'Valve {i}')
            #     layout.addWidget(checkBox)
            #     self.__dict__[f'checkBoxValve{i}'] = checkBox

            self.actionSR1.triggered.connect(self.test)
            self.pushButtonStart.clicked.connect(self.test2)

        def test(self):
            print('SR1 TRIGGERED')

        def test2(self):
            self.actionSR1.setChecked(True)

        def getUsbPort(self):
            ports = findArduino()
            dialog = UsbPortsTableDialog(ports=ports)
            if dialog.exec_() == QtWidgets.QDialog.Accepted:
                if dialog.tableViewUsbPorts.selectedIndexes():
                    print(dialog.tableViewUsbPorts.selectedIndexes()[0].data())
                else:
                    QtWidgets.QMessageBox.critical(
                        self,
                        'Warning!',
                        'Please select a USB port\n',
                        QtWidgets.QMessageBox.Ok)
                    self.getUsbPort()
            else:
                sys.exit()

        def show(self):
            super().show()
            self.getUsbPort()


    app = QtWidgets.QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec_())
