#!/usr/bin/env python

# make this my cfg file
from bjg.cfgBase import *
assign_cfg_module(__name__)

import numpy

# -- General analysis variables --
bregmaNormalMaxDistance = 1.0
# tcRegPts = numpy.array([[4.,2.31,0.,1.],[0.,-4.62,0.,1.],[-4.,2.31,0.,1.]])
# tcRegPts = numpy.array([[4.,-5.33,7.,1.],[0.,-12.26,-7.,1.],[-4.,-5.33,7.,1.]])
tcRegPts = numpy.array([[4.,15.23,4.5,1.],[0.,22.16,4.5,1.],[-4.,15.23,4.5,1.]])


# -- System specific variables --
scanRepo = '/Users/graham/Repositories/coxlab/structured_light_stereotaxy/scans/SurgeryScans'
outputDir = '/Users/graham/Repositories/coxlab/structured_light_stereotaxy/software/scan_analysis_pipeline/data'


# -- Locations of other scripts --
zoomViewBin = '/Users/graham/Projects/glZoomView/zoomView.py'


# -- Scan/Animal specific options --
animal = 'H8'
skullScan = 'skull'
hatScan = 'tc'
finalScan = 'final'
refObjLocation = 'ref_cropped.obj'
refTextureLocation = 'ref_cropped.png'
skullObjLocation = 'skull_cropped.obj'
skullTextureLocation = 'skull_cropped.png'

# animal = 'K3'
# skullScan = 'Scan01'
# hatScan = 'Scan04'
# finalScan = 'Scan05'
# refObjLocation = 'ref_cropped.obj'
# refTextureLocation = 'ref_cropped.png'
# skullObjLocation = 'skull_cropped.obj'
# skullTextureLocation = 'skull_cropped.png'

# animal = 'H10'
# skullScan = 'Scan03'
# hatScan = 'Scan06'
# refObjLocation = 'ref_cropped.obj'
# refTextureLocation = 'ref_cropped.png'
# skullObjLocation = 'skull_cropped.obj'
# skullTextureLocation = 'skull_cropped.png'

# animal = 'H3'
# skullScan = 'Scan02'
# hatScan = 'Scan03'
# finalScan = 'Scan04'
# refObjLocation = 'ref_cropped.obj'
# refTextureLocation = 'ref_cropped.png'
# skullObjLocation = 'skull_cropped.obj'
# skullTextureLocation = 'skull_cropped.png'

# animal = 'H4'
# skullScan = 'Scan01'
# hatScan = 'Scan02'
# finalScan = 'Scan03'
# refObjLocation = 'ref_cropped.obj'
# refTextureLocation = 'ref_cropped.png'
# skullObjLocation = 'skull_cropped.obj'
# skullTextureLocation = 'skull_cropped.png'

# -- Analysis options --