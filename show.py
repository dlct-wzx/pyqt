import os
import sys
from shutil import copyfile

import cv2
import numpy as np
import tifffile as tf
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QFileDialog
from pyexiv2 import Image

from ToolsUI import Ui_Dialog
from models import Model


def darkCurrentCorrection(tif, imageName):
    xmp = Image(imageName).read_xmp()
    tif = np.array(tif, dtype=np.float32)
    tif = tif / 65536.0 - float(xmp['Xmp.Camera.BlackCurrent']) / 65536.0
    return tif


def exposureTimeAndSensorGainCorrection(tif, imageName):
    xmp = Image(imageName).read_xmp()
    et = float(xmp['Xmp.drone-dji.ExposureTime'])
    sg = float(xmp['Xmp.drone-dji.SensorGain'])
    tif = tif / (et * sg * 1e-6)
    return tif


def vignettingCorrection(tif, imageName):
    xmp = Image(imageName).read_xmp()
    vdata = xmp['Xmp.drone-dji.VignettingData']
    vdata = vdata.split(', ')
    k0, k1, k2, k3, k4, k5 = [float(i) for i in vdata]
    rows, cols = tif.shape
    x, y = np.meshgrid(np.arange(cols), np.arange(rows))
    r = np.sqrt((x - cols / 2) ** 2 + (y - rows / 2) ** 2)
    polynomial_model = (k5 * r ** 6) + (k4 * r ** 5) + (k3 * r ** 4) + (k2 * r ** 3) + (k1 * r ** 2) + (k0 * r) + 1
    tif = tif * polynomial_model
    return tif


def incorporatedPhaseAlignment(tif, bindType):
    image = tif
    L, W = image.shape
    if bindType == 'blue':
        pos_x = -17
        pos_y = -19
    elif bindType == 'green':
        pos_x = -25
        pos_y = -14
    elif bindType == 'nir':
        pos_x = -27
        pos_y = -4
    elif bindType == 'red':
        pos_x = -14
        pos_y = -10
    elif bindType == 'red_edge':
        pos_x = 0
        pos_y = 21

    # print(pos_x, pos_y)
    pos_y1 = abs(pos_y)
    pos_x1 = abs(pos_x)

    image_pad = np.pad(image, ((pos_y1, pos_y1), (pos_x1, pos_x1)), 'constant', constant_values=(0, 0))
    if pos_y < 0:  # y轴负方向，图像上移
        image = image_pad[0:L, :]
    else:  # y轴正方向，图像下移
        image = image_pad[pos_y1 * 2:L + pos_y1 * 2, :]
    if pos_x < 0:  # x轴负方向，图像左移
        image = image[:, pos_x1 * 2:W + pos_x1 * 2]
    else:  # x轴正方向，图像右移
        image = image[:, 0:W]
    return image


