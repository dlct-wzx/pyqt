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

    def generateModel(self, modelName, encoderName):
        model = '111'

        if modelName == 'DBFormer':
            if self.__dict__['DBFormer_' + encoderName] is None:
                model = '222'
                self.__dict__['DBFormer_' + encoderName] = model
            else:
                model = self.__dict__['DBFormer_' + encoderName]
        elif modelName == 'SegFormer':
            if self.__dict__['SegFormer_' + encoderName] is None:
                model = '333'
                self.__dict__['SegFormer_' + encoderName] = model
            else:
                model = self.__dict__['SegFormer_' + encoderName]
        elif modelName == 'MaskFormer':
            if self.__dict__['MaskFormer_' + encoderName] is None:
                model = '444'
                self.__dict__['MaskFormer_' + encoderName] = model
            else:
                model = self.__dict__['MaskFormer_' + encoderName]
        elif modelName == 'SETR':
            if self.__dict__['SETR_' + encoderName] is None:
                model = '555'
                self.__dict__['SETR_' + encoderName] = model
            else:
                model = self.__dict__['SETR_' + encoderName]
        elif modelName == 'DeepLabV3+':
            if self.__dict__['DeepLabV3+_' + encoderName] is None:
                model = '666'
                self.__dict__['DeepLabV3+_' + encoderName] = model
            else:
                model = self.__dict__['DeepLabV3+_' + encoderName]
        elif modelName == 'PSPNet':
            if self.__dict__['PSPNet_' + encoderName] is None:
                model = '777'
                self.__dict__['PSPNet_' + encoderName] = model
            else:
                model = self.__dict__['PSPNet_' + encoderName]
        elif modelName == 'UNet':
            if self.__dict__['UNet_' + encoderName] is None:
                model = '888'
                self.__dict__['UNet_' + encoderName] = model
            else:
                model = self.__dict__['UNet_' + encoderName]
        elif modelName == 'HRNetV2':
            if self.__dict__['HRNetV2_' + encoderName] is None:
                model = '999'
                self.__dict__['HRNetV2_' + encoderName] = model
            else:
                model = self.__dict__['HRNetV2_' + encoderName]

        return model

    def detect(self, modelName, encoderName, redPath, greenPath, bluePath, nirPath, rePath):
        model = self.generateModel(modelName, encoderName)
        print(modelName)
        print(encoderName)
        print(redPath)
        print(greenPath)
        print(bluePath)
        print(nirPath)
        print(rePath)
