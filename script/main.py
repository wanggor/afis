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
        # self.ui = uic.loadUi('interface.ui',self)

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
        self.ui.radioButton_putih.toggled.connect(self.initSlide)
        self.ui.radioButton_kuning.toggled.connect(self.initSlide)
        self.ui.pushButton_startRead.clicked.connect(self.startRead)
        self.ui.pushButton_saveconst.clicked.connect(self.updateConst)
        self.ui.pushButton_testLampu.clicked.connect(self.testLampu)
        self.ui.frame_4.hide()
        # self.ui.frame_color.hide()
        # self.ui.lineEdit_code_send.hide()
        # self.ui.label_5.hide()
        self.ui.frame_setting.hide()

        self.itemList = {}
        self.encrypeList = {}
        self.start = False
        for i in range(2):
        # for i in impro.check_available_camera():
            self.ui.comboBox_camera.addItem("Camera " + str(i+1))

        self.slider = [
            self.ui.horizontalSlider_h,
            self.ui.horizontalSlider_s,
            self.ui.horizontalSlider_v,
            self.ui.horizontalSlider_min,
            self.ui.horizontalSlider_max,
            self.ui.horizontalSlider_kernel,
            self.ui.horizontalSlider_hmax,
            self.ui.horizontalSlider_smax,
            self.ui.horizontalSlider_vmax,
        ]
        self.slider_text = [
            self.ui.label_h,
            self.ui.label_s,
            self.ui.label_v,
            self.ui.label_min,
            self.ui.label_max,
            self.ui.label_kernel,
            self.ui.label_hmax,
            self.ui.label_smax,
            self.ui.label_vmax,
        ]

        self.slider[0].valueChanged.connect(lambda: self.sliderChange(0))
        self.slider[1].valueChanged.connect(lambda: self.sliderChange(1))
        self.slider[2].valueChanged.connect(lambda: self.sliderChange(2))
        self.slider[3].valueChanged.connect(lambda: self.sliderChange(3))
        self.slider[4].valueChanged.connect(lambda: self.sliderChange(4))
        self.slider[5].valueChanged.connect(lambda: self.sliderChange(5))
        self.slider[6].valueChanged.connect(lambda: self.sliderChange(6))
        self.slider[7].valueChanged.connect(lambda: self.sliderChange(7))
        self.slider[8].valueChanged.connect(lambda: self.sliderChange(8))

        self.initSlide()
        self.isSetting = True
        self.camera = None
        self.isreading= False
    
    def initSlide(self):
        color = self.get_config()["color"]
        self.initslidevalue( 0, constant.color_option[color]["H"] )
        self.initslidevalue( 1, constant.color_option[color]["S"] )
        self.initslidevalue( 2, constant.color_option[color]["V"] )
        self.initslidevalue( 3, int(constant.shape_config["minSize"] * 100))
        self.initslidevalue( 4, int(constant.shape_config["maxSize"] * 100))
        self.initslidevalue( 5, constant.shape_config["kernelSize"] )
        self.initslidevalue( 6, constant.color_option[color]["Hmax"] )
        self.initslidevalue( 7, constant.color_option[color]["Smax"] )
        self.initslidevalue( 8, constant.color_option[color]["Vmax"] )

    def updateConst(self):
        if self.camera is not None:
            cons = self.get_constant()
            self.camera.updateConst(cons)

    def changeSetting(self):
        if self.isSetting:
            if self.camera is not None:
                self.camera.changeSetting(True)
            self.ui.frame_setting.show()
        else:
            if self.camera is not None:
                self.camera.changeSetting(False)
            self.ui.frame_setting.hide()
        self.isSetting = not self.isSetting

    def initslidevalue(self, index, value):
        self.slider[index].setValue(value)
        self.slider_text[index].setText(str(value))
        
    def sliderChange(self, index):
        self.slider_text[index].setText(str(self.slider[index].value()))
        
    def get_config(self):
        if self.ui.radioButton_lambat.isChecked() : 
            mode_send = 1
        elif self.ui.radioButton_cepat.isChecked() :
            mode_send = 3
        else:
            mode_send = 2

        if self.ui.radioButton_putih.isChecked() : 
            color_send = 1
        else:
            color_send = 2
        return {"color" : color_send, "mode" : mode_send}

    def send(self):

        config =  self.get_config()   
        code = self.ui.lineEdit_code_send.text()
        msg = encryption.encode(code, self.ui.textEdit_msg_send.toPlainText())
        print(msg)
        
        url = "http://192.168.4.1/text?"+str(config["mode"])+str(config["color"])+msg
        self.senderHttp = sender.SendHttp(parent=self, url=url)
        self.senderHttp.respon.connect(self.getRespon)
        self.senderHttp.start()
        self.ui.pushButton_send.setEnabled(False)

    def testLampu(self):
        url = "http://192.168.4.1/text?"
        self.senderHttp = sender.SendHttp(parent=self, url=url)
        self.senderHttp.respon.connect(self.getRespon)
        self.senderHttp.start()

    @pyqtSlot(str)
    def getRespon(self, respon):
        self.ui.pushButton_send.setEnabled(True)

    def get_constant(self):
        return {
            "H"     : self.slider[0].value(),
            "S"     : self.slider[1].value(),
            "V"     : self.slider[2].value(),
            "min"   : self.slider[3].value()/100,
            "max"   : self.slider[4].value()/100,
            "kernel": self.slider[5].value(),
            "Hmax"  : self.slider[6].value(),
            "Smax"  : self.slider[7].value(),
            "Vmax"  : self.slider[8].value(),
            "tempo" : self.get_config()['mode']
        }

    def startCamera(self):
        if not (self.start) :
            cons = self.get_constant()
            self.camera = impro.Camera_stream(cap = self.comboBox_camera.currentIndex(), parent = self, const = cons)
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
            self.camera = None

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
                self.itemList = {}
                self.encrypeList = {}
                self.ui.listView_msg.blockSignals(True)
                self.ui.listView_msg.clear()
                self.ui.pushButton_startRead.setText("Stop Membaca")
            else:
                self.camera.changeReading(False)
                self.ui.pushButton_startRead.setText("Mulai Membaca")

        

    def modeDeteksi(self, radio):
        if radio.isChecked():
            mode = radio.text()

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
        # self.camera.stop = True
        time.sleep(1)
        self.camera.quit()
        event.accept()




if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(':/icons/icon.ico'))
    app.setStyleSheet('MainWindow {background-image: url(:/icons/background.PNG); }')
    Dialog = MainWindow()
    Dialog.setWindowTitle("AFIS")
    Dialog.showMaximized()
    sys.exit(app.exec_())