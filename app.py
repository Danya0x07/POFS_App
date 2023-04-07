import json

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
        self.mainwindow.set_available_ports_list(
            SerialPort.get_available_ports())

    def serial_connect(self):
        port_name = self.mainwindow.get_selected_port_name()
        if not port_name:
            self.mainwindow.show_msg("Ну порт же надо выбрать сначала...")
            return

        if self.serial.open(port_name):
            self.mainwindow.show_msg("Соединение установлено")
        else:
            self.mainwindow.show_msg(
                "Ой, порт {} не открывается!".format(port_name))

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

    def save_algorithm(self, algorithm, filename):
        string = json.dumps(algorithm, indent=4)
        with open(filename, 'w') as f:
            f.write(string)

    def load_algorithm(self, filename):
        with open(filename, 'r') as f:
            data = json.load(f)
        try:
            before = [Command.from_str(cmd) for cmd in data['before']]
            loop = [Command.from_str(cmd) for cmd in data['loop']]
            after = [Command.from_str(cmd) for cmd in data['after']]
            loop_times = abs(int(data['loop_times']))
        except (KeyError, TypeError):
            self.mainwindow.show_msg('Плохой файл', 3000)
        except ValueError as e:
            self.mainwindow.show_msg(str(e), 3000)
        else:
            if self.sequence_valid(before) and self.sequence_valid(loop) and self.sequence_valid(after):
                algorithm = {
                    'before': before,
                    'loop': loop,
                    'after': after,
                    'loop_times': loop_times
                }
                return algorithm
            else:
                self.mainwindow.show_msg(
                    'Считанные команды всраты по сути своей.', 3000)
        return None
    
    def save_servo_calibration(self, raw_calibration, filename):
        if all(self.angles_row_valid(row) for row in raw_calibration):
            calibration = [list(map(int, row)) for row in raw_calibration]
            string = json.dumps(calibration, indent=4)
            with open(filename, 'w') as f:
                f.write(string)
        else:
            self.mainwindow.show_msg('В таблице некоторый мусор, проверьте!')
    
    def load_servo_calibration(self, filename):
        with open(filename, 'r') as f:
            data = json.load(f)
        if (type(data) == list and len(data) == 5
                and all(type(r) == list and self.angles_row_valid(r) for r in data)):
            return data
        else:
            self.mainwindow.show_msg('Данные некорректны')
            return None

    def sequence_valid(self, sequence):
        return all(cmd.type in (CommandType.SET_FLAP, CommandType.SET_FILTER, CommandType.WAIT)
                   for cmd in sequence)
    
    def angles_row_valid(self, row):
        return all(str(a).isnumeric() and 0 <= int(a) <= 180 for a in row)
