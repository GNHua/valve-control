from PyQt5 import QtWidgets
import sys

from app.main import MainWindow


application = QtWidgets.QApplication(sys.argv)
mainwindow = MainWindow()
mainwindow.show()
sys.exit(application.exec_())
