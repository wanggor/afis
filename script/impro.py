import PyQt5
import imutils
from PyQt5.QtGui import QImage
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from imutils.video import VideoStream

import cv2
import numpy as np
import time
import datetime

import tracker as tracker
import constant as constant

def check_available_camera():
    data = []
    for i in range(10):
        try:
            cap = cv2.VideoCapture(i)
            if cap.read()[0]:
                data.append(i)
            cap.release()
        except:
            pass
    return data
        

class Camera_stream(QThread):
    changePixmap = pyqtSignal(QImage)
    data = pyqtSignal(dict)
    def __init__(self, cap = None, parent = None, const = {}):
        super(Camera_stream, self).__init__(parent)

        fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
        self.cap = cv2.VideoCapture()
        self.cap.open(cap + cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FOURCC, fourcc)
        # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        self.stop = False
        self.const = const

        self.morse = Morse(self.const)
        self.msg = Msg(self.const)
        self.tracker = tracker.CentroidTracker(maxDisappeared=500, maxDistance=50)
        self.mode = "Tunggal"
        self.isSetting = False
        self.isReading = False

    def __del__(self):
        self.quit()
        self.wait()

    def change_mode(self, val):
        self.tracker = tracker.CentroidTracker(maxDisappeared=30, maxDistance=50)
        self.mode = val

    def changeSetting(self, val):
        self.isSetting = val

    def updateConst(self, const):
        self.const = const
        self.morse.updateConst(const)

    def changeReading(self, val):
        self.isReading = val
        self.tracker.clear()
        return self.isReading

    def run(self):
        while  not self.stop :
            ret, frame = self.cap.read()
            if ret:
                frame_bin = self.morse.rgb2bin(frame)
                data = self.tracker.update([])
                bbox = self.morse.getContour(frame_bin)

                data = self.tracker.update(bbox)

                dataMorse = self.msg.parsingData(frame_bin, data)
                
                if self.isSetting:
                    frame = cv2.cvtColor(frame_bin,cv2.COLOR_GRAY2RGB)

                self.morse.drawRect(frame, data)


                frame = imutils.resize(frame, width=640 , height=480 )
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                convertToQtFormat = QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0], QImage.Format_RGB888)
                p = convertToQtFormat.scaled(rgbImage.shape[1], rgbImage.shape[0], Qt.KeepAspectRatio)
                
                if self.isReading:
                    self.data.emit(dataMorse)
                    
                self.changePixmap.emit(p)
                
        self.cap.release()

