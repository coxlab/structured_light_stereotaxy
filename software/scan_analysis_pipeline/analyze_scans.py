#!/usr/bin/env python
"""
Define a Scan object that supports:
 check_validity() : check files/dirs exist and scan is ready to run
"""

import logging, os, shutil, subprocess, sys, tempfile

logging.basicConfig(level=logging.DEBUG)

import numpy, pylab

import utilities.obj as obj
import utilities.vector as vector

# ----- operations -----
# 1) remesh
# 2) simplify
# 3) find refs
# 4) calc transforms
# 5) save

# ----- structures ------
# 3 skull objs (& textures)
# 3 ref objs (actually FUCKING use these)
# various points in 2d and 3d frames
# transformations between 3d frames

# ----- options -----
# scan numbers (skull, hat, final)
# scan directory
#   usage : <cmd> <scandir> <skullI> <hatI> <finalI>

# ----- pipeline -----
# 1) parse options
# 2) open structures
# 3) clean/analyze
# 3a) for each mesh: remesh -> simplify -> find refs
# 3b) calc transforms
# 3c) save

global zoomviewbin
zoomviewbin = 'panZoom.py'
global bregmaNormalMaxDistance
bregmaNormalMaxDistance = 1.0
global tcRefPts
tcRefPts = []
for y in xrange(5):
    for x in xrange(9):
        tcRefPts.append([x,y,0.,1.])
tcRefPts = numpy.array(tcRefPts)

def xy_to_uv(xy,im):
    return xy[0]/im.shape[1], 1.-xy[1]/im.shape[0]

def load(scandir, scanIndex):
    skull = obj.OBJ()
    skull.load('%s/Scan0%i/skull.obj' % (scandir, scanIndex))
    ref = obj.OBJ()
    ref.load('%s/Scan0%i/ref.obj' % (scandir, scanIndex))
    return skull, ref

def remesh(obj):
    obj.regen_faces()

def crop_texture(obj, outputFilename):
    cim = obj.crop_texture()
    # save cim
    cim.save(outputFilename)
    # fix obj.textureFilename
    obj.textureFilename = outputFilename

def simplify(o):
    """
    simply a mesh
    """
    logging.warning("Skipping, never seems to work")
    return o
    try:
        # save to temp dir
        #outputFilename = os.path.splitext(o.objFilename)[0] + "_simple.obj"
        #cmd = "%s -i %s -o %s -s %s" % ("meshlabserver", o.objFilename, outputFilename, "simplify.mlx")
        tempDir = tempfile.mkdtemp()
        infile = "%s/temp.obj" % tempDir
        outfile = "%s/temp_simple.obj" % tempDir
        o.save("%s/temp.obj" % tempDir) # temp.obj temp.png
        cmd = "meshlabserver -i %s -o%s -s simplify.mlx" % (infile, outfile)
        logging.debug("Running: %s" % cmd)
        subprocess.Popen(cmd).wait()
        logging.debug("Command finished")
        return obj.OBJ(outfile, o.textureFilename)
        #return o.load(outputFilename, o.textureFilename)
    except Exception as E:
        logging.error("Simplifcation failed, skipping [%s]" % str(E))
    return o

def load_ref_points(dataFilename):
    points = pylab.loadtxt(dataFilename)

    # get size
    f = open(dataFilename,'r')
    f.readline()
    l = f.readline()
    imsize = [float(v) for v in l.split('(')[-1].split(')')[-2].split(',')]
    
    # convert to uv
    points[:,0] /= imsize[0]
    points[:,1] = 1. - points[:,1]/imsize[1]

    return points

def find_refs(obj, dataFilename):
    """Find reference points in UV coordinates"""
    if not os.path.exists(dataFilename):
        global zoomviewbin
        so = file(dataFilename, 'w')
        obj.textureFilename
        subprocess.Popen("python %s %s" % (zoomviewbin, obj.textureFilename), shell = True, stdout = so).wait()
        so.close()
    return load_ref_points(dataFilename)

