#!/usr/bin/env python

import sys

import numpy
import pylab as pl
from scipy.interpolate import griddata

filename = sys.argv[1]
vertices = numpy.fromregex(filename,
                           r"v\s+([\d,.,-]+)\s+([\d,.,-]+)\s+([\d,.,-]+)",
                          (numpy.float64, 3))
# self.normals = numpy.fromregex(filename,
#            r"vn\s+([\d,.,-]+)\s+([\d,.,-]+)\s+([\d,.,-]+)",
#            (numpy.float64, 3))
texCoords = numpy.fromregex(filename,
                            r"vt\s+([\d,.,-]+)\s+([\d,.,-]+)",
                           (numpy.float64, 2))

print len(texCoords), len(vertices)

w, h = (3872, 2592)
ui = numpy.linspace(0., 1., w)
vi = numpy.linspace(0., 1., h)

zi = griddata((texCoords[:, 0], texCoords[:, 1]), vertices[:, 2], (ui[None,
              :], vi[:, None]), method='cubic')

# pl.figure()
# pl.gcf().add_subplot(111, aspect='equal')
# pl.imshow(zi)
# pl.ylim([h,0])
pl.gray()
pl.imsave('heightmap.png', zi)
