#!/usr/bin/env python
"""
== Givens ==
    skull scan (Scan01)
        skull
        ref object
    hat scan (Scan02)
        skull
        ref object
    final scan (Scan03)
        skull
        ref object

== Need ==
    skull-to-tricorner transformation matrix
        x = ML, + = right
        y = AP, + = anterior
        z = DV, + = dorsal
        0,0,0 = bregma
    converted scans (in skull coordinates)
        skull, hat, and final scans

== Steps ==
    load skull scan
        load ref mesh, calculate scaling matrix
        load skull mesh, correct scaling matrix
    load hat scan
        load ref mesh, calculate scaling matrix
        load skull mesh, correct scaling matrix
    align skull and hat scans
        using 3 identical points on the posterior coronal skull suture
    identify skull landmarks in skull scan
        find bregma, and normal at bregma
        find lambda
        find vector between
    calculate scan-to-skull transformation matrix
    convert skull and hat scans to skull coordinates and save scans
    find tricorner reference points in hat scan
    calculate skull-to-tricorner transformation matrix
    load and fix final scan
        load ref mesh, calculate scaling matrix
        load skull mesh, correct scaling matrix
        find tricorner ref points
        align this and the hat scan using ref points
        convert skull mesh to skull coordinates (using scan-to-skull matrix)
        save scan in skull coordinates
"""

import os, shutil, subprocess

import numpy
import pylab

import utilities.vector as vector
import utilities.obj as obj

# ====================================================================
# ========================  Setup ====================================
# ====================================================================


# enable logging
import logging
logging.basicConfig(level=logging.DEBUG)


# import configuration file containing analysis settings
import cfg


# process command line options
#cfg.process_command_line()
logging.debug('Processing scan for animal: %s' % cfg.animal)


# look for an animal specific configuration file
animalCfg = '%s/%s/animalCfg.py' % (cfg.outputDir, cfg.animal)
if os.path.isfile(animalCfg):
    logging.debug('Found animal specific configuration file')
    cfg.load_external_cfg(animalCfg)


# find the input directory (where the scans live)
inDir = '%s/%s' % (cfg.scanRepo, cfg.animal)
logging.debug('Input Directory: %s' % inDir)
if not os.path.exists(inDir):
    raise IOError('Could not find input directory:%s' % inDir)


# find all scans for this animal
scanDirs = os.listdir(inDir)
scanDirs = [s for s in scanDirs]# if s.find('Scan') != -1]
if len(scanDirs) < 2:
    raise IOError('There must be at least 2 scans, only %i found' % len(scanDirs))
if not cfg.skullScan in scanDirs:
    raise IOError('Skull scan(%s) not found in scan directory' % cfg.skullScan)
if not cfg.hatScan in scanDirs:
    raise IOError('Hat scan(%s) not found in scan directory' % cfg.hatScan)


# setup output directory
outDir = '%s/%s' % (cfg.outputDir, cfg.animal)
if not os.path.exists(outDir):
    os.makedirs(outDir)
logging.debug('Output Directory: %s' % outDir)


# ====================================================================
# ======================  Functions ==================================
# ====================================================================

def get_scaling_matrix_from_ref(refObj):
    pass

def load_and_fix_scan(scanDir):
    # # find location of texture
    # textureFilename = '%s/%s' % (scanDir, cfg.textureLocation)
    # if not os.path.isfile(textureFilename):
    #     raise IOError('Texture(%s) is not a file' % textureFilename)
    # texture = pylab.imread(textureFilename)
    # 
    # # find and load ref obj
    # refObjFilename = '%s/%s' % (scanDir, cfg.refObjLocation)
    # if not os.path.isfile(refObjFilename):
    #     raise IOError('Ref Obj(%s) is not a file' % refObjFilename)
    # refObj = obj.OBJ()
    # refObj.load(refObjFilename, textureFilename)
    # 
    # # calculate scaling matrix from reference object
    # sM = get_scaling_matrix_from_ref(refObj) #TODO
    # 
    # # load skull obj
    # skullObjFilename = '%s/%s' % (scanDir, cfg.skullObjLocation)
    # if not os.path.isfile(skullObjFilename):
    #     raise IOError('Skull Obj(%s) is not a file' % skullObjFilename)
    # skullObj = obj.OBJ()
    # skullObj.load(skullObjFilename, textureFilename)
    # 
    # # scale skull obj
    # skullObj.apply_matrix(sM) #TODO
    skullObj = obj.OBJ()
    skullObj.load('%s/%s' % (scanDir, cfg.skullObjLocation))
    skullTexture = pylab.imread('%s/%s' % (scanDir, cfg.skullTextureLocation))
    return skullObj, skullTexture

