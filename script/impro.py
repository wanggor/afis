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

def rotate_bound(image, angle):
    # grab the dimensions of the image and then determine the
    # center
    (h, w) = image.shape[:2]
    (cX, cY) = (w // 2, h // 2)
    # grab the rotation matrix (applying the negative of the
    # angle to rotate clockwise), then grab the sine and cosine
    # (i.e., the rotation components of the matrix)
    M = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])
    # compute the new bounding dimensions of the image
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))
    # adjust the rotation matrix to take into account translation
    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY
    # perform the actual rotation and return the image
    return cv2.warpAffine(image, M, (nW, nH))
    

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
    dataDurasiSignal = pyqtSignal(dict)
    def __init__(self, 
            cap = None, 
            parent = None, 
            const = {}, 
            treshold = 150,
            minSize = 0,
            angle = 0):
        super(Camera_stream, self).__init__(parent)

        fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
        self.cap = cv2.VideoCapture()
        self.cap.open(cap + cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FOURCC, fourcc)
        # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        self.stop = False
        self.const = const
        self.treshold = treshold

        self.morse = Morse(self.treshold)
        self.msg = Msg(self.const)
        self.isSetting = False
        self.isReading = False
        self.minSize = minSize
        self.angle = angle


    def __del__(self):
        self.quit()
        self.wait()

    def changeSetting(self, val):
        self.isSetting = val

    def updateConst(self, const, treshold, minSize):
        self.const = const
        self.treshold = treshold
        self.minSize = minSize
        self.morse.updateConst(treshold)

    def changeReading(self, val):
        self.isReading = val
        self.msg = Msg(self.const)
        return self.isReading

    def run(self):
        while  not self.stop :
            ret, frame = self.cap.read()
            minValue = 0.1
            if ret:
                frame = rotate_bound(frame, self.angle)
                frame_bin = self.morse.rgb2bin(frame)
                
                percentage = (np.sum(frame_bin)/ 255) / frame_bin.size
                
                if percentage > (self.minSize / 100):
                    value = 1
                else :
                    value = 0

                dataDurasi , dataMorse = self.msg.parsingData(value)
                
                if self.isSetting:
                    frame = cv2.cvtColor(frame_bin,cv2.COLOR_GRAY2RGB)


                frame = imutils.resize(frame, width=640 , height=480 )
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                if self.isSetting:
                    wb = 4
                    if value:
                        rgbImage= cv2.copyMakeBorder(rgbImage,wb,wb,wb,wb,cv2.BORDER_CONSTANT,value=[0, 0,255])
                    else :
                        rgbImage= cv2.copyMakeBorder(rgbImage,wb,wb,wb,wb,cv2.BORDER_CONSTANT,value=[255,0,0])
                    self.dataDurasiSignal.emit(dataDurasi)
                
                convertToQtFormat = QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0], QImage.Format_RGB888)
                p = convertToQtFormat.scaled(rgbImage.shape[1], rgbImage.shape[0], Qt.KeepAspectRatio)
                
                if self.isReading:
                    self.data.emit(dataMorse)
                else:
                    self.data.emit({})
                    
                self.changePixmap.emit(p)
                
        self.cap.release()

class Morse():
    def __init__(self, treshold):
        self.treshold = treshold
        dataObj = {}

    def updateConst(self, treshold):
        self.treshold = treshold

    def rgb2bin(self, image):
        low  = np.array([30, 0, 150])
        high = np.array([90,255, 255])   
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        thresh = cv2.inRange(hsv, low, high)


        # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # ret,thresh = cv2.threshold(gray,self.treshold,255,cv2.THRESH_BINARY)
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
        self.zero_tick  =config["zero-tick"]
        self.one_tick   = config["one-tick"]
        self.split_tick = config["space-tick"]
        self.tolerance = config["tolerance"]

        self.data = {}
        self.lastTime = {}
        self.value = {}
        self.duration = {}

        self.data_durasi = {
            "zero" : [0,0,0,0,0,0,0,0,0,0],
            "one" : [0,0,0,0,0,0,0,0,0,0],
        }

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
                self.data_durasi["one"].pop(0)
                self.data_durasi["one"].append( float("{:.2f}".format( self.duration[index])) )
                if self.duration[index] > (self.one_tick - self.tolerance) and  self.duration[index] < (self.one_tick + self.tolerance) :
                    self.data[index][-1][-1] += "1"
                elif self.duration[index] > (self.zero_tick - self.tolerance) and  self.duration[index] < (self.zero_tick + self.tolerance):
                    self.data[index][-1][-1] += "0"
            else:
                self.data_durasi["zero"].pop(0)
                self.data_durasi["zero"].append(float("{:.2f}".format( self.duration[index])) )
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

    def parsingData(self, value):
        self.update(0, value)
        return self.data_durasi.copy(), self.data.copy()





        



        
