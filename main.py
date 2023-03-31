# Copyright (C) 2023 Daniel Efimenko
#     github.com/Danya0x07
#
# This software is a part of POFS project.
#

import sys

from PyQt5.QtWidgets import QApplication

from view_controller import MainWindow, ServoCalibrationDialog, AboutDialog

qApp = QApplication([])
mw = MainWindow(None)
swc = ServoCalibrationDialog(None)
abd = AboutDialog(None)

mw.show()
swc.show()
abd.show()

sys.exit(qApp.exec_())