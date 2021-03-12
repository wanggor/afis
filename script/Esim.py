import PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import uic
import time

import impro as impro
import sender as sender
import encryption
import resources
import constant

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load the UI
        fileh = QFile(':/ui/interface.ui')
        fileh.open(QFile.ReadOnly)
        self.ui =  uic.loadUi(fileh, self)
        fileh.close()
        self.setup()

    def setup(self):
        self.ui.pushButton_start.clicked.connect(self.startCamera)
        self.ui.pushButton_send.clicked.connect(self.send)
        self.ui.pushButton_setting.clicked.connect(self.changeSetting)
        self.ui.pushButton_startRead.clicked.connect(self.startRead)
        self.ui.pushButton_saveconst.clicked.connect(self.updateConst)
        self.ui.pushButton_testLampu.clicked.connect(self.testLampu)
        self.ui.pushButton_clear.clicked.connect(self.clearList)
        self.ui.pushButton_rotate.clicked.connect(self.rotate)
        self.ui.frame_4.hide()
        self.ui.frame_setting.hide()
        # self.ui.frame_color.hide()

        self.itemList = {}
        self.encrypeList = {}
        self.start = False

        for i in range(2):
            self.ui.comboBox_camera.addItem("Camera " + str(i+1))

        self.isSetting = True
        self.camera = None
        self.isreading= False
        self.rotate_value = 0

        self.constant = constant.mode_detection
        self.treshold = 250
        self.minSize = 5
        self.updateSetting()

    def updateSetting(self):
        self.ui.lineEdit_treshold.setText(str(self.treshold))
        mode = self.get_mode()
        param = self.constant[mode]
        self.ui.lineEdit_short.setText(str(int(param["zero-tick"] * 1000)))
        self.ui.lineEdit_long.setText(str(int(param["one-tick"]* 1000)))
        self.ui.lineEdit_space.setText(str(int(param["space-tick"]* 1000)))
        self.ui.lineEdit_tolerance.setText(str(int(param["tolerance"]* 1000)))

        self.ui.lineEdit_objSize.setText(str(self.minSize))


    def rotate(self):
        self.rotate_value = (self.rotate_value + 90) % 360
        if self.rotate_value == 0:
            self.pushButton_rotate.setText(f"Putar")
        else:
            self.pushButton_rotate.setText(f"Putar ({str(self.rotate_value)} deg)")

    def updateConst(self):
        mode = self.get_mode()
        self.constant[mode] = {
                            "zero-tick" : float(self.ui.lineEdit_short.text()) / 1000,
                            "one-tick" : float(self.ui.lineEdit_long.text()) / 1000,
                            "space-tick" : float(self.ui.lineEdit_space.text()) / 1000,
                            "split-tick" : float(self.ui.lineEdit_space.text()) / 1000,
                            "tolerance" : float(self.ui.lineEdit_tolerance.text()) / 1000
                            }
        self.treshold = int(self.ui.lineEdit_treshold.text())
        if self.camera is not None:
            self.camera.updateConst(self.constant[mode], int(self.ui.lineEdit_treshold.text()), float(self.ui.lineEdit_objSize.text()))

    def changeSetting(self):
        if self.isSetting:
            if self.camera is not None:
                self.camera.changeSetting(True)
            self.ui.frame_setting.show()
            self.updateSetting()
            self.ui.label_info.show()
            self.ui.label_info2.show()
        else:
            if self.camera is not None:
                self.camera.changeSetting(False)
            self.ui.frame_setting.hide()
            self.ui.label_info.hide()
            self.ui.label_info2.hide()
        self.isSetting = not self.isSetting
        
    def get_mode(self):
        if self.ui.radioButton_lambat.isChecked() : 
            mode_send = 1
        elif self.ui.radioButton_cepat.isChecked() :
            mode_send = 3
        else:
            mode_send = 2
        return mode_send

    def send(self):
        mode =  self.get_mode()   
        code = self.ui.lineEdit_code_send.text()
        msg = encryption.encode(code, self.ui.textEdit_msg_send.toPlainText())
        # url = "http://192.168.4.1/text?="+msg #AFIS 1.0
        url = "http://192.168.4.1/text?2"+str(mode)+"1"+msg
        self.senderHttp = sender.SendHttp(parent=self, url=url)
        self.senderHttp.respon.connect(self.getRespon)
        self.senderHttp.start()
        self.ui.pushButton_send.setEnabled(False)

    def testLampu(self):
        url = "http://192.168.4.1/text?1"
        # url = "http://192.168.4.1/text?0" matikan test lemp
        self.senderHttp = sender.SendHttp(parent=self, url=url)
        self.senderHttp.respon.connect(self.getRespon)
        self.senderHttp.start()

    @pyqtSlot(str)
    def getRespon(self, respon):
        self.ui.pushButton_send.setEnabled(True)

    def startCamera(self):
        if not (self.start) :
            mode =  self.get_mode()
            param = self.constant[mode]
            self.camera = impro.Camera_stream(
                cap = self.comboBox_camera.currentIndex(), 
                parent = self, 
                const = param,
                treshold = int(self.ui.lineEdit_treshold.text()),
                angle= self.rotate_value)
            self.camera.changePixmap.connect(self.update_frame)
            self.camera.data.connect(self.update_data)
            self.camera.dataDurasiSignal.connect(self.update_data_durasi)
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
            self.camera = None

    @pyqtSlot(QImage)
    def update_frame(self,image):
        if self.start:
            self.ui.label_frame.setPixmap( QPixmap.fromImage(image))

    @pyqtSlot(dict)
    def update_data_durasi(self,dataDurasi):
        dataOne = dataDurasi["one"]
        dataZero = dataDurasi["zero"]
        labelOne = f"One  | {str(dataOne)}   | min : {min(dataOne)} | max : {max(dataOne)}"
        labelZero = f"Zero | {str(dataZero)}   | min : {min(dataZero)} | max : {max(dataZero)}"
        self.ui.label_info.setText(labelOne)
        self.ui.label_info2.setText(labelZero)

    @pyqtSlot(dict)
    def update_data(self,data):
        if self.isreading:
            keys = sorted(list(data.keys()))
            for key in keys:
                textvalue = "".join([ str(i[0]) for i in data[key][:-1]]) + " " + str(data[key][-1]) 
                if key not in self.itemList.keys():
                    self.itemList[key] = self.addMsgWidget( key ,textvalue)
                    self.encrypeList[key] = {
                        "code" : ""
                    }
                else:
                    if self.encrypeList[key]["code"] != "":
                        textvalue = f'[{self.encrypeList[key]["code"]}] ' + encryption.decode(self.encrypeList[key]["code"], textvalue.lower())
                    self.itemList[key].plainTextEdit.setPlainText(textvalue.upper())

    def startRead(self):
        self.isreading = not(self.isreading) 
        if self.camera is not None:
            if self.isreading:
                self.camera.changeReading(True)
                # self.itemList = {}
                # self.encrypeList = {}
                # self.ui.listView_msg.blockSignals(True)
                # self.ui.listView_msg.clear()
                self.ui.pushButton_startRead.setText("Stop Membaca")
            else:
                self.camera.changeReading(False)
                self.ui.pushButton_startRead.setText("Mulai Membaca")

    def clearList(self):
        self.itemList = {}
        self.encrypeList = {}
        self.ui.listView_msg.clear()

    def addMsgWidget(self, key, value):
        # widget = uic.loadUi('list_item.ui')

        # Load the UI
        fileh = QFile(':/ui/list_item.ui')
        fileh.open(QFile.ReadOnly)
        widget =  uic.loadUi(fileh)
        fileh.close()

        widget.number_index.setText(str(key + 1)+ ". ")
        # widget.widget.hide()
        widget.plainTextEdit.setPlainText(value)
        count = self.ui.listView_msg.count()
        widget.pushButton_decode.clicked.connect(lambda: self.decode(key))

        item =  QListWidgetItem()
        self.ui.listView_msg.insertItem(self.ui.listView_msg.count(), item)
        self.ui.listView_msg.setItemWidget(item, widget)
        item.setSizeHint(widget.sizeHint())
        return widget

    def decode(self, index):
        code = self.itemList[index].lineEdit_code.text()
        self.encrypeList[index]["code"] = code

    def closeEvent(self,event):
        self.camera.stop = True
        # time.sleep(1)
        self.camera.quit()
        event.accept()




if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(':/icons/icon.ico'))
    app.setStyleSheet('MainWindow {background-image: url(:/icons/background.PNG); }')
    Dialog = MainWindow()
    Dialog.setWindowTitle("ESIM 1.0 (Elektronik Sinyal Isyarat Morse)")
    Dialog.showMaximized()
    sys.exit(app.exec_())