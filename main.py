# Copyright (C) 2023 Daniel Efimenko
#     github.com/Danya0x07
#
# This software is a part of POFS project.
#

import sys

from PyQt5.QtWidgets import QApplication

from app import App

qApp = QApplication([])
app = App()

sys.exit(qApp.exec_())