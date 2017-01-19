__author__ = 'easycui'
import cv2
#from skimage.exposure import rescale_intensity
from color import *
from PyQt4.QtCore import QPoint
from lset import *
import morphsnakes
from scipy.misc import imread
from matplotlib import pyplot as ppl


def segment(orig, img, kernel_size, distance_threshold):
    """

    :param img:  one component of the img, it should be a np.array with size (height,width), the value should be
                unit8(0-255)
    :param kernel_size:
    :param distance_threshold:
    :return:
    """

    ret,h= cv2.threshold(img,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    h = np.uint8(h)
    print(h)
    #cv2.imshow('result of segmentation using otsu_threhold',h)
    kernel = np.ones((kernel_size,kernel_size),np.uint8)

    h = cv2.morphologyEx(h,cv2.MORPH_CLOSE,kernel)
    #cv2.imshow('open operation result',h)

    """get background"""
    sure_bg =  cv2.dilate(h,kernel,iterations=1)
    # imshow('dilation result(sure back ground)',sure_bg)

    """get foreground"""
    dist_transform = cv2.distanceTransform(h, cv2.DIST_L2,0)
    # imshow('result of distance transform',dist_transform)

    ret, sure_fg = cv2.threshold(dist_transform,distance_threshold*dist_transform.max(),255, cv2.THRESH_BINARY)
    sure_fg = np.uint8(sure_fg)
    # imshow('result of sure foreground',sure_fg)
    unknown = cv2.subtract(sure_bg,sure_fg)
    # imshow('the difference between background and foreground',unknown)

    """get_markerrs using connected components"""
    ret, markers = cv2.connectedComponents(sure_fg)
    markers = markers+1 # each connected component has a distinct positive value, such as 1,2,3,4

    """let the possible edge be 0"""
    markers[unknown>0] = 0


    """use watershed algorithm to get edges"""
    result=np.copy(orig)
    markers =  cv2.watershed(result,markers)

    result[markers == -1] = [255,0,0]# make the edge be red
    return result


def segmentOneCell(orig, img, patchSize, kernelSize,centralPoint):
    """

    :param orig:
    :param img:
    :param patchSize:
    :param kernelSize:
    :param centralPoint:  centralPoint
    :return:
    """
    newimg = img[centralPoint.y()+6-patchSize/2:centralPoint.y()+6+patchSize/2,
             centralPoint.x()+6-patchSize/2:centralPoint.x()+6+patchSize/2]

    print centralPoint.y(),centralPoint.x()
    cv2.imshow("patch",newimg)

    #levelset(newimg)
    cimg=np.zeros(newimg.shape,np.uint8)

    #clahe=cv2.createCLAHE(clipLimit=2.0,tileGridSize=(8,8))
    #cl1=clahe.apply(newimg)
    #cv2.imshow("result",cl1)
    #levelset(cl1)

    ret,h= cv2.threshold(newimg,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    h = np.uint8(h)
    cv2.imshow('result of segmentation using otsu_threhold',h)
    kernel = np.ones((3,3),np.uint8)

    h = cv2.morphologyEx(h,cv2.MORPH_CLOSE,kernel)

    gI = morphsnakes.gborders(h, alpha=1000, sigma=2)

    # Morphological GAC. Initialization of the level-set.
    mgac = morphsnakes.MorphGAC(gI, smoothing=2, threshold=0.8, balloon=-3)
    mgac.levelset = circle_levelset(h.shape, (25, 25), 20)

    # Visual evolution.
    ppl.figure()
    morphsnakes.evolve_visual(mgac, num_iters=145, background=h)



    print(h)
    cv2.imshow('after closing',h)
    #levelset(h)
    #contour,a,hierarchy=cv2.findContours(h,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    #cv2.imshow("contour",contour)
    #print "contour:",a
    #cnt=a[0]
    #print cnt
    # circles=cv2.HoughCircles(h,cv2.HOUGH_GRADIENT,1, 10, np.array([]), 100, 30, 1, 50)
    # print circles
    # a, b, c = circles.shape
    # for i in range(b):
    #     cv2.circle(cimg, (circles[0][i][0], circles[0][i][1]), circles[0][i][2], (0, 0, 255), 3, cv2.LINE_AA)
    #     cv2.circle(cimg, (circles[0][i][0], circles[0][i][1]), 2, (0, 255, 0), 3, cv2.LINE_AA) # draw center of circle

    #cv2.HoughCircles("circle",cimg)
    kernel = np.ones((kernelSize,kernelSize),np.uint8)

    h = cv2.morphologyEx(h,cv2.MORPH_OPEN,kernel)
    cv2.imshow('open operation result',h)

    cv2.waitKey(0)

def fillACircle(img):
    center=img.shape[0]/2

def circle_levelset(shape, center, sqradius, scalerow=1.0):
    """Build a binary function with a circle as the 0.5-levelset."""
    grid = np.mgrid[map(slice, shape)].T - center
    phi = sqradius - np.sqrt(np.sum((grid.T)**2, 0))
    u = np.float_(phi > 0)
    return u

