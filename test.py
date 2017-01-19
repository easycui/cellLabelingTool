import numpy as np
from segment import *
from PyQt4 import QtCore,QtGui
from util import *
pos=QtCore.QPoint()

pos.setX(756)
pos.setY(572)

img=cv2.imread("./a.jpg")
cv2.imshow("fdsa",img)

stainType = stainDetection(img)
h=deconvolution(img,stainType)
cv2.imshow("h",h)
cv2.imwrite('d.jpg',h)

cv2.waitKey(0)
#clahe=cv2.createCLAHE(clipLimit=2.0,tileGridSize=(8,8))
#cl1=clahe.apply(h)
#cv2.imshow("cl1",cl1)
#result=segment(img, cl1, 3, 0.2)
#cv2.imshow("result",result)
#segmentOneCell(img,h,50,5,pos)