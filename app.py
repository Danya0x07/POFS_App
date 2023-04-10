import json
from collections import deque

from view_controller import MainWindow, ServoCalibrationDialog, AboutDialog
from serial_port import SerialPort
from protocol import *


class App:
    def __init__(self):
        self.mainwindow = MainWindow(self)
        self.servo_calibration_dialog = ServoCalibrationDialog(self)
        self.about_dialog = AboutDialog(self)
        self.serial = SerialPort(self)
        self._command_queue = deque()
        self._response_queue = deque()
        self._device_is_executing = False
        self._expectations = None
        self.__last_algorithm_cmd = None

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
        if not self.connection_established():
            self.mainwindow.show_msg('Порт открой сперва')
            return
        
        if not self._device_is_executing or cmd.type == CommandType.EMERGENCY:
            self._expectations = self.generate_expected_response(cmd)
            if cmd.type == CommandType.EXECUTE_PROGRAM:
                if self.__last_algorithm_cmd is None:
                    self.mainwindow.show_msg('Перед выполнением алгоритм надо загрузить', 3000)
                    self._expectations.clear()
                    return
                self._expectations[0] = Response(ResponseType.EXEC_FINISH, self.__last_algorithm_cmd)
                self._device_is_executing = True
            self.serial.write(str(cmd))
            print(f'Sending: {repr(str(cmd))}')
        else:
            self.mainwindow.show_msg('В данный момент выполняется какой-то алгоритм', 3000)

    def send_reset(self):
        if self._device_is_executing:
            self.send_command(Command(CommandType.EMERGENCY))
            self._device_is_executing = False
        else:
            self.send_command(Command(CommandType.RESET))
    
    def send_calibration(self, raw_calibration):
        if not self.connection_established():
            self.mainwindow.show_msg('Порт открой сперва')
            return
        
        if self._device_is_executing:
            self.mainwindow.show_msg('В данный момент выполняется какой-то алгоритм', 3000)
            return

        self._command_queue.clear()
        self._response_queue.clear()

        calibration = self.process_calibration(raw_calibration)
        if calibration is None:
            return
        
        for i in range(len(calibration)):
            command = Command(CommandType.CALIBRATE,
                CalibrationData(
                    motorID=MotorID(str(i)),
                    openedAngle=calibration[i][0],
                    closedAngle=calibration[i][1]
                )
            )
            self._command_queue.append(command)
            self._response_queue.append(self.generate_expected_response(command))

        lastcmd = Command(CommandType.SAVE_CALIBRATION)
        self._command_queue.append(lastcmd)
        self._response_queue.append(self.generate_expected_response(lastcmd))

        firstcmd = self._command_queue.popleft()
        self._expectations = self._response_queue.popleft()

        self.serial.write(str(firstcmd))
        print(f'Sending: {repr(str(firstcmd))}')

    def send_algorithm(self, before, loop, after, loop_times):
        if not self.connection_established():
            self.mainwindow.show_msg('Порт открой сперва')
            return
        
        if self._device_is_executing:
            self.mainwindow.show_msg('В данный момент выполняется какой-то алгоритм', 3000)
            return
        
        self._command_queue.clear()
        self._response_queue.clear()

        commands = [
            Command(CommandType.LOADING_MODE),
            *before,
            *loop,
            *after,
            Command(CommandType.SAVE_PROGRAM,
                LoopData(
                    beginMark = len(before) + 1,
                    endMark = len(before) + len(loop),
                    numRepetitions = loop_times if len(loop) != 0 else 0
                )
            )
        ]
        self.__last_algorithm_cmd = commands[-2]

        for command in commands:
            self._command_queue.append(command)
            self._response_queue.append(self.generate_expected_response(command, realtime=False))
        
        firstcmd = self._command_queue.popleft()
        self._expectations = self._response_queue.popleft()

        self.serial.write(str(firstcmd))
        print(f'Sending: {repr(str(firstcmd))}')

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
    
    def process_calibration(self, raw_calibration):
        if all(self.angles_row_valid(row) for row in raw_calibration):
            calibration = [list(map(int, row)) for row in raw_calibration]
            return calibration
        else:
            self.mainwindow.show_msg('В таблице некоторый мусор, проверьте!')
    
    def save_servo_calibration(self, raw_calibration, filename):
        calibration = self.process_calibration(raw_calibration)
        if calibration is not None:
            string = json.dumps(calibration, indent=4)
            with open(filename, 'w') as f:
                f.write(string)
    
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
    
    def generate_expected_response(self, command, realtime=True):
        expectations = []
        if realtime and command.type != CommandType.PRINT_CALIBRATION:
            expectations.append(Response(ResponseType.EXEC_FINISH, command))
        expectations.append(Response(ResponseType.PARSING_OK, None))
        return expectations
        
    
    def process_packet(self):
        status, response = self.serial.read()

        if status == SerialPort.ErrorStatus.NO_PACKET:
            self.mainwindow.show_msg('Перенос строки просрали')
            return
        if status == SerialPort.ErrorStatus.DECODING_ERROR:
            self.mainwindow.show_msg('Контроллер что-то бормочет')
            return
        
        try:
            print(f'Received: {str(repr(response))}')
            response = parse_response(response)
        except ValueError as e:
            self.mainwindow.show_msg(f'Ошибка парсинга {repr(str(e))}', 1500)
            return
            
        if response.type == ResponseType.PARSING_OK or response.type == ResponseType.EXEC_FINISH:
            if len(self._expectations) == 0:
                self.mainwindow.show_msg('Рассинхронизация: нежданный ответ')
                return
            
            expected = self._expectations.pop()
            if response != expected:
                self.mainwindow.show_msg(f'Рассинхронизация: {response} -- {expected}')

            if len(self._expectations) == 0:
                if self._response_queue:
                    self._expectations = self._response_queue.popleft()
                    if self._command_queue:
                        next_cmd = self._command_queue.popleft()
                        self.serial.write(str(next_cmd))
                        print(f'Sending: {repr(str(next_cmd))}')
                    else:
                        self.mainwindow.show_msg('Рассинхронизация: нечем продолжить диалог')
                else:
                    self._device_is_executing = False

        elif response.type == ResponseType.PARSING_ERR:
            self.mainwindow.show_msg('Контроллер подавился')
            self._device_is_executing = False
        elif response.type == ResponseType.DISPATCH_ERR:
            self.mainwindow.show_msg('Контроллер растерялся')
            self._device_is_executing = False
        elif response.type == ResponseType.CALIB_DATA:
            calibration = [[c.openedAngle, c.closedAngle] for c in response.data]
            self.servo_calibration_dialog.set_table_contents(calibration)
