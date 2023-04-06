from view_controller import MainWindow, ServoCalibrationDialog, AboutDialog
from serial_port import SerialPort
from protocol import *


class App:
    def __init__(self):
        self.mainwindow = MainWindow(self)
        self.servo_calibration_dialog = ServoCalibrationDialog(self)
        self.about_dialog = AboutDialog(self)
        self.serial = SerialPort(self)

        self.mainwindow.show()
    
    def show_about(self):
        self.about_dialog.show()
    
    def show_servo_calibration(self):
        self.servo_calibration_dialog.show()
    
    def send_command(self, cmd):
        pass

    def send_reset(self):
        pass

    def send_algorithm(self, before, loop, after, loop_times):
        print(before)
        print(loop)
        print(after)