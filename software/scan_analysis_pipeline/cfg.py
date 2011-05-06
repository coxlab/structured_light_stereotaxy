#!/usr/bin/env python

# make this my cfg file
#from bjg.cfgBase import *
from utilities.cfgBase import *
assign_cfg_module(__name__)

import numpy

# name prefixes of meshes within a scan
refName = "skull" #"ref" # HACK until refs are here
skullName = "skull"

scanDir = '/Users/graham/Repositories/coxlab/structured_light_stereotaxy/scans/SurgeryScans'
outputDir = '/Users/graham/Repositories/coxlab/structured_light_stereotaxy/software/scan_analysis_pipeline/data'
# outputDir = '/Users/graham/Desktop/3d_pipeline_fixing/analysis/data'

skullRefsXYName = 'skullRefsXY'
#skullRefsXYZName = 'skullRefsXYZ'

hatRefsXYName = 'hatRefsXY'
#hatRefsXYZName = 'hatRefsXYZ'

# -- General analysis variables --
bregmaNormalMaxDistance = 1.0
# tcRegPts = numpy.array([[4.,2.31,0.,1.],[0.,-4.62,0.,1.],[-4.,2.31,0.,1.]])
# tcRegPts = numpy.array([[4.,-5.33,7.,1.],[0.,-12.26,-7.,1.],[-4.,-5.33,7.,1.]])
tcRefPts = numpy.array([[4.,15.23,4.5,1.],[0.,22.16,4.5,1.],[-4.,15.23,4.5,1.]])

freshAnalysis = False # if true, pipeline will run in full and not use existing results

zoomViewBin = '/Users/graham/Projects/glZoomView/zoomView.py'
meshlabBin = '/Applications/meshlab.app/Contents/MacOS/meshlabserver'
meshlabScript = '/Users/graham/Repositories/coxlab/structured_light_stereotaxy/software/scan_analysis_pipeline/simplify.mlx'

defaultAnimalCfg = '/Users/graham/Repositories/coxlab/structured_light_stereotaxy/software/scan_analysis_pipeline/animalCfg.py'

attrFuncMap = { 'skullObj'             : 'load_skull_obj',
                'hatObj'               : 'load_hat_obj',
                'finalObj'             : 'load_final_obj',
                'bregmaXYZ'            : 'find_skull_refs',
                'lambdaXYZ'            : 'find_skull_refs',
                'bregmaNormal'         : 'find_skull_refs',
                'bregmaToLambdaVector' : 'find_skull_refs',
                'tcRefsXYZ'            : 'find_hat_refs',
                'scanToSkull'          : 'calculate_scan_to_skull_matrix',
                'skullToHat'           : 'calculate_skull_to_hat_matrix',
                'scanToHat'            : 'calculate_scan_to_hat_matrix',
                }

# # -- System specific variables --
# scanRepo = '/Users/graham/Repositories/coxlab/structured_light_stereotaxy/scans/SurgeryScans'
# outputDir = '/Users/graham/Repositories/coxlab/structured_light_stereotaxy/software/scan_analysis_pipeline/data'


# -- Locations of other scripts --

animal = 'K4'
skullScan = 'Scan03'
hatScan = 'Scan04'
finalScan = 'Scan06'

# -- for old pipeline --
scanRepo = scanDir
tcRegPts = tcRefPts
refObjLocation = 'ref.obj'
refTextureLocation = 'ref.png'
skullObjLocation = 'skull.obj'
skullTextureLocation = 'skull.png'

# # -- Scan/Animal specific options --
# animal = 'H8'
# skullScan = 'skull'
# hatScan = 'tc'
# finalScan = 'final'
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

# animal = 'H7'
# skullScan = 'Scan01'
# hatScan = 'Scan02'
# finalScan = 'Scan03'
# refObjLocation = 'ref_cropped.obj'
# refTextureLocation = 'ref_cropped.png'
# skullObjLocation = 'skull_cropped.obj'
# skullTextureLocation = 'skull_cropped.png'

# animal = 'Acrylic'
# skullScan = 'Scan01'
# hatScan = 'Scan02'
# finalScan = 'Scan02'
# refObjLocation = 'ref_cropped.obj'
# refTextureLocation = 'ref_cropped.png'
# skullObjLocation = 'skull_cropped.obj'
# skullTextureLocation = 'skull_cropped.png'

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

# animal = 'H4'
# skullScan = 'Scan01'
# hatScan = 'Scan02'
# finalScan = 'Scan03'
# refObjLocation = 'ref_cropped.obj'
# refTextureLocation = 'ref_cropped.png'
# skullObjLocation = 'skull_cropped.obj'
# skullTextureLocation = 'skull_cropped.png'

# -- Analysis options --
