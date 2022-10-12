#截取旋转的矩形图片

import cv2
from bs4 import BeautifulSoup
import numpy as np
from numpy import cos,sin
import os
from numpy import cos,sin,pi
from glob import glob

def read_voc_xml(p):
    ##读取voc xml 文件
    boxes = []
    if os.path.exists(p):
        with open(p) as f:
            xmlString = f.read()
        xmlString = BeautifulSoup(xmlString, 'lxml')  # 抓取xml数据
        objList = xmlString.findAll('object')
        for obj in objList:
            robndbox = obj.find('robndbox')
            bndbox = obj.find('bndbox')
            if robndbox is not None and bndbox is None:

                cx = np.float(robndbox.find('cx').text)  # 框中心点，图像列
                cy = np.float(robndbox.find('cy').text)  # 框中心点，图像行
                w = np.float(robndbox.find('w').text)
                h = np.float(robndbox.find('h').text)
                angle = robndbox.find('angle').text


            else:
                xmin = np.float(bndbox.find('xmin').text)
                xmax = np.float(bndbox.find('xmax').text)
                ymin = np.float(bndbox.find('ymin').text)
                ymax = np.float(bndbox.find('ymax').text)
                cx = (xmin + xmax) / 2.0
                cy = (ymin + ymax) / 2.0
                w = (-xmin + xmax)  # /2.0
                h = (-ymin + ymax)  # /2.0
                angle = 0.0
            boxes.append({'cx': cx, 'cy': cy, 'w': w, 'h': h, 'angle': angle})

    return boxes


def rotate(x,y,angle,cx,cy):
    angle = angle#*pi/180
    x_new = (x-cx)*cos(angle) - (y-cy)*sin(angle)+cx
    y_new = (x-cx)*sin(angle) + (y-cy)*cos(angle)+cy
    return x_new,y_new

def xy_rotate_box(cx, cy, w, h, angle):
    """
    绕 cx,cy点 w,h 旋转 angle 的坐标
    x_new = (x-cx)*cos(angle) - (y-cy)*sin(angle)+cx
    y_new = (x-cx)*sin(angle) + (y-cy)*sin(angle)+cy
    """

    cx = float(cx)
    cy = float(cy)
    w = float(w)
    h = float(h)
    angle = float(angle)
    x1, y1 = rotate(cx - w / 2, cy - h / 2, angle, cx, cy)
    x2, y2 = rotate(cx + w / 2, cy - h / 2, angle, cx, cy)
    x3, y3 = rotate(cx + w / 2, cy + h / 2, angle, cx, cy)
    x4, y4 = rotate(cx - w / 2, cy + h / 2, angle, cx, cy)
    return x1, y1, x2, y2, x3, y3, x4, y4


def box_rotate(box, angle=0, imgH=0, imgW=0):
    """
    对坐标进行旋转 逆时针方向 0\90\180\270,
    """
    x1, y1, x2, y2, x3, y3, x4, y4 = box[:8]
    if angle == 90:
        x1_, y1_ = y2, imgW - x2
        x2_, y2_ = y3, imgW - x3
        x3_, y3_ = y4, imgW - x4
        x4_, y4_ = y1, imgW - x1

    elif angle == 180:
        x1_, y1_ = imgW - x3, imgH - y3
        x2_, y2_ = imgW - x4, imgH - y4
        x3_, y3_ = imgW - x1, imgH - y1
        x4_, y4_ = imgW - x2, imgH - y2

    elif angle == 270:
        x1_, y1_ = imgH - y4, x4
        x2_, y2_ = imgH - y1, x1
        x3_, y3_ = imgH - y2, x2
        x4_, y4_ = imgH - y3, x3
    else:
        x1_, y1_, x2_, y2_, x3_, y3_, x4_, y4_ = x1, y1, x2, y2, x3, y3, x4, y4

    return (x1_, y1_, x2_, y2_, x3_, y3_, x4_, y4_)


