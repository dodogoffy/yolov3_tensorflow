#!/usr/bin/env python3
#coding=utf-8

#============================#
#Program:parseJson.py
#       对BDD100K的json文件进行解析
#Date:19-11-6
#Author:liheng
#Version:V1.0
#============================#


import json
import os
from tqdm import tqdm
import cv2

def read_class_names(class_file_name):
    '''
    load classes's name from the given file
    :param class_file_name:
    :return:返回值类型：dict,ID--类别名称
    '''
    names = {}
    with open(class_file_name,'r') as data:
        for ID,name in enumerate(data):
            names[ID] = name.strip('\n')#去除每一行结尾的换行符

    return names


if __name__ == '__main__':
    imgRootPath = "/media/liheng/TOSHIBA EXT/DataSet/bdd100k/images/100k/val/"
    labelPath = "/media/liheng/TOSHIBA EXT/DataSet/bdd100k/labels/bdd100k_labels_images_val.json"
    yolo_format_saved_path = './val.txt' #导出文件保存路径
    needed_classes_file = '../data/classes/bdd100k.names'  # 需要的类别

    needed_classes = read_class_names(needed_classes_file)#需要的类别名称
    needed_classes = {value: key for key, value in needed_classes.items()}#key value 互换

    nWaitTime = 1
    with open(labelPath,'r') as labelFile, open(yolo_format_saved_path,'w') as yoloFile:
        lines = json.load(labelFile)
        labelFile.close()

        for line in tqdm(lines):
            name = line['name']
            labels = line['labels']
            imgPath = imgRootPath + name
            txtPath = imgPath.replace("jpg", "txt")
            if not os.path.isfile(imgPath):
                continue

            image = cv2.imread(imgPath, cv2.IMREAD_COLOR)
            H,W,C = image.shape
            category_label = ''
            for label in labels:  # 对所有label进行遍历
                category = label['category']  # 获取类别名称
                if category in needed_classes.keys():  # 该类在导出列表中
                    obj_roi = label['box2d']
                    xmin, ymin = obj_roi['x1'], obj_roi['y1']
                    xmax, ymax = obj_roi['x2'], obj_roi['y2']
                    xmax = min(xmax,W-1)
                    ymax = min(ymax,H-1)
                    cls_id = needed_classes[category]
                    w = xmax - xmin
                    h = ymax - ymin
                    #根据框的大小过滤一部分目标
                    if h<(10.0/416.0)*H:
                        continue
                    if w<(10.0/416.0)*W:
                        continue

                    _str = '{},{},{},{},{} '.format(xmin, ymin, xmax, ymax, cls_id)
                    category_label += _str

                    # =========画图显示===========#
                    cv2.rectangle(image, (int(xmin), int(ymin)), (int(xmax), int(ymax)), (0, 255, 0), 1,
                                  lineType=cv2.LINE_AA)

            if len(category_label.strip()):
                category_label = '{} {}\n'.format(imgPath, category_label)
                yoloFile.write(category_label)
                cv2.imshow('image', image)
                key = cv2.waitKey(nWaitTime)
                if 27 == key:  # ESC
                    break
                elif 32 == key:  # space
                    nWaitTime = not nWaitTime

        cv2.destroyAllWindows()