def find_skull_landmarks(skullObj, skullTexture, scanDir):
    # find landmarks in images
    so = file(outDir+'/skullLandmarksXY','w')
    subprocess.Popen("python %s %s/%s" % (cfg.zoomViewBin, scanDir, cfg.skullTextureLocation), shell=True, stdout=so).wait()
    so.close()
    
    # convert XY to uv
    bregmaXY, lambdaXY = pylab.loadtxt(outDir+'/skullLandmarksXY')
    bregmaUV = bregmaXY[0]/skullTexture.shape[1], 1.-bregmaXY[1]/skullTexture.shape[0]
    lambdaUV = lambdaXY[0]/skullTexture.shape[1], 1.-lambdaXY[1]/skullTexture.shape[0]
    
    bregmaXYZ = skullObj.get_positions(*bregmaUV)[0]
    lambdaXYZ = skullObj.get_positions(*lambdaUV)[0]
    
    bregmaNormal = skullObj.get_average_normal(bregmaXYZ, cfg.bregmaNormalMaxDistance)
    print bregmaNormal
    bregmaToLambdaVector = pylab.array(lambdaXYZ) - pylab.array(bregmaXYZ)
    bregmaToLambdaVector = bregmaToLambdaVector/pylab.norm(bregmaToLambdaVector)
    return bregmaXYZ, bregmaNormal, bregmaToLambdaVector

def calculate_scan_to_skull_matrix(bLoc, bNorm, bToLVec):
    a1 = numpy.cross(-numpy.array(bToLVec), bNorm)
    #a2 = numpy.cross(bNorm, a1)
    a2 = -numpy.array(bToLVec)
    #a3 = bNorm
    a3 = numpy.cross(a1,-numpy.array(bToLVec))
    #R = vector.rebase(numpy.cross(-numpy.array(bToLVec), bNorm), -numpy.array(bToLVec), bNorm)
    R = vector.rebase(a1, a2, a3)
    T = vector.translation_to_matrix(-bLoc[0],-bLoc[1],-bLoc[2])
    return vector.translate_and_rotate(T,R)

def align_objs_with_skull(fromObj, toObj, fromTexture=None, toTexture=None):
    pass

def find_hat_refs(hatObj, hatTexture, scanDir):
    so = file(outDir+'/tcRefsXY', 'w')
    subprocess.Popen("python %s %s/%s" % (cfg.zoomViewBin, scanDir, cfg.skullTextureLocation), shell=True, stdout=so).wait()
    so.close()
    
    # convert XY to uv
    tcRefsXY = pylab.loadtxt(outDir+'/tcRefsXY')
    #tcRefsUV = pylab.zeros(tcRefsXY.shape, tcRefsXY.dtype)
    tcRefsUV = tcRefsXY / (float(hatTexture.shape[1]), float(hatTexture.shape[0]))
    tcRefsUV[:,1] = 1. - tcRefsUV[:,1]
    print tcRefsUV
    #tcRefsUV = pylab.array((tcRefsXY[0]/hatTexture.shape[1], 1.-tcRefsXY/hatTexture.shape[0]))
    
    tcRefsXYZ = pylab.ones((tcRefsUV.shape[0], 4), dtype=pylab.float64)
    for i in xrange(tcRefsUV.shape[0]):
        positions = hatObj.get_positions(tcRefsUV[i,0], tcRefsUV[i,1])
        print positions
        tcRefsXYZ[i,:3] = positions[0]
    return tcRefsXYZ

def calculate_skull_to_hat_matrix(hatRefs):
    # points are already in skull frame
    STT = vector.calculate_rigid_transform(hatRefs, cfg.tcRegPts)
    return pylab.matrix(STT)