def calculate_scan_to_skull_matrix(skullObj, skullRefsUV):
    if skullRefsUV[0][1] < skullRefsUV[1][1]: # point 0 is 'lower' in image
        bregmaUV = skullRefsUV[0]
        lambdaUV = skullRefsUV[1]
    else:
        bregmaUV = skullRefsUV[1]
        lambdaUV = skullRefsUV[0]

    logging.debug("B_UV: %f %f" % (bregmaUV[0], bregmaUV[1]))
    logging.debug("L_UV: %f %f" % (lambdaUV[0], lambdaUV[1]))
    
    bregmaXYZ = skullObj.get_positions(*bregmaUV)[0]
    lambdaXYZ = skullObj.get_positions(*lambdaUV)[0]
    
    global bregmaNormalMaxDistance
    bregmaNormal = skullObj.get_average_normal(bregmaXYZ, bregmaNormalMaxDistance)
        
    bregmaToLambdaVector = pylab.array(lambdaXYZ) - pylab.array(bregmaXYZ)
    # order skullrefs
    a1 = numpy.cross(-numpy.array(bregmaToLambdaVector), bregmaNormal)
    a1 /= pylab.norm(a1)
    #a2 = numpy.cross(bNorm, a1)
    a2 = -numpy.array(bregmaToLambdaVector)
    a2 /= pylab.norm(a2)
    #a3 = bNorm
    a3 = numpy.cross(a1,-numpy.array(bregmaToLambdaVector))
    a3 /= pylab.norm(a3)
    #R = vector.rebase(numpy.cross(-numpy.array(bToLVec), bNorm), -numpy.array(bToLVec), bNorm)
    R = vector.rebase(a1, a2, a3)
    T = vector.translation_to_matrix(-bregmaXYZ[0],-bregmaXYZ[1],-bregmaXYZ[2])
    scanToSkull = vector.translate_and_rotate(T,R)
    skullRefsXYZ = numpy.ones((2,4),dtype=numpy.float64)
    skullRefsXYZ[0,:3] = bregmaXYZ
    skullRefsXYZ[1,:3] = lambdaXYZ
    return scanToSkull, skullRefsXYZ, (a1, a2, a3)

def calculate_skull_to_hat_matrix(hatObj, tcRefsUV, scanToSkull):
    # order tcRefs
    # V+ is up
    # U+ is right
    # order right to left and bottom to top
    # first sort by Y
    tcRefsUV = tcRefsUV[numpy.argsort(tcRefsUV[:,1])]
    npts = numpy.zeros_like(tcRefsUV)
    for v in xrange(5):
        row = tcRefsUV[v*9:(v+1)*9]
        #print row
        row = row[numpy.argsort(row[:,0])[::-1]]
        npts[v*9:(v+1)*9] = row
    tcRefsUV = npts
    
    # convert UV to XYZ
    goodPts = []
    tcRefsXYZ = []
    for (i,uv) in enumerate(tcRefsUV):
        ps = hatObj.get_positions(*uv)
        if len(ps):
            tcRefsXYZ.append(ps[0])
            goodPts.append(i)
        else:
            logging.debug("failed to find hat ref at uv: %s" % str(uv))
        #tcRefsXYZ.append(hatObj.get_positions(*uv)[0])
    tcRefsXYZ = numpy.array(tcRefsXYZ)
    logging.debug("Good hat ref indices: %s" % str(goodPts))
    goodPts = numpy.array(goodPts)

    tcRefs_in_skull = vector.apply_matrix_to_points(scanToSkull,tcRefsXYZ)
    global tcRefPts
    tcRefPts = numpy.array(tcRefPts)[goodPts]
    skullToHat, fitR = vector.calculate_rigid_transform(tcRefs_in_skull, tcRefPts)
    #skullToHat, fitR = vector.calculate_rigid_transform(tcRefs_in_skull, tcRefPts)
    return skullToHat, tcRefsXYZ, tcRefs_in_skull, fitR

def calculate_scan_to_hat_matrix(self):
    raise NotImplemented
    self.scanToHat = vector.calculate_rigid_transform(self.tcRefsXYZ, self.cfg.tcRefPts)

def convert_scans_to_skull_coordinates(self):
    raise NotImplemented
    for s in [self.skullObj, self.hatObj, self.finalObj]:
        if s.frame != 'skull':
            s.vertices = vector.apply_matrix_to_points(pylab.matrix(self.scanToSkull), s.vertices)[:,:3]
            s.frame == 'skull'

