#!/usr/bin/env python

import os
import sys
import time

from pylab import *
from scikits import delaunay
import PIL.Image as Image

from bjg.obj import OBJ

objFile = 'Scan02.obj'
imFile = 'Scan02.png'

if len(sys.argv) == 2:
    objFile = sys.argv[1]
    imFile = os.path.splitext(objFile)[0] + '.png'
if len(sys.argv) > 2:
    objFile = sys.argv[1]
    imFile = sys.argv[2]

# load obj
o = OBJ()
o.load(objFile, imFile)

# load texture image
im = Image.open(o.textureFilename)
w, h = im.size

# show image
# imshow(im, interpolation='nearest')

# show uv coordinates
uvs = o.texCoords
# xys = transpose(vstack((uvs[:,0]*w,h - uvs[:,1]*h)))
# scatter(xys[:,0],xys[:,1],c='k')

tri = delaunay.Triangulation(uvs[:, 0], uvs[:, 1])

# st = time.time()
o.faces = zeros((len(tri.triangle_nodes), 3, 3))
o.faces[:, 0, :] = tri.triangle_nodes
o.faces[:, 1, :] = tri.triangle_nodes
# print "N:", time.time() - st

# st = time.time()
# o.faces = []
# for n in tri.triangle_nodes:
#     face = list(array(n))
#     o.faces.append((face,[0,0,0],face))
# o.faces = array(o.faces)
# print "O:", time.time() - st

o.save('new.obj')
