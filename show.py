import sys
import os
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import QPixmap
from shutil import copyfile
from ToolsUI import Ui_Dialog
from qt_material import apply_stylesheet
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QLineEdit, QMainWindow, QFileDialog
from models import Model

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

        self.ModelSet.currentIndexChanged.connect(self.modelSet)
        self.Seg.clicked.connect(self.modelDetect)
        self.CachaPath = "./Cache/"
        self.GreenPath = self.CachaPath + "Green.TIF"
        self.RedPath = self.CachaPath + "Red.TIF"
        self.BluePath = self.CachaPath + "Blue.TIF"
        self.NIRPath = self.CachaPath + "NIR.TIF"
        self.RePath = self.CachaPath + "RE.TIF"

        self.model = Model()

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

    def modelSet(self):
        modelName = self.ModelSet.currentText()
        print(modelName + ' is selected')
        self.EncoderSet.clear()
        for i in self.model.encoderList[modelName]:
            self.EncoderSet.addItem(i)

    def modelDetect(self):
        modelName = self.ModelSet.currentText()
        encoderName = self.EncoderSet.currentText()
        print(modelName + ' is selected')
        print(encoderName + ' is selected')
        self.model.detect(modelName, encoderName, self.RedPath, self.GreenPath, self.BluePath, self.NIRPath, self.RePath)


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
