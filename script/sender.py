from PyQt5.QtGui import QImage
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import requests
import serial

class SendHttp(QThread):
    respon = pyqtSignal(str)
    def __init__(self, parent = None, url = ""):
        super(SendHttp, self).__init__(parent)
        self.url = url

    def run(self):
        try:
            res = requests.get(self.url)
            print(res)
        except :
            res = "error"
        self.respon.emit(str(res))

class SendSerial(QThread):
    respon = pyqtSignal(str)
    def __init__(self, parent = None, port = "", baudrate = 9600 , msg =""):
        super(SendSerial, self).__init__(parent)
        self.port = port
        self.baudrate = baudrate
        self.msg = msg

    def run(self):
        res = "ok"
        try:
            self.ser = serial.Serial(port=self.port, baudrate= self.baudrate)
            self.ser.open()
            if (self.ser.is_open):
                self.ser.write(b'hello')
            self.ser.close()
        except :
            res = "error"
        self.respon.emit(str(res))