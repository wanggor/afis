from PyQt5.QtGui import QImage
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import requests

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