class MyPyQT_Form(QtWidgets.QWidget, Ui_Dialog):
    def __init__(self):
        super(MyPyQT_Form, self).__init__()
        self.setupUi(self)

        self.RedSet.clicked.connect(self.pushSetButton_click)
        self.GreenSet.clicked.connect(self.pushSetButton_click)
        self.BlueSet.clicked.connect(self.pushSetButton_click)
        self.NIRSet.clicked.connect(self.pushSetButton_click)
        self.ReSet.clicked.connect(self.pushSetButton_click)

        self.RedSave.clicked.connect(self.pushSaveButton_click)
        self.GreenSave.clicked.connect(self.pushSaveButton_click)
        self.BlueSave.clicked.connect(self.pushSaveButton_click)
        self.NIRSave.clicked.connect(self.pushSaveButton_click)
        self.ReSave.clicked.connect(self.pushSaveButton_click)
        self.ResultSave.clicked.connect(self.pushSaveButton_click)

        self.IncorporatedPhaseAlignment.clicked.connect(self.pushIncorporatedPhaseAlignmentButton_click)
        self.DarkCurrentCorrection.clicked.connect(self.pushDarkCurrentCorrectionButton_click)
        self.ExposureTimeAndSensorGainCorrection.clicked.connect(self.pushExposureTimeAndSensorGainCorrectionButton_click)
        self.VignettingCorrection.clicked.connect(self.pushVignettingCorrectionButton_click)
        
        self.VI.clicked.connect(self.pushVIButton_click)

        self.ModelSet.currentIndexChanged.connect(self.modelSet)
        self.Seg.clicked.connect(self.modelDetect)

        self.CachaPath = "./Cache/"

        self.GreenPath = self.CachaPath + "Green.TIF"
        self.RedPath = self.CachaPath + "Red.TIF"
        self.BluePath = self.CachaPath + "Blue.TIF"
        self.NIRPath = self.CachaPath + "NIR.TIF"
        self.RePath = self.CachaPath + "RE.TIF"
        self.ResultPath = self.CachaPath + "Result.TIF"

        self.afterIncorporatedPhaseAlignmentGreenPath = self.CachaPath + "afterIncorporatedPhaseAlignmentGreenPath.TIF"
        self.afterIncorporatedPhaseAlignmentRedPath = self.CachaPath + "afterIncorporatedPhaseAlignmentRedPath.TIF"
        self.afterIncorporatedPhaseAlignmentBluePath = self.CachaPath + "afterIncorporatedPhaseAlignmentBluePath.TIF"
        self.afterIncorporatedPhaseAlignmentNIRPath = self.CachaPath + "afterIncorporatedPhaseAlignmentNIRPath.TIF"
        self.afterIncorporatedPhaseAlignmentRePath = self.CachaPath + "afterIncorporatedPhaseAlignmentRePath.TIF"

        self.afterDarkCurrentCorrectionGreenPath = self.CachaPath + "afterDarkCurrentCorrectionGreen.TIF"
        self.afterDarkCurrentCorrectionRedPath = self.CachaPath + "afterDarkCurrentCorrectionRed.TIF"
        self.afterDarkCurrentCorrectionBluePath = self.CachaPath + "afterDarkCurrentCorrectionBlue.TIF"
        self.afterDarkCurrentCorrectionNIRPath = self.CachaPath + "afterDarkCurrentCorrectionNIR.TIF"
        self.afterDarkCurrentCorrectionRePath = self.CachaPath + "afterDarkCurrentCorrectionRE.TIF"

        self.afterExposureTimeAndSensorGainCorrectionGreenPath = self.CachaPath + "afterExposureTimeAndSensorGainCorrectionGreen.TIF "
        self.afterExposureTimeAndSensorGainCorrectionRedPath = self.CachaPath + "afterExposureTimeAndSensorGainCorrectionRed.TIF"
        self.afterExposureTimeAndSensorGainCorrectionBluePath = self.CachaPath + "afterExposureTimeAndSensorGainCorrectionBlue.TIF"
        self.afterExposureTimeAndSensorGainCorrectionNIRPath = self.CachaPath + "afterExposureTimeAndSensorGainCorrectionNIR.TIF"
        self.afterExposureTimeAndSensorGainCorrectionRePath = self.CachaPath + "afterExposureTimeAndSensorGainCorrectionRE.TIF"

        self.afterVignettingCorrectionGreenPath = self.CachaPath + "afterVignettingCorrectionGreen.TIF"
        self.afterVignettingCorrectionRedPath = self.CachaPath + "afterVignettingCorrectionRed.TIF"
        self.afterVignettingCorrectionBluePath = self.CachaPath + "afterVignettingCorrectionBlue.TIF"
        self.afterVignettingCorrectionNIRPath = self.CachaPath + "afterVignettingCorrectionNIR.TIF"
        self.afterVignettingCorrectionRePath = self.CachaPath + "afterVignettingCorrectionRE.TIF"


        self.model = Model()

    def flashAllImage(self):
        self.RedBind.setPixmap(QPixmap(self.RedPath).scaled(320, 260))
        self.GreenBind.setPixmap(QPixmap(self.GreenPath).scaled(320, 260))
        self.BlueBind.setPixmap(QPixmap(self.BluePath).scaled(320, 260))
        self.NIRBind.setPixmap(QPixmap(self.NIRPath).scaled(320, 260))
        self.ReBind.setPixmap(QPixmap(self.RePath).scaled(320, 260))

    def pushSetButton_click(self):
        buttonName = self.sender().objectName()
        print(buttonName + ' is clicked')
        fileName, _ = QFileDialog.getOpenFileName(self, "请选择文件", "", "All Files (*);;Text Files (*.txt)")
        pix = QPixmap(fileName)
        pix.scaled(320, 260)
        self.__dict__[buttonName[:-3] + 'Bind'].setPixmap(pix)
        self.__dict__[buttonName[:-3] + 'Bind'].setScaledContents(True)
        copyfile(fileName, self.__dict__[buttonName[:-3] + 'Path'])

    def pushSaveButton_click(self):
        buttonName = self.sender().objectName()
        print(buttonName + ' is clicked')
        ImagePath = self.__dict__[buttonName[:-4] + 'Path']
        saveFilePath, _ = QFileDialog.getSaveFileName(self, "保存文件",
                                                      "C:/Users/Administrator/Desktop/" + ImagePath.split('/')[-1],
                                                      "all files(*)")
        copyfile(ImagePath, saveFilePath)

    def pushIncorporatedPhaseAlignmentButton_click(self):
        print('IncorporatedPhaseAlignment is clicked')
        red = tf.imread(self.RedPath)
        green = tf.imread(self.GreenPath)
        blue = tf.imread(self.BluePath)
        nir = tf.imread(self.NIRPath)
        re = tf.imread(self.RePath)

        red = incorporatedPhaseAlignment(red, 'red')
        green = incorporatedPhaseAlignment(green, 'green')
        blue = incorporatedPhaseAlignment(blue, 'blue')
        nir = incorporatedPhaseAlignment(nir, 'nir')
        re = incorporatedPhaseAlignment(re, 'red_edge')

        tf.imwrite(self.afterIncorporatedPhaseAlignmentRedPath, red)
        tf.imwrite(self.afterIncorporatedPhaseAlignmentGreenPath, green)
        tf.imwrite(self.afterIncorporatedPhaseAlignmentBluePath, blue)
        tf.imwrite(self.afterIncorporatedPhaseAlignmentNIRPath, nir)
        tf.imwrite(self.afterIncorporatedPhaseAlignmentRePath, re)

    def pushDarkCurrentCorrectionButton_click(self):
        print('DarkCurrentCorrection is clicked')
        red = tf.imread(self.afterIncorporatedPhaseAlignmentRedPath)
        green = tf.imread(self.afterIncorporatedPhaseAlignmentGreenPath)
        blue = tf.imread(self.afterIncorporatedPhaseAlignmentBluePath)
        nir = tf.imread(self.afterIncorporatedPhaseAlignmentNIRPath)
        re = tf.imread(self.afterIncorporatedPhaseAlignmentRePath)
        red = darkCurrentCorrection(red, self.RedPath)
        green = darkCurrentCorrection(green, self.GreenPath)
        blue = darkCurrentCorrection(blue, self.BluePath)
        nir = darkCurrentCorrection(nir, self.NIRPath)
        re = darkCurrentCorrection(re, self.RePath)
        tf.imwrite(self.afterDarkCurrentCorrectionBluePath, blue)
        tf.imwrite(self.afterDarkCurrentCorrectionGreenPath, green)
        tf.imwrite(self.afterDarkCurrentCorrectionRedPath, red)
        tf.imwrite(self.afterDarkCurrentCorrectionNIRPath, nir)
        tf.imwrite(self.afterDarkCurrentCorrectionRePath, re)

    def pushExposureTimeAndSensorGainCorrectionButton_click(self):
        print('ExposureTimeAndSensorGainCorrection is clicked')
        blue = tf.imread(self.afterDarkCurrentCorrectionBluePath)
        green = tf.imread(self.afterDarkCurrentCorrectionGreenPath)
        red = tf.imread(self.afterDarkCurrentCorrectionRedPath)
        nir = tf.imread(self.afterDarkCurrentCorrectionNIRPath)
        re = tf.imread(self.afterDarkCurrentCorrectionRePath)

        red = exposureTimeAndSensorGainCorrection(red, self.RedPath)
        green = exposureTimeAndSensorGainCorrection(green, self.GreenPath)
        blue = exposureTimeAndSensorGainCorrection(blue, self.BluePath)
        nir = exposureTimeAndSensorGainCorrection(nir, self.NIRPath)
        re = exposureTimeAndSensorGainCorrection(re, self.RePath)

        tf.imwrite(self.afterExposureTimeAndSensorGainCorrectionBluePath, blue)
        tf.imwrite(self.afterExposureTimeAndSensorGainCorrectionGreenPath, green)
        tf.imwrite(self.afterExposureTimeAndSensorGainCorrectionRedPath, red)
        tf.imwrite(self.afterExposureTimeAndSensorGainCorrectionNIRPath, nir)
        tf.imwrite(self.afterExposureTimeAndSensorGainCorrectionRePath, re)


    def pushVignettingCorrectionButton_click(self):
        print('VignettingCorrection is clicked')
        red = tf.imread(self.afterExposureTimeAndSensorGainCorrectionRedPath)
        green = tf.imread(self.afterExposureTimeAndSensorGainCorrectionGreenPath)
        blue = tf.imread(self.afterExposureTimeAndSensorGainCorrectionBluePath)
        nir = tf.imread(self.afterExposureTimeAndSensorGainCorrectionNIRPath)
        re = tf.imread(self.afterExposureTimeAndSensorGainCorrectionRePath)

        red = vignettingCorrection(red, self.RedPath)
        green = vignettingCorrection(green, self.GreenPath)
        blue = vignettingCorrection(blue, self.BluePath)
        nir = vignettingCorrection(nir, self.NIRPath)
        re = vignettingCorrection(re, self.RePath)

        tf.imwrite(self.afterVignettingCorrectionBluePath, blue)
        tf.imwrite(self.afterVignettingCorrectionGreenPath, green)
        tf.imwrite(self.afterVignettingCorrectionRedPath, red)
        tf.imwrite(self.afterVignettingCorrectionNIRPath, nir)
        tf.imwrite(self.afterVignettingCorrectionRePath, re)


    def pushVIButton_click(self):
        print('VI is clicked')
        VIName = self.VISet.currentText()
        red = tf.imread(self.afterVignettingCorrectionRedPath)
        green = tf.imread(self.afterVignettingCorrectionGreenPath)
        blue = tf.imread(self.afterVignettingCorrectionBluePath)
        nir = tf.imread(self.afterVignettingCorrectionNIRPath)
        re = tf.imread(self.afterVignettingCorrectionRePath)
        if VIName == 'NDVI':
            print('NDVI is selected')
            vi = (nir - red) / (nir + red)
        elif VIName == 'EVI':
            print('EVI is selected')
            vi = 2.5 * (nir - red) / (nir + 6 * red - 7.5 * blue + 1)
        elif VIName == "RVI":
            print('RVI is selected')
            vi = red / nir
        elif VIName == 'ARI':
            vi = 1/green - 1/re
        elif VIName == 'OSAVI':
            vi = (nir - red) / (nir + red + 0.16)
        vi = np.uint8(vi * 255)
        vi = np.uint8(vi)
        tf.imwrite(self.ResultPath, vi)
        # image = cv2.imread(self.CachaPath+ VIName + '.TIF')
        # PsedoImage2 = cv2.applyColorMap(image, colormap=cv2.COLORMAP_HSV)
        # cv2.imwrite(self.CachaPath + VIName + '.jpg', PsedoImage2)
        # print('VI is done')

        self.Result.setPixmap(QPixmap(self.ResultPath).scaled(320, 260))

    def modelSet(self):
        modelName = self.ModelSet.currentText()
        print(modelName + ' is selected')
        self.EncoderSet.clear()
        for i in self.model.encoderList[modelName]:
            self.EncoderSet.addItem(i)

    def modelDetect(self):
        modelName = self.ModelSet.currentText()
        encoderName = self.EncoderSet.currentText()
        print('use model ' + modelName + 'and encoder ' + encoderName + ' to detected')
        self.model.detect(modelName, encoderName, self.RedPath, self.GreenPath, self.BluePath, self.NIRPath,
                          self.RePath)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        print('close')
        # for file in os.listdir(self.CachaPath):
        #     os.remove(self.CachaPath + file)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    my_pyqt_form = MyPyQT_Form()
    my_pyqt_form.show()
    # apply_stylesheet(app, theme='light_cyan.xml')
    sys.exit(app.exec_())
