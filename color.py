__author__ = 'easycui'
import numpy as np
rgb_from_hed = np.array([[0.65, 0.70, 0.29],
                         [0.07, 0.99, 0.11],
                         [0.27, 0.57, 0.78]])

hed_from_rgb = np.linalg.inv(rgb_from_hed)

bgra_dtype = np.dtype({'b': (np.uint8, 0),
                          'g': (np.uint8, 1),
                          'r': (np.uint8, 2),
                          'a': (np.uint8, 3)})

def rgb2hed(rgb):
    I = np.zeros(rgb.shape,dtype=np.float64)
    I = rgb/255.0
    I += 2
    I=-np.log(I)
    stains = np.dot(np.reshape(I, (-1, 3)), hed_from_rgb)
    return np.reshape(stains, I.shape)
def rescale_intensity(data,out_range=(0,1)):
    newData=np.zeros(data.shape)
    maxV=np.amax(data)
    minV=np.amin(data)
    rangeData=maxV-minV
    base=out_range[0]
    scale=rangeData/(out_range[1]-out_range[0])
    
    for i in range(newData.shape[0]):
        for j in range(newData.shape[1]):
            newData[i,j]=(data[i,j]-minV)/scale+base

    return newData
    
