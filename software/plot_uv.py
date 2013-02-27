#!/usr/bin/env python

from pylab import *

import PIL.Image as Image

from bjg.obj import OBJ

objFile = 'cropped.obj'
imFile = 'cropped.png'

# load obj
o = OBJ()
o.load(objFile, imFile)

# load texture image
im = Image.open(o.textureFilename)
w, h = im.size

# show image
imshow(im, interpolation='nearest')

# show uv coordinates
uvs = o.texCoords
xys = transpose(vstack((uvs[:, 0] * w, h - uvs[:, 1] * h)))
scatter(xys[:, 0], xys[:, 1], c='k')
mx = min(xys[:, 1])
rxy = xys[where(xys == mx)[0], :]
scatter(rxy[:, 0], rxy[:, 1], c='b')

show()
