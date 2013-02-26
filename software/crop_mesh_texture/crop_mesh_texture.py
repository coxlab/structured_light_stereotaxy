#!/usr/bin/env python

import os
import sys

from pylab import *
import PIL.Image as Image
# from scipy.misc import imsave

from bjg.obj import OBJ

o = OBJ()

objFilename = '/Users/graham/Desktop/mesh_fill/cropped.obj'  # 'scans/K3/Scan05/skull.obj'
textureFilename = '/Users/graham/Desktop/mesh_fill/cropped.png'  # 'scans/K3/Scan05/skull.png'

if len(sys.argv) == 3:
    objFilename = sys.argv[1]
    textureFilename = sys.argv[2]

o.load(objFilename, textureFilename)

# im = imread(o.textureFilename)
im = Image.open(o.textureFilename)

# h, w, d = im.shape
w, h = im.size

uvs = o.texCoords

xys = transpose(vstack((uvs[:, 0] * w, h - uvs[:, 1] * h)))

# figure out x,y bounds (look for edges of pixels)
# give myself a N=2 pixel border
# crop the texture
# xm, ym = (xys.min(0) - 2) #.astype(int)
# xM, yM = (xys.max(0) + 2) #.astype(int)
# cim = im.crop((int(round(xm)),int(round(ym)),int(round(xM)),int(round(yM))))

xm, ym = (xys.min(0) - 2).astype(int)
xM, yM = (xys.max(0) + 2).astype(int)
cim = im.crop((xm, ym, xM, yM))

# scale the uvs
# ch, cw, cd = cim.shape
cw, ch = cim.size
# um, vm = float(xm) / w, float(ym) / h
# uM, vM = float(xM) / w, float(yM) / h
# nuvs = transpose(vstack(((uvs[:,0]-um)/(uM-um),(uvs[:,1]-vm)/(vM-vm))))
nuvs = transpose(vstack(((xys[:, 0] - xm) / cw, 1 - (xys[:, 1] - ym) / ch)))


# save changes
newObjFilename = os.path.splitext(
    objFilename)[0] + '_cropped' + os.path.splitext(objFilename)[1]
newTextureFilename = os.path.splitext(
    textureFilename)[0] + '_cropped' + os.path.splitext(textureFilename)[1]

# imsave(newTextureFilename, cim)
cim.save(newTextureFilename)
o.texCoords = nuvs
o.save(newObjFilename)