# ====================================================================
# ======================  Analysis ===================================
# ====================================================================

# 1. load and fix skull scan
logging.debug('Loading and fixing skull scan')
skullObj, skullTexture = load_and_fix_scan('%s/%s' % (inDir, cfg.skullScan))

# 2. calculate scan-to-skull transformation matrix
logging.debug('Calculating scan-to-skull matrix')
bregmaLocation, bregmaNormal, bregmaToLambdaVector = find_skull_landmarks(skullObj, skullTexture, '%s/%s' % (inDir, cfg.skullScan))
scanToSkullMatrix = calculate_scan_to_skull_matrix(bregmaLocation, bregmaNormal, bregmaToLambdaVector)
logging.debug('\tMatrix:\n'+str(pylab.array(scanToSkullMatrix)))
pylab.savetxt(outDir+'/scanToSkullMatrix', scanToSkullMatrix)
pylab.savetxt(outDir+'/bregmaInScan', bregmaLocation)
pylab.savetxt(outDir+'/bregmaToLambda', bregmaToLambdaVector)
pylab.savetxt(outDir+'/bregmaNormal', bregmaNormal)

# 3. load and fix hat scan
logging.debug('Loading and fixing hat scan')
hatObj, hatTexture = load_and_fix_scan('%s/%s' % (inDir, cfg.hatScan))

# # 4. align skull and hat scans
# alignmentMatrix = align_objs_with_skull(hatObj, skullObj, fromTexture=hatTexture, toTexture=skullTexture)
# hatObj.apply_matrix(alignmentMatrix)

# 5. convert skull and hat scans to skull coordinates
logging.debug('Converting scans to skull coordinates')
skullObj.vertices = vector.apply_matrix_to_points(pylab.matrix(scanToSkullMatrix), skullObj.vertices)[:,:3]
hatObj.vertices = vector.apply_matrix_to_points(pylab.matrix(scanToSkullMatrix), hatObj.vertices)[:,:3]
# skullObj.apply_matrix(scanToSkullMatrix)
# hatObj.apply_matrix(scanToSkullMatrix)

logging.debug('Saving new meshes')
skullObj.save(outDir+'/skullInSkull.obj')
shutil.copyfile('%s/%s/%s' % (inDir, cfg.skullScan, cfg.skullTextureLocation), '%s/%s' % (outDir, '/skullInSkull.png'))
hatObj.save(outDir+'/hatInSkull.obj')
shutil.copyfile('%s/%s/%s' % (inDir, cfg.hatScan, cfg.skullTextureLocation), '%s/%s' % (outDir, '/hatInSkull.png'))

# 6. calculate skull-to-tricorner transformation matrix
logging.debug('Calculating skull-to-tricorner matrix')
hatRefs = find_hat_refs(hatObj, hatTexture, '%s/%s' % (inDir, cfg.hatScan))
skullToHatMatrix = calculate_skull_to_hat_matrix(hatRefs)
logging.debug('\tMatrix:\n'+str(pylab.array(skullToHatMatrix)))
pylab.savetxt(outDir+'/skullToHatMatrix', skullToHatMatrix)
pylab.savetxt(outDir+'/hatRefs', hatRefs)
# TODO save

# 7. load and fix final scan
logging.debug('Converting final scan to skull coordinates')
finalObj, finalTexture = load_and_fix_scan('%s/%s' % (inDir, cfg.finalScan))
finalObj.vertices = vector.apply_matrix_to_points(pylab.matrix(scanToSkullMatrix), finalObj.vertices)[:,:3]
finalObj.save(outDir+'/finalInSkull.obj')
shutil.copyfile('%s/%s/%s' % (inDir, cfg.finalScan, cfg.skullTextureLocation), '%s/%s' % (outDir, '/finalInSkull.png'))
# TODO
    # load ref mesh, calculate scaling matrix
    # load skull mesh, correct scaling matrix
    # find tricorner ref points
    # align this and the hat scan using ref points
    # convert skull mesh to skull coordinates (using scan-to-skull matrix)
    # save scan in skull coordinates