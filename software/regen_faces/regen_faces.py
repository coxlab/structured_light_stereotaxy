#!/usr/bin/env python

import sys

from pylab import *
from scikits import delaunay
import PIL.Image as Image

from bjg.obj import OBJ

objFile = 'Scan02.obj'
imFile = 'Scan02.png'

# load obj
o = OBJ()
o.load(objFile, imFile)

# load texture image
im = Image.open(o.textureFilename)
w, h = im.size

# show image
#imshow(im, interpolation='nearest')

# show uv coordinates
uvs = o.texCoords
#xys = transpose(vstack((uvs[:,0]*w,h - uvs[:,1]*h)))
#scatter(xys[:,0],xys[:,1],c='k')

tri = delaunay.Triangulation(uvs[:,0], uvs[:,1])

o.faces = []
for n in tri.triangle_nodes:
    face = list(array(n))
    o.faces.append((face,[0,0,0],face))
o.faces = array(o.faces)

o.save('new.obj')
