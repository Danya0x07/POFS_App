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
    
    def update_available_ports(self):
        self.mainwindow.set_available_ports_list(SerialPort.get_available_ports())
    
    def serial_connect(self):
        port_name = self.mainwindow.get_selected_port_name()
        if not port_name:
            self.mainwindow.show_msg("Ну порт же надо выбрать сначала...")
            return

        if self.serial.open(port_name):
            self.mainwindow.show_msg("Соединение установлено")
        else:
            self.mainwindow.show_msg("Ой, порт {} не открывается!".format(port_name))

    def serial_disconnect(self):
        self.serial.close()
        self.mainwindow.show_msg("Соединение закрыто")

    def connection_established(self):
        return self.serial.is_open()
    
    def send_command(self, cmd):
        pass

    def send_reset(self):
        pass

    def send_algorithm(self, before, loop, after, loop_times):
        print(before)
        print(loop)
        print(after)