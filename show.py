import sys
import os
import tifffile as tf
import numpy as np
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import QPixmap
from shutil import copyfile
from ToolsUI import Ui_Dialog
from qt_material import apply_stylesheet
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QLineEdit, QMainWindow, QFileDialog
from models import Model


def incorporatedPhaseAlignment(imageName, bindType):
    image = tf.imread(imageName)
    os.remove(imageName)
    W, L = image.shape
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
    tf.imwrite(imageName, image)


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

        self.VI.clicked.connect(self.pushVIButton_click)

        self.ModelSet.currentIndexChanged.connect(self.modelSet)
        self.Seg.clicked.connect(self.modelDetect)

        self.CachaPath = "./Cache/"
        self.GreenPath = self.CachaPath + "Green.TIF"
        self.RedPath = self.CachaPath + "Red.TIF"
        self.BluePath = self.CachaPath + "Blue.TIF"
        self.NIRPath = self.CachaPath + "NIR.TIF"
        self.RePath = self.CachaPath + "RE.TIF"
        self.VIPath = self.CachaPath + "VI.TIF"

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
        incorporatedPhaseAlignment(self.RedPath, 'red')
        print('red is done')
        incorporatedPhaseAlignment(self.GreenPath, 'green')
        incorporatedPhaseAlignment(self.BluePath, 'blue')
        incorporatedPhaseAlignment(self.NIRPath, 'nir')
        incorporatedPhaseAlignment(self.RePath, 'red_edge')
        print('green is done')
        self.flashAllImage()

    def pushVIButton_click(self):
        print('VI is clicked')
        VIName = self.VISet.currentText()
        red = tf.imread(self.RedPath)
        green = tf.imread(self.GreenPath)
        blue = tf.imread(self.BluePath)
        nir = tf.imread(self.NIRPath)
        re = tf.imread(self.RePath)
        if VIName == 'NDVI':
            print('NDVI is selected')
            vi = (nir - red) / (nir + red)
        elif VIName == 'EVI':
            print('EVI is selected')
            vi = 2.5 * (nir - red) / (nir + 6 * red - 7.5 * blue + 1)
        elif VIName == "RVI":
            print('RVI is selected')
            vi = red / nir
        print('VI is done')
        tf.imwrite(self.VIPath, vi)
        self.Result.setPixmap(QPixmap(self.VIPath).scaled(320, 260))

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
