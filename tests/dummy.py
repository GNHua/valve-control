"""Dummy app for testing without Arduino"""
import os
import sys
import types

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(TEST_DIR, os.pardir))

module_name = 'app.valve_control'
dummy_module = types.ModuleType(module_name)
sys.modules[module_name] = dummy_module
_code = open(os.path.join(TEST_DIR, 'dummy_valve_control.py'), 'rb').read()
exec(_code, dummy_module.__dict__)


if __name__ == '__main__':

    from PyQt5 import QtWidgets
    from app.main import MainWindow

    application = QtWidgets.QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(application.exec_())