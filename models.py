import tifffile as tf
import numpy as np

class Model:
    def __init__(self):
        self.modelList = ['DBFormer', 'SegFormer', 'MaskFormer', 'SETR', 'DeepLabV3+', 'PSPNet', 'UNet', 'HRNetV2']
        self.encoderList = {
            'DBFormer': ['DBEC-B0', 'DBEC-B1', 'DBEC-B2', 'DBEC-B3', 'DBEC-B4', 'DBEC-B5'],
            'SegFormer': ['MiT-B0', 'MiT-B1', 'MiT-B2', 'MiT-B3', 'MiT-B4', 'MiT-B5'],
            'MaskFormer': ['ViT-T', 'ViT-S', 'ViT-B', 'ViT-L'],
            'SETR': ['ViT-L'],
            'DeepLabV3+': ['Xception'],
            'PSPNet': ['ResNet50'],
            'UNet': ['ResNet50'],
            'HRNetV2': ['HRNetV2-w18', 'HRNetV2-w32', 'HRNetV2-w48']
        }
        self.models = dict()

    def generateModel(self, modelName, encoderName):
        model = None
        if modelName == 'DBFormer':
            if 'DBFormer_' + encoderName not in self.models:
                model = '222'
                self.models['DBFormer_' + encoderName] = model
            else:
                model = self.models['DBFormer_' + encoderName]
        elif modelName == 'SegFormer':
            if 'SegFormer_' + encoderName not in self.models:
                model = '333'
                self.models['SegFormer_' + encoderName] = model
            else:
                model = self.models['SegFormer_' + encoderName]
        elif modelName == 'MaskFormer':
            if 'MaskFormer_' + encoderName not in self.models:
                model = '444'
                self.models['MaskFormer_' + encoderName] = model
            else:
                model = self.models['MaskFormer_' + encoderName]
        elif modelName == 'SETR':
            if 'SETR_' + encoderName not in self.models:
                model = '555'
                self.models['SETR_' + encoderName] = model
            else:
                model = self.models['SETR_' + encoderName]
        elif modelName == 'DeepLabV3+':
            if 'DeepLabV3+_' + encoderName not in self.models:
                model = '666'
                self.models['DeepLabV3+_' + encoderName] = model
            else:
                model = self.models['DeepLabV3+_' + encoderName]
        elif modelName == 'PSPNet':
            if 'PSPNet_' + encoderName not in self.models:
                model = '777'
                self.models['PSPNet_' + encoderName] = model
            else:
                model = self.models['PSPNet_' + encoderName]
        elif modelName == 'UNet':
            if 'UNet_' + encoderName not in self.models:
                model = '888'
                self.models['UNet_' + encoderName] = model
            else:
                model = self.models['UNet_' + encoderName]
        elif modelName == 'HRNetV2':
            if 'HRNetV2_' + encoderName not in self.models:
                model = '999'
                self.models['HRNetV2_' + encoderName] = model
            else:
                model = self.models['HRNetV2_' + encoderName]

        return model

    def detect(self, modelName, encoderName, redPath, greenPath, bluePath, nirPath, rePath):
        model = self.generateModel(modelName, encoderName)
        print('use model ' + model + ' to detect')
        print(redPath)
        print(greenPath)
        print(bluePath)
        print(nirPath)
        print(rePath)
        red = tf.imread(redPath)[np.newaxis, :]
        green = tf.imread(greenPath)[np.newaxis, :]
        blue = tf.imread(bluePath)[np.newaxis, :]
        nir = tf.imread(nirPath)[np.newaxis, :]
        re = tf.imread(rePath)[np.newaxis, :]
        rvi = red / nir
        rvi = np.where(rvi < 0.8, 0, 1)
        tif = np.concatenate(([blue, green, red, re, nir, rvi]), axis=0)
        print(tif.shape)

