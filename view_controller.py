from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QDialog

from protocol import (Command, CommandType, FlapStatus,
                      FilterState, MotorID, CalibrationData)


class MainWindow(QMainWindow):

    def __init__(self, app):
        super().__init__()
        uic.loadUi('assets/mainwindow.ui', self)
        self.app = app
        self.connect_signals()
        self.counter = 0

    def connect_signals(self):
        self.btnConnect.clicked.connect(self.__btnConnect_clicked)
        self.btnRefreshPorts.clicked.connect(self.__btnRefreshPorts_clicked)
        self.btnFlapOpen.clicked.connect(self.__btnFlapOpen_clicked)
        self.btnFlapClose.clicked.connect(self.__btnFlapClose_clicked)
        self.btnFilterNone.clicked.connect(self.__btnFilterNone_clicked)
        self.btnFilter1.clicked.connect(self.__btnFilter1_clicked)
        self.btnFilter2.clicked.connect(self.__btnFilter2_clicked)
        self.btnFilter3.clicked.connect(self.__btnFilter3_clicked)
        self.btnFilter4.clicked.connect(self.__btnFilter4_clicked)
        self.btnWait.clicked.connect(self.__btnWait_clicked)
        self.btnAlgorithmExecute.clicked.connect(
            self.__btnAlgorithmExecute_clicked)
        self.btnReset.clicked.connect(self.__btnReset_clicked)
        self.btnCalibrationSend.clicked.connect(
            self.__btnCalibrationSend_clicked)
        self.btnAlgorithmSend.clicked.connect(self.__btnAlgorithmSend_clicked)
        self.btnAlgorithmClear.clicked.connect(
            self.__btnAlgorithmClear_clicked)
        self.btnDeleteCmd.clicked.connect(self.__btnDeleteCmd_clicked)

        self.rbModeRealtime.clicked.connect(self.__rbModeRealtime_clicked)
        self.rbModeRecording.clicked.connect(self.__rbModeRecording_clicked)

        self.actAlgorithmOpen.triggered.connect(
            self.__actAlgorithmOpen_triggered)
        self.actAlgorithmSave.triggered.connect(
            self.__actAlgorithmSave_triggered)
        self.actAbout.triggered.connect(self.__actAbout_triggered)
        self.actCalibrateServos.triggered.connect(
            self.__actCalibrateServos_triggered)

    def show_msg(self, msg, timeout=2000):
        self.statusBar().showMessage(msg, timeout)

    def set_available_ports_list(self, port_names):
        self.cbbSerialPort.clear()
        self.cbbSerialPort.addItems(port_names)

    def get_selected_port_name(self):
        return self.cbbSerialPort.currentText()

    def get_wait_time(self):
        wait_time = self.lnWait.text()
        return int(wait_time)

    def get_selected_servo_idx(self):
        return self.cbbServo.currentIndex()

    def get_calibration_angles(self):
        return self.spbAngleOpen.value(), self.spbAngleClose.value()

    def get_loop_times(self):
        return self.spbLoopTimes.value()

    def _get_selected_list(self):
        if self.rbBeforeLoop.isChecked():
            return self.listPreProcessing
        if self.rbLoop.isChecked():
            return self.listLoop
        if self.rbAfterLoop.isChecked():
            return self.listPostProcessing
        return None  # should be impossible

    @staticmethod
    def _get_section_commands(selected_list):
        commands = []
        for i in range(selected_list.count()):
            txt = selected_list.item(i).text()
            command = MainWindow._cmd_from_readable(txt)
            commands.append(command)
        return commands

    def get_algorithm(self):
        before = self._get_section_commands(self.listPreProcessing)
        loop = self._get_section_commands(self.listLoop)
        after = self._get_section_commands(self.listPostProcessing)
        return before, loop, after

    @staticmethod
    def _cmd_to_readable(cmd):
        if cmd.type == CommandType.SET_FLAP:
            return f'Махалка {("ОТКР" if cmd.arg == FlapStatus.OPENED else "ЗАКР")}'
        if cmd.type == CommandType.SET_FILTER:
            return f'Фильтр {cmd.arg.value if cmd.arg.value != "0" else "НЕТ"}'
        if cmd.type == CommandType.WAIT:
            return f'Ждать {cmd.arg // 1000} сек'
        raise Exception('До седова дойти не должно было. #1')

    @staticmethod
    def _cmd_from_readable(string):
        parts = string.split(' ')[:2]
        if parts[0] == 'Махалка':
            return Command(CommandType.SET_FLAP, FlapStatus.OPENED if parts[1] == 'ОТКР' else FlapStatus.CLOSED)
        if parts[0] == 'Фильтр':
            return Command(CommandType.SET_FILTER, FilterState(parts[1] if parts[1] != 'НЕТ' else '0'))
        if parts[0] == 'Ждать':
            return Command(CommandType.WAIT, int(parts[1]) * 1000)
        raise Exception('До седова дойти не должно было. #2')

    def record_command(self, cmd):
        selected_list = self._get_selected_list()
        row = selected_list.currentRow() + 1
        if selected_list is not None:
            cmd = self._cmd_to_readable(cmd)
            selected_list.insertItem(row, cmd)
            selected_list.setCurrentRow(row)

    def post_command(self, cmd, realtime=True, recording=True):
        if self.rbModeRealtime.isChecked():
            if realtime:
                self.app.send_command(cmd)
            else:
                self.show_msg("Эта команда не для RealTime")
        elif self.rbModeRecording.isChecked():
            if recording:
                self.record_command(cmd)
            else:
                self.show_msg("Эта команда не для записи")

    def __btnConnect_clicked(self):
        # Если соединение уже открыто, закрываем его, иначе открываем.
        if self.app.connection_established():
            self.app.serial_disconnect()
            self.btnConnect.setText("Подключить")
        else:
            self.app.serial_connect()
            if self.app.connection_established():
                self.btnConnect.setText("Отключить")

    def __btnRefreshPorts_clicked(self):
        self.app.update_available_ports()

    def __btnFlapOpen_clicked(self):
        cmd = Command(CommandType.SET_FLAP, FlapStatus.OPENED)
        self.post_command(cmd)

    def __btnFlapClose_clicked(self):
        cmd = Command(CommandType.SET_FLAP, FlapStatus.CLOSED)
        self.post_command(cmd)

    def __btnFilterNone_clicked(self):
        cmd = Command(CommandType.SET_FILTER, FilterState.NONE)
        self.post_command(cmd)

    def __btnFilter1_clicked(self):
        cmd = Command(CommandType.SET_FILTER, FilterState.FS1)
        self.post_command(cmd)

    def __btnFilter2_clicked(self):
        cmd = Command(CommandType.SET_FILTER, FilterState.FS2)
        self.post_command(cmd)

    def __btnFilter3_clicked(self):
        cmd = Command(CommandType.SET_FILTER, FilterState.FS3)
        self.post_command(cmd)

    def __btnFilter4_clicked(self):
        cmd = Command(CommandType.SET_FILTER, FilterState.FS4)
        self.post_command(cmd)

    def __btnWait_clicked(self):
        wait_time = int(self.lnWait.text())
        wait_time *= 1000  # Convert to milliseconds
        cmd = Command(CommandType.WAIT, wait_time)
        self.post_command(cmd, realtime=False)

    def __btnAlgorithmExecute_clicked(self):
        cmd = Command(CommandType.EXECUTE_PROGRAM)
        self.post_command(cmd, recording=False)

    def __btnReset_clicked(self):
        self.app.send_reset()

    def __btnCalibrationSend_clicked(self):
        servo_id = MotorID(str(self.get_selected_servo_idx()))
        ang_opened, ang_closed = self.get_calibration_angles()
        cmd = Command(CommandType.CALIBRATE, CalibrationData(
            servo_id, ang_opened, ang_closed))
        self.post_command(cmd, recording=False)

    def __btnAlgorithmSend_clicked(self):
        before, loop, after = self.get_algorithm()
        loop_times = self.get_loop_times()
        self.app.send_algorithm(before, loop, after, loop_times)

    def __btnAlgorithmClear_clicked(self):
        self.listPreProcessing.clear()
        self.listLoop.clear()
        self.listPostProcessing.clear()

    def __btnDeleteCmd_clicked(self):
        selected_list = self._get_selected_list()
        if selected_list is not None:
            row = selected_list.currentRow()
            selected_list.takeItem(row)

    def __rbModeRealtime_clicked(self):
        pass

    def __rbModeRecording_clicked(self):
        pass

    def __actAlgorithmOpen_triggered(self):
        print('triggered')

    def __actAlgorithmSave_triggered(self):
        print('triggered')

    def __actAbout_triggered(self):
        self.app.show_about()

    def __actCalibrateServos_triggered(self):
        self.app.show_servo_calibration()


class ServoCalibrationDialog(QDialog):

    def __init__(self, app):
        super().__init__()
        uic.loadUi('assets/servocalibration.ui', self)
        self.app = app
        self.connect_signals()

    def connect_signals(self):
        self.btnOpen.clicked.connect(self.__btnOpen_clicked)
        self.btnSave.clicked.connect(self.__btnSave_clicked)
        self.btnRead.clicked.connect(self.__btnRead_clicked)
        self.btnProg.clicked.connect(self.__btnProg_clicked)

    def __btnOpen_clicked(self):
        print('clicked')

    def __btnSave_clicked(self):
        print('clicked')

    def __btnRead_clicked(self):
        print('clicked')

    def __btnProg_clicked(self):
        print('clicked')


class AboutDialog(QDialog):

    def __init__(self, app):
        super().__init__()
        uic.loadUi('assets/about.ui', self)
        self.app = app
