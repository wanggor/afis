from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import uic
import time

import impro
import sender

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi('interface.ui',self)

        self.setup()

    def setup(self):
        self.ui.pushButton_start.clicked.connect(self.startCamera)
        self.ui.pushButton_send.clicked.connect(self.send)
        # self.ui.radioButton_tunggal.toggled.connect(lambda:self.modeDeteksi(self.ui.radioButton_tunggal))
        # self.ui.radioButton_multi.toggled.connect(lambda:self.modeDeteksi(self.ui.radioButton_multi))
        self.ui.pushButton_clear.clicked.connect(self.clearList)
        self.ui.frame_4.hide()
        self.ui.frame_color.hide()
        self.ui.lineEdit_code_send.hide()
        self.ui.label_5.hide()

        self.itemList = {}
        self.start = False
        for i in range(2):
        # for i in impro.check_available_camera():
            self.ui.comboBox_camera.addItem("Camera " + str(i+1))

    def get_config(self):
        if self.ui.radioButton_lambat.isChecked() : 
            mode_send = "lambat"
        elif self.ui.radioButton_cepat.isChecked() :
            mode_send = "cepat"
        else:
            mode_send = "sedang"
        if self.ui.radioButton_putih.isChecked() : 
            color_send = "putih"
        else:
            color_send = "kuning"

        return {"color" : color_send, "mode" : mode_send}

    def send(self):
        config =  self.get_config()
                
        code = self.ui.lineEdit_code_send.text()
        msg = self.ui.textEdit_msg_send.toPlainText()
        
        url = "http://192.168.4.1/text?{msg}"
        self.senderHttp = sender.SendHttp(parent=self, url=url)
        self.senderHttp.respon.connect(self.getRespon)
        self.senderHttp.start()
        self.ui.pushButton_send.setEnabled(False)

    @pyqtSlot(str)
    def getRespon(self, respon):
        print(respon)
        self.ui.pushButton_send.setEnabled(True)

    def startCamera(self):
        if not (self.start) :
            config = self.get_config()

            self.camera = impro.Camera_stream(cap = self.comboBox_camera.currentIndex(),parent = self, mode_detection=config["mode"], color=config["color"])
            self.camera.changePixmap.connect(self.update_frame)
            self.camera.data.connect(self.update_data)
            self.camera.start()
            self.start = True
            self.ui.pushButton_start.setText("Berhenti")

            self.ui.frame_color.setEnabled(False)
            self.ui.frame_mode.setEnabled(False)
        else:
            self.camera.stop = True
            self.ui.pushButton_start.setText("Mulai")
            self.start = False

            if self.camera.isRunning():
                self.ui.label_frame.clear()
                self.camera.quit()

            self.ui.frame_color.setEnabled(True)
            self.ui.frame_mode.setEnabled(True)

    @pyqtSlot(QImage)
    def update_frame(self,image):
        if self.start:
            self.ui.label_frame.setPixmap( QPixmap.fromImage(image))

    @pyqtSlot(dict)
    def update_data(self,data):
        keys = sorted(list(data.keys()))
        for key in keys:
            textvalue = "".join([ str(i[0]) for i in data[key][:-1]]) + " " + str(data[key][-1]) 
            if key not in self.itemList.keys():
                self.itemList[key] = self.addMsgWidget( key ,textvalue)
            else:
                self.itemList[key].plainTextEdit.setPlainText(textvalue)

    def clearList(self):
        self.itemList = {}
        self.ui.listView_msg.clear()

    def modeDeteksi(self, radio):
        if radio.isChecked():
            mode = radio.text()

    def addMsgWidget(self, key, value):
        widget = uic.loadUi('list_item.ui')
        widget.number_index.setText(str(key + 1)+ ". ")
        # widget.widget.hide()
        widget.plainTextEdit.setPlainText(value)
        count = self.ui.listView_msg.count()
        # widget.pushButton_decode.clicked.connect(lambda: self.decode(key))

        item =  QListWidgetItem()
        self.ui.listView_msg.insertItem(self.ui.listView_msg.count(), item)
        self.ui.listView_msg.setItemWidget(item, widget)
        item.setSizeHint(widget.sizeHint())
        return widget

    def decode(self, index):
        code = self.itemList[index].lineEdit_code.text()
        msg = self.itemList[index].plainTextEdit.toPlainText()
        new_msg = msg + code
        self.itemList[index].plainTextEdit.setPlainText(new_msg)

    def closeEvent(self,event):
        self.camera.stop = True
        time.sleep(1)
        self.camera.quit()
        event.accept()




if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    app.setStyleSheet('MainWindow {background-image: url(background.jpg); }')
    Dialog = MainWindow()
    Dialog.setWindowTitle("AFIS")
    Dialog.showMaximized()
    sys.exit(app.exec_())