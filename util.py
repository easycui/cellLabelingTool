__author__ = 'easycui'
import numpy as np
from PyQt4.QtGui import QImage, QColor
from segment import *
def deconvolution(img,stain_type="HE"):
    I = np.zeros(img.shape,dtype=np.uint8)
    #bgr to rgb(opencv imread is bgr)
    I[:,:,0]=img[:,:,2]
    I[:,:,1]=img[:,:,1]
    I[:,:,2]=img[:,:,0]
    if stain_type=="HE":
        hed=rgb2hed(I)
        h=rescale_intensity(hed[:,:,0],out_range=(0,1))
        h=np.uint8(h*255)
    #h=I[:,:,2]
    return h


def qimage2np(qimage, dtype = 'array'):
    """Convert QImage to np.ndarray.  The dtype defaults to uint8
    for QImage.Format_Indexed8 or `bgra_dtype` (i.e. a record array)
    for 32bit color images.  You can pass a different dtype to use, or
    'array' to get a 3D uint8 array for color images."""
    result_shape = (qimage.height(), qimage.width())
    temp_shape = (qimage.height(),
                  qimage.bytesPerLine() * 8 / qimage.depth())
    if qimage.format() in (QImage.Format_ARGB32_Premultiplied,
                           QImage.Format_ARGB32,
                           QImage.Format_RGB32):
        if dtype == 'rec':
            dtype = bgra_dtype
        elif dtype == 'array':
            dtype = np.uint8
            result_shape += (4, )
            temp_shape += (4, )
    elif qimage.format() == QImage.Format_Indexed8:
        dtype = np.uint8
    else:
        raise ValueError("qimage2np only supports 32bit and 8bit images")
    # FIXME: raise error if alignment does not match
    buf = qimage.bits().asstring(qimage.numBytes())
    result = np.frombuffer(buf, dtype).reshape(temp_shape)
    if result_shape != temp_shape:
        result = result[:,:result_shape[1]]
    if qimage.format() == QImage.Format_RGB32 and dtype == np.uint8:
        result = result[...,:3]
    return result

def np2qimage(array):
    if len(array.shape) != 3:
        raise ValueError("rgb2QImage can only convert 3D arrays")
    if array.shape[2] not in (3, 4):
        raise ValueError("rgb2QImage can expects the last dimension to contain exactly three (R,G,B) or four (R,G,B,A) channels")

    h, w, channels = array.shape

    # Qt expects 32bit BGRA data for color images:
    bgra = np.empty((h, w, 4), np.uint8, 'C')
    bgra[...,0] = array[...,2]
    bgra[...,1] = array[...,1]
    bgra[...,2] = array[...,0]
    if array.shape[2] == 3:
        bgra[...,3].fill(255)
        fmt = QImage.Format_RGB32
    else:
        bgra[...,3] = array[...,3]
        fmt = QImage.Format_ARGB32

    result = QImage(bgra.data, w, h, fmt)
    result.ndarray = bgra
    return result
def pixmap2array(pixmap):
    image=pixmap.toImage()
    I=qimage2np(image)
    img = np.zeros(I.shape,dtype=np.uint8)
    img[:,:,0]= I[:,:,0]
    img[:,:,1]=I[:,:,1]
    img[:,:,2]=I[:,:,2]
    return img
def seg(img,Samples):
    stainType = stainDetection(img)
    h=deconvolution(img,stainType)
    result=segment(img, h, 3, 0.2)
    return result

def segOne(img,Samples):
    stainType = stainDetection(img)
    h=deconvolution(img,stainType)
    cv2.imshow("fdsa",h)
    for i in Samples:
        segmentOneCell(img,h,50,3,i.getPosition())

def stainDetection(img):
    return "HE"