def get_rect_image(img,boxes):
    angle=0
    tmp = np.array(img)
    c=[0,0,255]

    for line in boxes:
        cx = line['cx']
        cy = line['cy']
        degree = line['angle']
        w = line['w']
        h = line['h']
        #获取左上 右上 右下 左下四个点
        x1, y1, x2, y2, x3, y3, x4, y4 = xy_rotate_box(cx, cy, w, h, degree)
        cx = np.mean([x1, x2, x3, x4])
        cy = np.mean([y1, y2, y3, y4])

        rect=cv2.retangle(tmp)
        cv2.line(tmp, (int(x1), int(y1)), (int(x2), int(y2)), c, 1)
        cv2.line(tmp, (int(x2), int(y2)), (int(x3), int(y3)), c, 1)
        cv2.line(tmp, (int(x3), int(y3)), (int(x4), int(y4)), c, 1)
        cv2.line(tmp, (int(x4), int(y4)), (int(x1), int(y1)), c, 1)

        cv2.imshow('img', tmp)
        cv2.waitKey(1)
        print(1)


def draw_single_image():
    img = cv2.imread('C:\\Users\\87797\\Desktop\\264.jpg')
    xmlP = 'C:\\Users\\87797\\Desktop\\264.xml'
    boxes = read_voc_xml(xmlP)
    get_rect_image(img, boxes)



def rorate_signle_image():
    img = cv2.imread('C:\\Users\\87797\\Desktop\\264.jpg')
    size=img.shape
    width=size[1]
    height=size[0]
    xmlP = 'C:\\Users\\87797\\Desktop\\264.xml'
    boxes = read_voc_xml(xmlP)
    angle=float(boxes[0]['angle'])*180/pi
    matRotate = cv2.getRotationMatrix2D((width * 0.5, height * 0.5), angle, 1)

    dst = cv2.warpAffine(img, matRotate, (width + 10, height + 10))

    cv2.imshow('image', dst)
    cv2.waitKey(1)

    print(1)

def rorate_multi_image():
    root = 'E:\\code\\yolo_crnn_ocr\\yolo_crnn_ocr\\Shebei_data\\third_mark_image\\text\\*.[j|p|J]*'
    jpgPath = glob(root)
    path_str='E:\\code\\yolo_crnn_ocr\\yolo_crnn_ocr\\Shebei_data\\third_mark_image\\ocr\\rorate_image\\'

    for p in jpgPath:

        xmlP = p.replace('.jpg', '.xml').replace('.png', '.xml')
        # 读取xml文件
        boxes = read_voc_xml(xmlP)
        img=cv2.imread(p)
        size = img.shape
        width = size[1]
        height = size[0]

        angle = float(boxes[0]['angle']) * 180 / pi
        matRotate = cv2.getRotationMatrix2D((width * 0.5, height * 0.5), 180+angle, 1)

        dst = cv2.warpAffine(img, matRotate, (width + 10, height + 10))
        img1=dst.copy()
        cv2.imshow('img',dst)
        cv2.waitKey(1)
        image_name = p.split('\\')[-1]
        cv2.imwrite(path_str+image_name,img1)


def rorate_90_image():
    root = 'E:\\code\\yolo_crnn_ocr\\yolo_crnn_ocr\\Shebei_data\\third_mark_image\\ocr\\rorate_image\\*.[j|p|J]*'
    jpgPath = glob(root)
    path_str = 'E:\\code\\yolo_crnn_ocr\\yolo_crnn_ocr\\Shebei_data\\third_mark_image\\ocr\\1\\'
    for p in jpgPath:
        img = cv2.imread(p)
        img90=np.rot90(img)

        img90 = np.rot90(img90)
        cv2.imshow('img', img90)
        cv2.waitKey(1)
        image_name=p.split('\\')[-1]
        cv2.imwrite(path_str+image_name,img90)











if __name__=='__main__':
    #draw_single_image()
    rorate_multi_image()
    #rorate_90_image()