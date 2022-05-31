import os

import matplotlib.pyplot as plt
import numpy as np

from nets import get_model_from_name
from utils.utils import (cvtColor, get_classes, letterbox_image,
                         preprocess_input, show_config)


#--------------------------------------------#
#   使用自己训练好的模型预测需要修改4个参数
#   model_path和classes_path、backbone
#   和alpha都需要修改！
#--------------------------------------------#
class Classification(object):
    _defaults = {
        #--------------------------------------------------------------------------#
        #   使用自己训练好的模型进行预测一定要修改model_path和classes_path！
        #   model_path指向logs文件夹下的权值文件，classes_path指向model_data下的txt
        #   如果出现shape不匹配，同时要注意训练时的model_path和classes_path参数的修改
        #--------------------------------------------------------------------------#
        "model_path"    : 'logs/ep160-loss0.359-val_loss0.396.h5',
        "classes_path"  : 'model_data/cls_classes.txt',
        #--------------------------------------------------------------------#
        #   输入的图片大小
        #--------------------------------------------------------------------#
        "input_shape"   : [250, 250],
        #--------------------------------------------------------------------#
        #   所用模型种类：
        #   mobilenet、resnet50、vgg16、vit
        #--------------------------------------------------------------------#
        "backbone"      : 'vgg16',
        #--------------------------------------------------------------------#
        #   当使用mobilenet的alpha值
        #   仅在backbone='mobilenet'的时候有效
        #--------------------------------------------------------------------#
        # "alpha"         : 0.25,
        #--------------------------------------------------------------------#
        #   该变量用于控制是否使用letterbox_image对输入图像进行不失真的resize
        #   否则对图像进行CenterCrop
        #--------------------------------------------------------------------#
        "letterbox_image"   : False,
        "cuda"     : True
    }

    @classmethod
    def get_defaults(cls, n):
        if n in cls._defaults:
            return cls._defaults[n]
        else:
            return "Unrecognized attribute name '" + n + "'"

    #---------------------------------------------------#
    #   初始化classification
    #---------------------------------------------------#
    def __init__(self, **kwargs):
        self.__dict__.update(self._defaults)
        for name, value in kwargs.items():
            setattr(self, name, value)

        #---------------------------------------------------#
        #   获得种类
        #---------------------------------------------------#
        self.class_names, self.num_classes = get_classes(self.classes_path)
        self.generate()
        
        show_config(**self._defaults)

    #---------------------------------------------------#
    #   载入模型
    #---------------------------------------------------#
    def generate(self):
        model_path = os.path.expanduser(self.model_path)
        assert model_path.endswith('.h5'), 'Keras model or weights must be a .h5 file.'
        
        #---------------------------------------------------#
        #   载入模型与权值
        #---------------------------------------------------#
        if self.backbone == "mobilenet":
            self.model = get_model_from_name[self.backbone](input_shape = [self.input_shape[0], self.input_shape[1], 3], classes = self.num_classes, alpha = self.alpha)
        else:
            self.model = get_model_from_name[self.backbone](input_shape = [self.input_shape[0], self.input_shape[1], 3], classes = self.num_classes)
        self.model.load_weights(self.model_path)
        print('{} model, and classes loaded.'.format(model_path))

    #---------------------------------------------------#
    #   检测图片
    #---------------------------------------------------#
    def detect_image(self, image):
        #---------------------------------------------------------#
        #   在这里将图像转换成RGB图像，防止灰度图在预测时报错。
        #   代码仅仅支持RGB图像的预测，所有其它类型的图像都会转化成RGB
        #---------------------------------------------------------#
        image       = cvtColor(image)
        #---------------------------------------------------#
        #   对图片进行不失真的resize
        #---------------------------------------------------#
        image_data  = letterbox_image(image, [self.input_shape[1], self.input_shape[0]], self.letterbox_image)
        #---------------------------------------------------------#
        #   归一化+添加上batch_size维度
        #---------------------------------------------------------#
        image_data  = np.expand_dims(preprocess_input(np.array(image_data, np.float32)), 0)
        
        #---------------------------------------------------#
        #   图片传入网络进行预测
        #---------------------------------------------------#
        preds       = self.model.predict(image_data)[0]
        #---------------------------------------------------#
        #   获得所属种类
        #---------------------------------------------------#
        class_name  = self.class_names[np.argmax(preds)]
        probability = np.max(preds)

        #---------------------------------------------------#
        #   绘图并写字
        #---------------------------------------------------#
        plt.subplot(1, 1, 1)
        plt.imshow(np.array(image))
        plt.title('Class:%s Probability:%.3f' %(class_name, probability))
        plt.show()
        return class_name