#!/usr/bin/env python
"""
Define a Scan object that supports:
 check_validity() : check files/dirs exist and scan is ready to run
"""

import logging, os, shutil, subprocess

import numpy, pylab
import PIL.Image as Image
from scikits import delaunay

import utilities.obj as obj
import utilities.vector as vector

def test(testFunc, testFile, lvl=logging.ERROR):
    if not testFunc(testFile):
        logging.log(lvl, "Test %s failed on %s" % (testFunc.__name__, testFile))
        return False
    return True

def xy_to_uv(xy,im):
    return xy[0]/im.shape[1], 1.-xy[1]/im.shape[0]

def crop_texture(o):
    """
    Load, and then crop an objects texture image, removing all un-referenced areas
    
    returns a texture of type PIL.Image
    """
    im = Image.open(o.textureFilename)
    w, h = im.size
    uvs = o.texCoords
    xys = numpy.zeros_like(uvs)
    xys[:,0] = uvs[:,0]*w
    xys[:,1] = h - uvs[:,1]*h
    
    xm, ym = (xys.min(0) - 2).astype(int)
    xM, yM = (xys.max(0) + 2).astype(int)
    
    cim = im.crop((xm,ym,xM,yM))
    
    cw, ch = cim.size
    cw = float(cw)
    ch = float(ch)
    
    o.texCoords[:,0] = (xys[:,0] - xm) / cw
    o.texCoords[:,1] = 1. - (xys[:,1] - ym) / ch
    
    return cim

def regen_faces(o):
    """
    Regenerate all the faces of a mesh using just the uv texture coordinates
    """
    tri = delaunay.Triangulation(o.texCoords[:,0], o.texCoords[:,1])

    o.faces = zeros((len(tri.triangle_nodes),3,3))
    o.faces[:,0,:] = tri.triangle_nodes
    o.faces[:,1,:] = tri.triangle_nodes
    return o

def simply(o):
    """
    simply a mesh
    """
    return o

