# Copyright (C) 2023 Daniel Efimenko
#     github.com/Danya0x07
#
# This software is a part of POFS project.
#

import sys

from PyQt5.QtWidgets import QApplication

from view_controller import MainWindow

qApp = QApplication([])
mw = MainWindow(None)

sys.exit(qApp.exec_())