def convert_mesh_to_skull(s, scanToSkull):
    s.vertices = vector.apply_matrix_to_points(pylab.matrix(scanToSkull), s.vertices)[:,:3]

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    if len(sys.argv) < 5:
        print "Usage: %s <scandir> <skullScanIndex> <hatI> <finalI>" % __file__
        sys.exit(1)
    
    scanDir, skullI, hatI, finalI = sys.argv[1:5]
    skullI = int(skullI)
    hatI = int(hatI)
    finalI = int(finalI)
    if len(sys.argv) == 6:
        outDir = sys.argv[5]
    else:
        outDir = "output"

    if not (os.path.exists(outDir)):
        os.makedirs(outDir)
    # load refs and get scaling factors?
    # TODO
    #skullRef = obj.OBJ("%s/Scan%02i/ref.obj" % (scanDir, skullI))
    #hatRef = obj.OBJ("%s/Scan%02i/ref.obj" % (scanDir, hatI))
    #finalRef = obj.OBJ("%s/Scan%02i/ref.obj" % (scanDir, finalI))
    
    # load OBJs, Remesh, and get ref points
    logging.debug("Opening skull scan")
    skullObj = obj.OBJ("%s/Scan%02i/skull.obj" % (scanDir, skullI))
    remesh(skullObj)
    crop_texture(skullObj, "%s/skull.png" % outDir)
    skullObjSimple = simplify(skullObj)
    refFile = "%s/skullrefsUV" % outDir
    if not os.path.exists(refFile):
        skullRefs = find_refs(skullObjSimple, refFile)
    else:
        skullRefs = load_ref_points(refFile)
    
    logging.debug("calculating scan to skull")
    scanToSkull, skullRefsXYZ, bases = calculate_scan_to_skull_matrix(skullObjSimple, skullRefs)
    pylab.savetxt("%s/scanToSkull" % outDir, scanToSkull)
    pylab.savetxt("%s/skullRefs" % outDir, skullRefsXYZ)
    skullRefs_inskull = vector.apply_matrix_to_points(pylab.matrix(scanToSkull), skullRefsXYZ)
    pylab.savetxt("%s/skullRefsInSkull" % outDir, skullRefs_inskull)
    pylab.savetxt("%s/bases" % outDir, pylab.vstack(bases).T) # each column is a vector
    logging.debug("converting skull to skull")
    convert_mesh_to_skull(skullObjSimple, scanToSkull)
    logging.debug("saving skull")
    skullObjSimple.save("%s/skullInSkull.obj" % outDir)
    
    logging.debug("Opening hat scan")
    hatObj = obj.OBJ("%s/Scan%02i/skull.obj" % (scanDir, hatI))
    remesh(hatObj)
    crop_texture(hatObj, "%s/hat.png" % outDir)
    hatObjSimple = simplify(hatObj)
    refFile = "%s/hatrefsUV" % outDir
    if not os.path.exists(refFile):
        hatRefs = find_refs(hatObjSimple, refFile)
    else:
        hatRefs = load_ref_points(refFile)
    
    logging.debug("calculating hat to skull")
    skullToHat, hatRefsXYZ, hatRefs_inskull, fitR = calculate_skull_to_hat_matrix(hatObjSimple, hatRefs, scanToSkull)
    pylab.savetxt("%s/skullToHat" % outDir, skullToHat)
    global tcRefPts
    pylab.savetxt("%s/tcRefPts" % outDir, tcRefPts)
    pylab.savetxt("%s/tcRefsInScan" % outDir, hatRefsXYZ)
    pylab.savetxt("%s/tcRefsInSkull" % outDir, hatRefs_inskull)
    logging.debug("converting hat to skull")
    convert_mesh_to_skull(hatObjSimple, scanToSkull)
    logging.debug("saving hat")
    hatObjSimple.save("%s/hatInSkull.obj" % outDir)
    
    logging.debug("Opening final scan")
    finalObj = obj.OBJ("%s/Scan%02i/skull.obj" % (scanDir, finalI))
    remesh(finalObj)
    crop_texture(finalObj, "%s/final.png" % outDir)
    finalObjSimple = simplify(finalObj)
    refFile = "%s/finalrefsUV" % outDir
    if not os.path.exists(refFile):
        finalRefs = find_refs(finalObjSimple, refFile)
    else:
        finalRefs = load_ref_points(refFile)
    logging.debug("converting final to skull")
    convert_mesh_to_skull(finalObjSimple, scanToSkull)
    logging.debug("saving final")
    finalObjSimple.save("%s/finalInSkull.obj" % outDir)

    # save fitting results
    #print fitR
    #cov_x, infodict, mesg, ier = fitR
    #print "ier:", ier
    #print "mesg:", mesg
    #print "infodict::"
    #print infodict
    #pylab.savetxt("cov_x", cov_x)
    
# --------------------------------------------------------------
# --------------------------------------------------------------
# -----------------------   OLD   ------------------------------
# --------------------------------------------------------------
# --------------------------------------------------------------
