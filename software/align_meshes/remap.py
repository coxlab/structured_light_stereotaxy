#!/usr/bin/env python
"""
"""

import os, shutil, subprocess, sys

import numpy
import pylab

import bjg.vector as vector
import bjg.obj as obj

# ====================================================================
# ========================  Setup ====================================
# ====================================================================


zoomViewBin = '/Users/graham/Projects/glZoomView/zoomView.py'

# enable logging
import logging
logging.basicConfig(level=logging.DEBUG)

if len(sys.argv) != 3:
    logging.error("requires two arguments: <base_mesh> <mesh_to_remap>")
    sys.exit(1)

baseMeshFilename = sys.argv[1]
remapMeshFilename = sys.argv[2]

# ====================================================================
# ======================  Analysis ===================================
# ====================================================================

baseObj = obj.OBJ()
baseObj.load(baseMeshFilename)
baseTextureFilename = os.path.splitext(baseMeshFilename)[0]+'.png'
baseTexture = pylab.imread(baseTextureFilename)

remapObj = obj.OBJ()
remapObj.load(remapMeshFilename)
remapTextureFilename = os.path.splitext(remapMeshFilename)[0]+'.png'
remapTexture = pylab.imread(remapTextureFilename)

# find ref points in base
basePtsFilename = 'basePts'
baseSO = file(basePtsFilename,'w')
baseSP = subprocess.Popen("python %s %s" % (zoomViewBin, baseTextureFilename), shell=True, stdout=baseSO)

# find ref points in remap
remapPtsFilename = 'remapPts'
remapSO = file(remapPtsFilename,'w')
subprocess.Popen("python %s %s" % (zoomViewBin, remapTextureFilename), shell=True, stdout=remapSO).wait()
baseSP.wait()
baseSO.close()
remapSO.close()

basePtsXY = pylab.loadtxt(basePtsFilename)
basePtsUV = basePtsXY / (float(baseTexture.shape[1]), float(baseTexture.shape[0]))
basePtsUV[:,1] = 1. - basePtsUV[:,1]
basePtsXYZ = pylab.ones((basePtsUV.shape[0],4), dtype=pylab.float64)

goodPts = pylab.ones(basePtsUV.shape[0])

for i in xrange(basePtsUV.shape[0]):
    positions = baseObj.get_positions(basePtsUV[i,0], basePtsUV[i,1])
    if len(positions) == 0:
        goodPts[i] = 0
        print "Point %i could not be located in the mesh" % i
        continue
    print positions[0], basePtsXYZ[i,:3]
    basePtsXYZ[i,:3] = positions[0]

remapPtsXY = pylab.loadtxt(remapPtsFilename)
remapPtsUV = remapPtsXY / (float(remapTexture.shape[1]), float(remapTexture.shape[0]))
remapPtsUV[:,1] = 1. - remapPtsUV[:,1]
remapPtsXYZ = pylab.ones((remapPtsUV.shape[0],4), dtype=pylab.float64)

for i in xrange(remapPtsUV.shape[0]):
    positions = remapObj.get_positions(remapPtsUV[i,0], remapPtsUV[i,1])
    if len(positions) == 0:
        goodPts[i] = 0
        print "Point %i could not be located in the mesh" % i
        continue
    print positions[0], remapPtsXYZ[i,:3]
    remapPtsXYZ[i,:3] = positions[0]

# get rid of the bad points
#remapPtsXYZ = pylab.choose(pylab.where(goodPts == 1)[0], remapPtsXYZ)
remapPtsXYZ = pylab.array([remapPtsXYZ[i] for i in pylab.where(goodPts == 1)])
#basePtsXYZ = pylab.choose(pylab.where(goodPts == 1)[0], basePtsXYZ)
basePtsXYZ = pylab.array([basePtsXYZ[i] for i in pylab.where(goodPts == 1)])
print "Good pts found: %i " % sum(goodPts)

# calculate matrix
#T = vector.calculate_rigid_transform(remapPtsXYZ, basePtsXYZ)
T = vector.fit_rigid_transform(remapPtsXYZ, basePtsXYZ)
pylab.savetxt('affineMatrix', T)
print "Transformation from 1 to 2:"
t, r = vector.decompose_matrix(T)
print " Translation: ", t
print " Rotation   : ", r


# apply matrix to points in remap
remapObj.vertices = vector.apply_matrix_to_points(pylab.matrix(T), remapObj.vertices)[:,:3]
remapObj.save('remapped.obj')