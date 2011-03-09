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
so = file(basePtsFilename,'w')
subprocess.Popen("python %s %s" % (zoomViewBin, baseTextureFilename), shell=True, stdout=so).wait()
so.close()

basePtsXY = pylab.loadtxt(basePtsFilename)
basePtsUV = basePtsXY / (float(baseTexture.shape[1]), float(baseTexture.shape[0]))
basePtsUV[:,1] = 1. - basePtsUV[:,1]
basePtsXYZ = pylab.ones((basePtsUV.shape[0],4), dtype=pylab.float64)

for i in xrange(basePtsUV.shape[0]):
    positions = baseObj.get_positions(basePtsUV[i,0], basePtsUV[i,1])
    print positions
    basePtsXYZ[i,:3] = positions[0]

# find ref points in remap
remapPtsFilename = 'remapPts'
so = file(remapPtsFilename,'w')
subprocess.Popen("python %s %s" % (zoomViewBin, remapTextureFilename), shell=True, stdout=so).wait()
so.close()

remapPtsXY = pylab.loadtxt(remapPtsFilename)
remapPtsUV = remapPtsXY / (float(remapTexture.shape[1]), float(remapTexture.shape[0]))
remapPtsUV[:,1] = 1. - remapPtsUV[:,1]
remapPtsXYZ = pylab.ones((remapPtsUV.shape[0],4), dtype=pylab.float64)

for i in xrange(remapPtsUV.shape[0]):
    positions = remapObj.get_positions(remapPtsUV[i,0], remapPtsUV[i,1])
    print positions
    remapPtsXYZ[i,:3] = positions[0]

# calculate matrix
T = vector.calculate_rigid_transform(remapPtsXYZ, basePtsXYZ)

# apply matrix to points in remap
remapObj.vertices = vector.apply_matrix_to_points(pylab.matrix(T), remapObj.vertices)[:,:3]
remapObj.save('remapped.obj')