class Morse():
    def __init__(self, const):
        self.const = const
        self.blurr_core = constant.shape_config["blurr_core"]
        self.kernelSize = self.const['kernel']
        self.kernel = cv2.getStructuringElement(cv2.MORPH_CROSS,(self.kernelSize,self.kernelSize))
        self.minSize = self.const['min']
        self.maxSize = self.const['max']
        self.shapeTolarance = constant.shape_config["shapeTolarance"]

        dataObj = {}

    def updateConst(self, const):
        self.const = const
        self.blurr_core = constant.shape_config["blurr_core"]
        self.kernelSize = self.const['kernel']
        self.kernel = cv2.getStructuringElement(cv2.MORPH_CROSS,(self.kernelSize,self.kernelSize))
        self.minSize = self.const['min']
        self.maxSize = self.const['max']
        self.shapeTolarance = constant.shape_config["shapeTolarance"]

    def rgb2bin(self, image):
        low  = np.array([self.const["H"], self.const["S"], self.const["V"]])
        high = np.array([self.const["Hmax"], self.const["Smax"], self.const["Vmax"]])   
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        thresh = cv2.inRange(hsv, low, high)
        # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # gray = cv2.GaussianBlur(gray, (self.kernelSize+self.blurr_core, self.kernelSize+self.blurr_core), 0)
        # ret,thresh = cv2.threshold(gray,self.thresholdValue,255,cv2.THRESH_BINARY)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, self.kernel)
        return thresh

    def getContour(self,thresh):
        contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        data = []
        H,W = thresh.shape
        for c in contours:
            x,y,w,h = cv2.boundingRect(c)  
            if np.abs(np.subtract(w,h))< int(self.shapeTolarance * H) and w > int(self.minSize * H) and w < int(self.maxSize * H):
                cx = x+(w//2)
                cy = y+(h//2)
                approx = len(cv2.approxPolyDP(c,0.01*cv2.arcLength(c,True),True))
                M = cv2.moments(c)
                cxO = int(M['m10']/M['m00'])
                cyO = int(M['m01']/M['m00'])
                corr = constant.shape_config["center-correction"]
                if approx > constant.shape_config["min-circle-coorection"] and (abs(cx-cxO)/w) < corr  and (abs(cy-cyO)/h) < corr:
                    data.append([cx,cy,w,h, 0, approx])
                # data.append([cx,cy,w,h, 0, approx])
        return data

    def drawRect(self, frame, data):
        ind = 0
        for key, item in data.items():
            ind += 1
            cx = int(item[0])
            cy = int(item[1])
            w  = int(item[2])
            h  = int(item[3])
            x  = cx - w //2
            y  = cy - h // 2

            frame = cv2.rectangle(frame, (x, y), (x+w, y+h), (0,0,255), 2, )
            # Using cv2.putText() method 

            frame = cv2.rectangle(frame, (x, y+h-30), (x+20, y+h), (0,0,255), -1, )
            frame = cv2.putText(frame, str(ind), (x+8, y+h), cv2.FONT_HERSHEY_SIMPLEX , 0.5, 
                            (255,255,255), 3, cv2.LINE_AA, False)  
        return frame

class Msg():
    def __init__(self, config):
       
        self.zero_tick  = constant.mode_detection[config["tempo"]]["zero-tick"]
        self.one_tick   = constant.mode_detection[config["tempo"]]["one-tick"]
        self.split_tick = constant.mode_detection[config["tempo"]]["space-tick"]
        self.tolerance = constant.mode_detection[config["tempo"]]["tolerance"]

        self.data = {}
        self.lastTime = {}
        self.value = {}
        self.duration = {}

        self.mors_code = {
            "01":"A",
            "1000":"B",
            "1010":"C",
            "100":"D",
            "0":"E",
            "0010":"F",
            "110":"G",
            "0000":"H",
            "00":"I",
            "0111":"J",
            "101":"K",
            "0100":"L",
            "11":"M",
            "10":"N",
            "111":"O",
            "0110":"P",
            "1101":"Q",
            "010":"R",
            "000":"S",
            "1":"T",
            "001":"U",
            "0001":"V",
            "011":"W",
            "1001":"X",
            "1011":"Y",
            "1100":"Z",
            "01111":"1",
            "00111":"2",
            "00011":"3",
            "00001":"4",
            "00000":"5",
            "10000":"6",
            "11000":"7",
            "11100":"8",
            "11110":"9",
            "11111":"0",
        }

    def update(self, index, value):
        if index not in self.data.keys():
            self.data[index] = []
            self.lastTime[index] = time.time()
            self.value[index] = None
            self.duration[index] = 0

        if self.value[index] is None :
            self.value[index] = value
            self.data[index].append([""])

        if value != self.value[index]:

            if self.value[index] == 1:
                # print("one value", self.duration[index])
                if self.duration[index] > (self.one_tick - self.tolerance) and  self.duration[index] < (self.one_tick + self.tolerance) :
                    self.data[index][-1][-1] += "1"
                elif self.duration[index] > (self.zero_tick - self.tolerance) and  self.duration[index] < (self.zero_tick + self.tolerance):
                    self.data[index][-1][-1] += "0"
            else:
                # print("zero-value", self.duration[index])
                if self.duration[index] > self.split_tick:
                    if len(self.data[index][-1]) > 0:
                        if self.data[index][-1][-1] in self.mors_code.keys():
                            text = self.mors_code[self.data[index][-1][-1]]
                            self.data[index][-1][-1] = text
                        else:
                            self.data[index][-1] = [""]
                        self.data[index].append([""])

            self.value[index] = value
            self.duration[index] = 0
            self.lastTime[index] = time.time()
            
        else:
            self.duration[index] = time.time() - self.lastTime[index]
            
            if self.value[index] == 0 and self.duration[index] > self.split_tick:
                if self.data[index][-1][-1] in self.mors_code.keys():
                    text = self.mors_code[self.data[index][-1][-1]]
                    self.data[index][-1][-1] = text
                else:
                    self.data[index][-1] = [""]
                self.data[index].append([""])

    def parsingData(self, thres, data):
        for n, item in enumerate(data.values()):
            cx,cy,w,h = int(item[0]),int(item[1]),int(item[2]),int(item[3])
            x1, y1, x2, y2 = (cx - w//2), (cy - h//2), (cx + w//2), (cy + h//2)
            roi = h * w
            area = np.sum(thres[y1:y2, x1:x2]) / 255
            rasio = area/roi
            if rasio > 0.1 :
                self.update(n, 1)
            else:
                self.update(n, 0)
        return self.data.copy()





        



        
