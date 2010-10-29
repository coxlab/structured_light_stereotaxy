#!/usr/bin/env python
"""
Procedure:
    Open mesh file
    Generate random transformation (combined translation and rotation or just one)
    Generate transformed mesh
    
    Calculate transformation matrix given original and transformed mesh
    
    Check calculated with generated transformation matrix
    
    Plot error etc...
"""

import sys

import numpy
from pylab import *

# image processing
from scipy import ndimage
import mahotas
import pymorph
import cv

from skull_library import obj

objFilename = 'skull.obj'
textureFilename = 'texture.jpg'

#o = obj.OBJ(objFilename, textureFilename)

def rgb_to_hsv_arr(arr):
    """ fast rgb_to_hsv using numpy array """
    
    # adapted from Arnar Flatberg
    # http://www.mail-archive.com/numpy-discussion@scipy.org/msg06147.html
    # it now handles NaN properly and mimics colorsys.rgb_to_hsv output
    
    arr = arr/255.
    out = numpy.empty_like(arr)
    
    arr_max = arr.max(-1)
    delta = arr.ptp(-1)
    s = delta / arr_max
    
    s[delta==0] = 0
    
    # red is max
    idx = (arr[:,:,0] == arr_max)
    out[idx, 0] = (arr[idx, 1] - arr[idx, 2]) / delta[idx]
    
    # green is max
    idx = (arr[:,:,1] == arr_max)
    out[idx, 0] = 2. + (arr[idx, 2] - arr[idx, 0] ) / delta[idx]
    
    # blue is max
    idx = (arr[:,:,2] == arr_max)
    out[idx, 0] = 4. + (arr[idx, 0] - arr[idx, 1] ) / delta[idx]
    
    out[:,:,0] = (out[:,:,0]/6.0) % 1.0
    out[:,:,1] = s
    out[:,:,2] = arr_max
    
    # rescale back to [0, 255]
    out *= 255.
    
    # remove NaN
    out[numpy.isnan(out)] = 0
    
    return out

def find_skull(textureFilename):
    """
    Tries to find the skull within a scan texture image by:
        -color segmentation (red)
        -labeling all red regions
        -making bounding box around largest red region
    return:
        xmin, xmax, ymin, ymax : coordinates of bounding box
    """
    im = imread(textureFilename)
    
    # split up and filter image
    s = im.shape[0] / 100.0
    fr = ndimage.gaussian_filter(im[:,:,0], s).astype(float)
    fg = ndimage.gaussian_filter(im[:,:,1], s).astype(float)
    fb = ndimage.gaussian_filter(im[:,:,2], s).astype(float)
    
    # find the red parts
    #T = 200
    dT = 30
    bi = ((fr-fg) > dT) & ((fr-fb) > dT)
    
    # label all connected areas
    labeled, nObjects = ndimage.label(bi)
    
    # get largest area (other than background)
    objIndex = bincount(labeled.flatten())[1:].argmax() + 1
    
    # get points that only correspond to this object
    sbi = labeled == objIndex
    
    # get bounding box
    ymin = where(sbi)[0].min()
    ymax = where(sbi)[0].max()
    xmin = where(sbi)[1].min()
    xmax = where(sbi)[1].max()
    
    return xmin, xmax, ymin, ymax


def find_bregma(objFilename, textureFilename, mesh=None):
    
    if mesh == None:
        mesh = obj.OBJ(objFilename, textureFilename)
    pass

if __name__ == '__main__':
    # # ======== test find_skull ============
    # if len(sys.argv) != 2:
    #     print "must supply texture file"
    # xmin, xmax, ymin, ymax = find_skull(sys.argv[1])
    # figure(1)
    # imshow(imread(sys.argv[1])[ymin:ymax,xmin:xmax])
    # show()
    
    pass
    