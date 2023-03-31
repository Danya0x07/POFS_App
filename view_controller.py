from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QDialog


class MainWindow(QMainWindow):

    def __init__(self, app):
        super().__init__()
        uic.loadUi('assets/mainwindow.ui', self)
        self.app = app
        self.connect_signals()
    
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
        self.btnAlgorithmExecute.clicked.connect(self.__btnAlgorithmExecute_clicked)
        self.btnReset.clicked.connect(self.__btnReset_clicked)
        self.btnCalibrationSend.clicked.connect(self.__btnCalibrationSend_clicked)
        self.btnAlgorithmSend.clicked.connect(self.__btnAlgorithmSend_clicked)
        self.btnAlgorithmClear.clicked.connect(self.__btnAlgorithmClear_clicked)
        self.btnDeleteCmd.clicked.connect(self.__btnDeleteCmd_clicked)

        self.rbModeRealtime.clicked.connect(self.__rbModeRealtime_clicked)
        self.rbModeRecording.clicked.connect(self.__rbModeRecording_clicked)

        self.actAlgorithmOpen.triggered.connect(self.__actAlgorithmOpen_triggered)
        self.actAlgorithmSave.triggered.connect(self.__actAlgorithmSave_triggered)
        self.actAbout.triggered.connect(self.__actAbout_triggered)
        self.actCalibrateServos.triggered.connect(self.__actCalibrateServos_triggered)
    
    def __btnConnect_clicked(self):
        print('clicked')
    
    def __btnRefreshPorts_clicked(self):
        print('clicked')

    def __btnFlapOpen_clicked(self):
        print('clicked')
    
    def __btnFlapClose_clicked(self):
        print('clicked')
    
    def __btnFilterNone_clicked(self):
        print('clicked')
    
    def __btnFilter1_clicked(self):
        print('clicked')
    
    def __btnFilter2_clicked(self):
        print('clicked')
    
    def __btnFilter3_clicked(self):
        print('clicked')
    
    def __btnFilter4_clicked(self):
        print('clicked')
    
    def __btnWait_clicked(self):
        print('clicked')
    
    def __btnAlgorithmExecute_clicked(self):
        print('clicked')
    
    def __btnReset_clicked(self):
        print('clicked')
    
    def __btnCalibrationSend_clicked(self):
        print('clicked')
    
    def __btnAlgorithmSend_clicked(self):
        print('clicked')
    
    def __btnAlgorithmClear_clicked(self):
        print('clicked')
    
    def __btnDeleteCmd_clicked(self):
        print('clicked')
    
    def __rbModeRealtime_clicked(self):
        print('clicked')
    
    def __rbModeRecording_clicked(self):
        print('clicked')
    
    def __actAlgorithmOpen_triggered(self):
        print('triggered')
    
    def __actAlgorithmSave_triggered(self):
        print('triggered')
    
    def __actAbout_triggered(self):
        print('triggered')
    
    def __actCalibrateServos_triggered(self):
        print('triggered')


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