class Scan(object):
    """
    Object that contains references to various files associated with a structured light scan
    """
    def __init__(self, cfg):
        """
        
        """
        self.cfg = cfg
    
    def __getattribute__(self, name):
        """Overload this so that scans are only loaded when needed"""
        # print name
        if (name[:2] == '__') or \
            (name in self.__dict__.keys() or \
            (name not in self.cfg.attrFuncMap.keys())):
            # this attribute does not invoke functions
            # or has been previously generated
            return object.__getattribute__(self, name)
        else:
            # call the associated function to generate the attribute
            object.__getattribute__(self, self.cfg.attrFuncMap[name]).__call__()
            # recall this function to get the attribute
            return self.__getattribute__(name)
        
        # try:
        #             return object.__getattribute__(self, name)
        #         except:
        #     if name not in ['skullObj', 'hatObj', 'finalObj']:
        #         try:
        #             return object.__getattribute__(self, name)
        #         except:
        #             logging.debug("Loading scan: %s" % name)
        #             self.__setattr__(name, self.load_scan(cfg.__getattribute__(name)))
        #             self.__getattribute__(name) # recall this function to return loaded value
        #     else:
        #         return object.__getattribute__(self, name)
    
    
    # ==============================================================================
    # =========================== Validity Checking ================================
    # ==============================================================================
    
    def check_scans(self):
        """ Check that each sub-scan is a directory and contains necessary files """
        for s in ['%s/%s/%s' % (self.cfg.scanDir,self.cfg.animal,s) for s in [self.cfg.skullScan, self.cfg.hatScan, self.cfg.finalScan]]:
            test(os.path.exists, s)
            test(os.path.isdir, s)
            
            for f in ['%s/%s.obj' % (s, f)
                        for f in [self.cfg.refName, self.cfg.skullName]]:
                test(os.path.exists, f)
                test(os.path.isfile, f)
            
            for f in ['%s/%s.png' % (s, f)
                        for f in [self.cfg.refName, self.cfg.skullName]]:
                if not test(os.path.exists, f, logging.WARNING):
                    logging.warning("%s did not exist, looking for jpg version" % f)
                    test(os.path.exists, os.path.splitext(f)[0] + '.jpg')
                    logging.debug("creating from jpg: %s" % f)
                    shutil.copyfile(os.path.splitext(f)[0] + '.jpg', f)
                test(os.path.isfile, f)
    
    def check_output(self):
        """ Check if output directory exists """
        if not test(os.path.exists, '/'.join([self.cfg.outputDir,self.cfg.animal]), logging.WARNING):
            logging.debug("Making output directory: %s" % self.cfg.outputDir)
            os.makedirs('/'.join([self.cfg.outputDir,self.cfg.animal]))
    
    def check_validity(self):
        self.check_scans()
        self.check_output()
    
    
    # ==============================================================================
    # =============================== Operations ===================================
    # ==============================================================================
    
    def load_obj(self, scan):
        o = obj.OBJ()
        prefix = '%s/%s/%s/%s' % (self.cfg.scanDir, self.cfg.animal, scan, self.cfg.skullName)
        o.load('%s.obj' % prefix, '%s.png' % prefix)
        o.frame = 'scan' # coordinate frame of mesh
        return o
    
    def load_skull_obj(self):
        self.skullObj = self.load_obj(self.cfg.skullScan)
    
    def load_hat_obj(self):
        self.hatObj = self.load_obj(self.cfg.hatScan)
    
    def load_final_obj(self):
        self.finalObj = self.load_obj(self.cfg.finalScan)
    
    def find_skull_refs(self):
        dataFilename = '%s/%s/%s' % (self.cfg.outputDir, self.cfg.animal, self.cfg.skullRefsXYName)
        if self.cfg.freshAnalysis or not test(os.path.exists, dataFilename):
            so = file(dataFilename, 'w')
            textureFilename = '%s/%s/%s/%s.png' % (self.cfg.scanDir, self.cfg.animal, self.cfg.skullScan, self.cfg.skullName)
            subprocess.Popen("python %s %s" % (self.cfg.zoomViewBin, textureFilename), shell=True, stdout=so).wait()
            so.close()
        
        bregmaXY, lambdaXY = pylab.loadtxt(dataFilename)
        if bregmaXY[1] < lambdaXY[1]: # bregma should ALWAYS be 'lower' in the image and have a HIGHER Y value
            logging.warning("bregma and lambda appeared switched, swapping positions...")
            t = bregmaXY
            bregmaXY = lambdaXY
            lambdaXY = bregmaXY
        
        # convert XY to uv
        skullTexture = pylab.imread('/'.join([self.cfg.scanDir,self.cfg.animal,self.cfg.skullScan,self.cfg.skullName])+'.png')
        bregmaUV = xy_to_uv(bregmaXY, skullTexture)
        lambdaUV = xy_to_uv(lambdaXY, skullTexture)
        
        self.bregmaXYZ = self.skullObj.get_positions(*bregmaUV)[0]
        self.lambdaXYZ = self.skullObj.get_positions(*lambdaUV)[0]
        
        self.bregmaNormal = self.skullObj.get_average_normal(self.bregmaXYZ, self.cfg.bregmaNormalMaxDistance)
        
        self.bregmaToLambdaVector = pylab.array(self.lambdaXYZ) - pylab.array(self.bregmaXYZ)
        self.bregmaToLambdaVector = self.bregmaToLambdaVector/pylab.norm(self.bregmaToLambdaVector)
    
    def find_hat_refs(self):
        dataFilename = '%s/%s/%s' % (self.cfg.outputDir, self.cfg.animal, self.cfg.hatRefsXYName)
        if self.cfg.freshAnalysis or not test(os.path.exists, dataFilename):
            so = file(dataFilename, 'w')
            textureFilename = '%s/%s/%s/%s.png' % (self.cfg.scanDir, self.cfg.animal, self.cfg.hatScan, self.cfg.skullName)
            subprocess.Popen("python %s %s" % (self.cfg.zoomViewBin, textureFilename), shell=True, stdout=so).wait()
            so.close()
        
        tcRefsXY = pylab.loadtxt(dataFilename)
        tcRefsXY = sorted(tcRefsXY, cmp=lambda l, r: cmp(l[0],r[0])) # sort by X
        hatTexture = pylab.imread('/'.join([self.cfg.scanDir,self.cfg.animal,self.cfg.hatScan,self.cfg.skullName])+'.png')
        
        self.tcRefsXYZ = pylab.ones((3, 4), dtype=pylab.float64)
        for i in xrange(3):
            tcRefUV = xy_to_uv(tcRefsXY[i], hatTexture)
            self.tcRefsXYZ[i,:3] = self.hatObj.get_positions(*tcRefUV)[0]
    
    def calculate_scan_to_skull_matrix(self):
        a1 = numpy.cross(-numpy.array(self.bregmaToLambdaVector), self.bregmaNormal)
        #a2 = numpy.cross(bNorm, a1)
        a2 = -numpy.array(self.bregmaToLambdaVector)
        #a3 = bNorm
        a3 = numpy.cross(a1,-numpy.array(self.bregmaToLambdaVector))
        #R = vector.rebase(numpy.cross(-numpy.array(bToLVec), bNorm), -numpy.array(bToLVec), bNorm)
        R = vector.rebase(a1, a2, a3)
        T = vector.translation_to_matrix(-self.bregmaXYZ[0],-self.bregmaXYZ[1],-self.bregmaXYZ[2])
        self.scanToSkull = vector.translate_and_rotate(T,R)
    
    def calculate_skull_to_hat_matrix(self):
        tcRefs_in_skull = vector.apply_matrix_to_points(self.scanToSkull,self.tcRefsXYZ)
        self.skullToHat = vector.calculate_rigid_transform(tcRefs_in_skull, self.cfg.tcRefPts)
    
    def calculate_scan_to_hat_matrix(self):
        self.scanToHat = vector.calculate_rigid_transform(self.tcRefsXYZ, self.cfg.tcRefPts)
    
    def convert_scans_to_skull_coordinates(self):
        for s in [self.skullObj, self.hatObj, self.finalObj]:
            if s.frame != 'skull':
                s.vertices = vector.apply_matrix_to_points(pylab.matrix(self.scanToSkull), s.vertices)[:,:3]
                s.frame == 'skull'
    
    # ==============================================================================
    # ================================= Saving =====================================
    # ==============================================================================
    def save(self):
        self.check_validity()
        
        save_it = lambda fn, ob : pylab.savetxt('/'.join([self.cfg.outputDir, self.cfg.animal, fn]), ob)
        
        for a in ['bregmaXYZ', 'lambdaXYZ', 'bregmaNormal', 'tcRefsXYZ',
                    'skullToHat', 'scanToHat', 'scanToSkull']:
            save_it(a,self.__getattribute__(a))
        
        # save converted scans
        self.convert_scans_to_skull_coordinates()
        for s, f  in [[self.skullObj,'skullInSkull'],
                        [self.hatObj, 'hatInSkull'],
                        [self.finalObj, 'finalInSkull']]:
            # crop and resave texture file
            ctex = crop_texture(s)
            s.save('/'.join([self.cfg.outputDir, self.cfg.animal, f])+'.obj')
            # TODO simplify mesh
            s = simplify(s)
            # regenerate faces
            s = regen_faces(s)
            s.save('/'.join([self.cfg.outputDir, self.cfg.animal, f])+'_remesh.obj')
            
            ctex.save('/'.join([self.cfg.outputDir, self.cfg.animal, f]) + '.png')
            ctex.save('/'.join([self.cfg.outputDir, self.cfg.animal, f]) + '.png')

if __name__ == '__main__':
    import cfg
    
    cfg.process_options() # process commandline
    
    scan = Scan(cfg) # load scan
    
    scan.save() # forces calculation of all necessary attributes