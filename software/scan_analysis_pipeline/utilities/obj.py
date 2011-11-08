#!/usr/bin/env python

import time, os, shutil

import numpy
import pylab

from scikits import delaunay
import PIL.Image as Image

import vector

class OBJ:
    def __init__(self, fn=None, tx=None):
        self.vertices = numpy.transpose(numpy.array([[],[],[]]))
        self.normals = numpy.transpose(numpy.array([[],[],[]]))
        self.texCoords = numpy.transpose(numpy.array([[],[]]))
        self.faces = numpy.transpose(numpy.array([[[],[],[]],[[],[],[]],[[],[],[]]]))
        self.textureFilename = None
        self.objFilename = None
        if not (fn is None):
            self.load(fn, tx)
    def load(self, filename, textureFilename = None):
        self.objFilename = filename
        self.textureFilename = textureFilename
        if self.textureFilename is None:
            # guess textureFilename
            bn = os.path.splitext(filename)[0]
            if os.path.exists(bn + '.png'):
                self.textureFilename = bn + '.png'
            #elif os.path.exists(bn + '.jpg'): # don't automatically load jpgs
            #    self.textureFilename = bn + '.jpg'

        self.vertices = numpy.fromregex(filename,
                    r"v\s+([\d,.,-]+)\s+([\d,.,-]+)\s+([\d,.,-]+)",
                    (numpy.float64, 3))
        #self.normals = numpy.fromregex(filename,
        #            r"vn\s+([\d,.,-]+)\s+([\d,.,-]+)\s+([\d,.,-]+)",
        #            (numpy.float64, 3))
        self.texCoords = numpy.fromregex(filename,
                    r"vt\s+([\d,.,-]+)\s+([\d,.,-]+)",
                    (numpy.float64, 2))
        if len(self.texCoords) == 0:
            if len(self.normals) == 0:
                tf = numpy.fromregex(filename,
                    r"f\s+([\d]+)\s+([\d]+)\s+([\d]+)",
                    (numpy.int64, 3))
                self.faces = numpy.zeros((len(tf),3,3))
                self.faces[:,0,:] = tf - 1 # vertices
            else:
                tf = numpy.fromregex(filename,
                    r"f\s+([\d]+)/[.*?]/([\d]+)\s+([\d]+)/[.*?]/([\d]+)\s+([\d]+)/[.*?]/([\d]+)",
                    (numpy.int64, 6))
                self.faces = numpy.zeros((len(tf),3,3))
                self.faces[:,0,:] = tf[:,::2] - 1 # vertices
                self.faces[:,1,:] = tf[:,1::2] - 1 # normals
        else:
            if len(self.normals) == 0:
                tf = numpy.fromregex(filename,
                    r"f\s+([\d]+)/([\d]+)\s+([\d]+)/([\d]+)\s+([\d]+)/([\d]+)",
                    (numpy.int64, 6))
                self.faces = numpy.zeros((len(tf),3,3))
                self.faces[:,0,:] = tf[:,::2] - 1 # vertices
                self.faces[:,2,:] = tf[:,1::2] - 1 # texCoords
            else:
                tf = numpy.fromregex(filename,
                    r"f\s+([\d]+)/([\d]+)/([\d]+)\s+([\d]+)/([\d]+)/([\d]+)\s+([\d]+)/([\d]+)/([\d]+)",
                    (numpy.int64, 9))
                self.faces = numpy.zeros((len(tf),3,3))
                self.faces[:,0,:] = tf[:,::3] - 1 # vertices
                self.faces[:,1,:] = tf[:,2::3] - 1 # normals
                self.faces[:,2,:] = tf[:,1::3] - 1 # texCoords
        # self.faces = numpy.fromregex(filename,
        #             r"f\s+([\d]+)/([\d]+)\s+([\d]+)/([\d]+)\s+([\d]+)/([\d]+)",
        #             [('v1', numpy.int64), ('t1', numpy.int64),
        #                             ('v2', numpy.int64), ('t2', numpy.int64),
        #                             ('v3', numpy.int64), ('t3', numpy.int64)])
        # zf = numpy.zeros((len(self.faces),3,3))
        # zf[:,0,:] = numpy.transpose(numpy.vstack((self.faces['v1'],self.faces['v2'],self.faces['v3']))) - 1
        # zf[:,1,:] = numpy.transpose(numpy.vstack((self.faces['t1'],self.faces['t2'],self.faces['t3']))) - 1
        
        # rearrange faces to be [[[v1,v2,v3],[n1,n2,n3],[t1,t2,t3]],...]
        
        # for line in open(filename, 'r'):
        #     if line.startswith('#'): continue
        #     values = line.split()
        #     if not values: continue
        #     if values[0] == 'v': # vertex found
        #         # TODO clock this
        #         self.vertices.append(map(float, values[1:4]))
        #     elif values[0] == 'vn': # normal found
        #         self.normals.append(map(float, values[1:4]))
        #     elif values[0] == 'vt': # texture coordinate found
        #         self.texCoords.append(map(float, values[1:3]))
        #     elif values[0] == 'f':
        #         face = []
        #         texcoords = []
        #         norms = []
        #         for v in values[1:]:
        #             w = v.split('/')
        #             face.append(int(w[0])-1)
        #             if len(w) >= 2 and len(w[1]) > 0:
        #                 texcoords.append(int(w[1])-1)
        #             else:
        #                 texcoords.append(0)
        #             if len(w) >=3 and len(w[2]) > 0:
        #                 norms.append(int(w[2]))
        #             else:
        #                 norms.append(0)
        #         if len(face) == 3:
        #             self.faces.append((face, norms, texcoords))
        
        # self.vertices = numpy.array(self.vertices) # 3d positions (x,y,z)
        # self.normals = numpy.array(self.normals) # 3d normals (_,_,_)
        # self.texCoords = numpy.array(self.texCoords) # 2d coordinate (u,v)
        # self.faces = numpy.array(self.faces) # list of indices:
        if len(self.vertices) == 0:
            self.vertices = numpy.transpose(numpy.array([[],[],[]]))
        if len(self.normals) == 0:
            self.normals = numpy.transpose(numpy.array([[],[],[]]))
        if len(self.texCoords) == 0:
            self.texCoords = numpy.transpose(numpy.array([[],[]]))
        if len(self.faces) == 0:
            self.faces = numpy.transpose(numpy.array([[[],[],[]],[[],[],[]],[[],[],[]]]))
        #   face[0] = (p1, p2, p3)
        #   face[1] = (n1, n2, n3)
        #   face[2] = (t1, t2, t3)
    
    def crop_texture(self):
        im = Image.open(self.textureFilename)
        w, h = im.size
        uvs = self.texCoords
        xys = numpy.zeros_like(uvs)
        xys[:,0] = uvs[:,0]*w
        xys[:,1] = h - uvs[:,1]*h

        xm, ym = (xys.min(0) - 2).astype(int)
        xM, yM = (xys.max(0) + 2).astype(int)

        cim = im.crop((xm,ym,xM,yM))
        cw, ch = cim.size
        cw = float(cw)
        ch = float(ch)

        self.texCoords[:,0] = (xys[:,0] - xm) / cw
        self.texCoords[:,1] = 1. - (xys[:,1] - ym) / ch

        return cim

    def regen_faces(self):
        tri = delaunay.Triangulation(self.texCoords[:,0], self.texCoords[:,1])
        self.faces = numpy.zeros((len(tri.triangle_nodes),3,3))
        self.faces[:,0,:] = tri.triangle_nodes
        self.faces[:,1,:] = tri.triangle_nodes
        self.faces[:,2,:] = tri.triangle_nodes
    

    def center_mean(self):
        self.vertices = self.vertices - numpy.mean(self.vertices, 0)
    
    
    def scale(self, x=1., y=1., z=1.):
        self.transform(vector.scale_to_matrix(x,y,z))
    
    
    def transform(self, P):
        """Apply a 4x4 transformation matrix to the vertices"""
        for (i, v) in enumerate(self.vertices):
            nv = numpy.ones(4)
            nv[:3] = v
            nv = numpy.matrix(nv) * P
            self.vertices[i] = numpy.array(nv)[0][:3]
    
    
    def save(self, outputFile):
        o = open(outputFile, 'w')
        if len(self.vertices) != 0:
            for v in self.vertices:
                o.write("v %f %f %f\n" % (v[0], v[1], v[2]))
        if len(self.texCoords) != 0:
            for t in self.texCoords:
                o.write("vt %f %f\n" % (t[0], t[1]))
        if len(self.normals) != 0:
            for n in self.normals:
                o.write("vn %f %f %f\n" % (n[0], n[1], n[2]))
        if len(self.faces) != 0:
            if len(self.texCoords) != 0:
                if len(self.normals) != 0:
                    for f in self.faces:
                        # f p1/t1/n1 ...
                        o.write("f %i/%i/%i %i/%i/%i %i/%i/%i\n" % (f[0][0]+1, f[2][0]+1, f[1][0]+1, f[0][1]+1, f[2][1]+1, f[1][1]+1, f[0][2]+1, f[2][2]+1, f[1][2]+1))
                else:
                    for f in self.faces:
                        # f p1/t1 ...
                        o.write("f %i/%i %i/%i %i/%i\n" % (f[0][0]+1, f[2][0]+1, f[0][1]+1, f[2][1]+1, f[0][2]+1, f[2][2]+1))
            else:
                for f in self.faces:
                    # f p1 ...
                    o.write("f %i %i %i\n" % (f[0][0]+1, f[0][1]+1, f[0][2]+1))
        o.close()

        # copy over texture filename
        if not (self.textureFilename is None):
            base, _ = os.path.splitext(outputFile)
            _, ext = os.path.splitext(self.textureFilename)
            shutil.copyfile(self.textureFilename, base + ext)
    
    def save_as_pov(self, outputFile):
        o = open(outputFile, 'w')
        o.write("#declare ObjMesh = mesh2 {\n")
        
        o.write("vertex_vectors{ %i " % len(self.vertices))
        for v in self.vertices:
            o.write("<%0.2f,%0.2f,%0.2f>" % tuple(v))
        o.write("}\n")
        
        o.write("uv_vectors{ %i "% len(self.texCoords))
        for t in self.texCoords:
            o.write("<%0.4f,%0.4f>" % tuple(t))
        o.write("}\n")
        
        #o.write('texture_list { 1 texture {pigment{uv_mapping image_map{jpeg "texture.jpg"}}}}')
        
        o.write("face_indices{ %i " % len(self.faces))
        for f in self.faces:
            o.write("<%i,%i,%i>" % tuple(f[0]))
        o.write("}\n")
        
        o.write("uv_indices{ %i " % len(self.faces))
        for f in self.faces:
            o.write("<%i,%i,%i>" % tuple(f[2]))
        o.write("}\n")
        
        o.write('}')
        #o.write('pigment{image_map {jpeg "texture.jpg"}}}')
        
        #o.write('background{color rgb<0.0,0.0,0.0>}\nobject{ObjMesh}\n')
        #o.write('camera{location <0,0,20> look_at <0,0,-1>}\n')
        #o.write('light_source{ <0,0,10> color rgb<1.0,1.0,1.0>}')
        
        o.close()
        
        # use something like this to render the pov file
        # -----
        # #include "test.pov"
        # background{ color rgb<0.5, 0.5, 0.5> }
        # object{ ObjMesh texture{ pigment{ uv_mapping image_map {jpeg "texture.jpg"}}} }
        # camera{ location <0,0,-400> look_at <0,0,-1000> }
        # light_source{ <0,0,10> color rgb<1.0,1.0,1.0> }
        # ------
    
    
    def find_uv(self, u, v):
        # texCoords consider 0,0 to be bottom left
        # get index of closest value in self.texCoords
        P = numpy.array([u,v])
        closest = numpy.sum((self.texCoords - P)**2, 1).argmin()
        #print "Testing: u:%f, v:%f" % (u,v)
        #print "Closest texCoord(%i)" % closest, self.texCoords[closest]
        # find faces that contain it
        faceIndices = numpy.where(self.faces[:,2,:] == closest)[0]
        #print "Found faceIndices:"
        #print faceIndices
        inFaces = []
        # find which face actually contains the given u, v coordinates
        for i in faceIndices:
            # test if face contains u,v
            # calculate barycentric coordinates [nu, nv]
            # http://www.blackpawn.com/texts/pointinpoly/default.html
            A = self.texCoords[self.faces[i][2][0]]
            B = self.texCoords[self.faces[i][2][1]]
            C = self.texCoords[self.faces[i][2][2]]
            #print A, B, C
            
            v0 = C - A
            v1 = B - A
            v2 = P - A
            
            #print v0, v1, v2
            
            dot00 = numpy.dot(v0, v0)
            dot01 = numpy.dot(v0, v1)
            dot02 = numpy.dot(v0, v2)
            dot11 = numpy.dot(v1, v1)
            dot12 = numpy.dot(v1, v2)
            
            invDenom = 1. / (dot00 * dot11 - dot01 * dot01)
            nu = (dot11 * dot02 - dot01 * dot12) * invDenom
            nv = (dot00 * dot12 - dot01 * dot02) * invDenom
            
            #print i, nu, nv
            
            if (nu >= 0) and (nv >= 0) and (nu + nv <= 1.):
                inFaces.append(i)
        return inFaces
    
    
    def get_positions(self, u, v, faceIndices=None):
        """faceIndices may be of variable length"""
        if faceIndices == None:
            faceIndices = self.find_uv(u, v)
        
        #positions = numpy.array([0., 0., 0.])
        positions = []
        
        for fi in faceIndices:
            uv1 = self.texCoords[self.faces[fi][2][0]]
            uv2 = self.texCoords[self.faces[fi][2][1]]
            uv3 = self.texCoords[self.faces[fi][2][2]]
            uv = numpy.array([u,v])
            
            # calculate distace of point from vertices
            d1 = sum((uv - uv1)**2)
            d2 = sum((uv - uv2)**2)
            d3 = sum((uv - uv3)**2)
            d = d1 + d2 + d3
            d1 = d1/d
            d2 = d2/d
            d3 = d3/d
            
            # use distances as weights to calc position using weighted average
            p1 = self.vertices[self.faces[fi][0][0]]
            p2 = self.vertices[self.faces[fi][0][1]]
            p3 = self.vertices[self.faces[fi][0][2]]
            p = p1 * d1 + p2 * d2 + p3 * d3
            #print p
            positions.append(p)
        return positions
    
    
    def get_normals(self, u, v, faceIndices=None):
        """faceIndices may be of variable length"""
        if faceIndices == None:
            faceIndices = self.find_uv(u, v)
        
        #normals = numpy.array([0., 0., 0.])
        normals = []
        
        for fi in faceIndices:
            # don't assume the face normal is valid
            normals.append(vector.calculate_normal(self.vertices[self.faces[fi][0][0]],
                            self.vertices[self.faces[fi][0][1]],
                            self.vertices[self.faces[fi][0][2]]))
        
        return normals
    
    
    def get_average_position(self, position, maxDistance):
        squaredMaxDist = maxDistance ** 2
        nPoints = 0
        avgPosition = numpy.array([0., 0., 0.])
        for p in self.vertices:
            d = numpy.sum((position - p) ** 2)
            if d < squaredMaxDist:
                avgPosition += position
                nPoints += 1
        return avgPosition / float(nPoints)
    
    
    def get_average_normal(self, position, maxDistance):
        squaredMaxDist = maxDistance ** 2
        closePoints = []
        for i in xrange(len(self.vertices)):
            d = numpy.sum((position - self.vertices[i]) ** 2)
            if d < squaredMaxDist:
                closePoints.append(i)
        
        closeFaces = []
        for f in self.faces:
            if all([p in closePoints for p in f[0]]):
                closeFaces.append(f)
        
        nFaces = len(closeFaces)
        normal = numpy.array([0., 0., 0.])
        for f in closeFaces:
            normal += numpy.array(vector.calculate_normal(self.vertices[f[0][0]],
                            self.vertices[f[0][1]],
                            self.vertices[f[0][2]]))
        normal /= nFaces
        return normal/pylab.norm(normal)
    
    def apply_mask(self, maskFilename, threshold=128):
        mask = numpy.mean(pylab.imread(maskFilename),2)
        newFaces = []
        for f in self.faces:
            for tc in (self.texCoords[f[2][0]], self.texCoords[f[2][1]], self.texCoords[f[2][2]]):
                u = tc[0] * mask.shape[1]
                v = tc[1] * mask.shape[0]
                if mask[v,u] >= threshold:
                    newFaces.append(f)
                    break
        self.faces = numpy.array(newFaces)
        self.remove_unused_points()
    
    def remove_unused_points(self):
        """remove all points and uv coordinates not used in faces"""
        # current format of face: f %i/%i %i/%i %i/%i\n with vi/ti (vertex index and texture index)
        # generate dictionary of used faces and texture indexes
        usedVs = {}
        for f in self.faces:
            usedVs[f[0][0]] = 1
            usedVs[f[0][1]] = 1
            usedVs[f[0][2]] = 1
        
        oldV = usedVs.keys()
        oldV.sort()
        
        for (i,v) in enumerate(oldV):
            usedVs[v] = i
        
        for i in xrange(len(self.faces)):
            self.faces[i][0][0] = usedVs[self.faces[i][0][0]]
            self.faces[i][0][1] = usedVs[self.faces[i][0][1]]
            self.faces[i][0][2] = usedVs[self.faces[i][0][2]]
        
        newVs = []
        for v in oldV:
            newVs.append(self.vertices[v])
        self.vertices = numpy.array(newVs)
        
        if len(self.texCoords) > 0:
            #usedVs = {}
            usedTs = {}
            for f in self.faces:
                # f = ( (v1, v2, v3), (n1, n2, n3), (t1, t2, t3) )
                #usedVs[f[0][0]] = 1
                #usedVs[f[0][1]] = 1
                #usedVs[f[0][2]] = 1
                usedTs[f[2][0]] = 1
                usedTs[f[2][1]] = 1
                usedTs[f[2][2]] = 1
            
            #oldV = usedVs.keys()
            #oldV.sort()
            oldT = usedTs.keys()
            oldT.sort()
            
            #for (i,v) in enumerate(oldV):
            #    usedVs[v] = i
            for (i,t) in enumerate(oldT):
                usedTs[t] = i
            
            for i in xrange(len(self.faces)):
                #self.faces[i][0][0] = usedVs[self.faces[i][0][0]]
                #self.faces[i][0][1] = usedVs[self.faces[i][0][1]]
                #self.faces[i][0][2] = usedVs[self.faces[i][0][2]]
                
                self.faces[i][2][0] = usedTs[self.faces[i][2][0]]
                self.faces[i][2][1] = usedTs[self.faces[i][2][1]]
                self.faces[i][2][2] = usedTs[self.faces[i][2][2]]
            
            #newVs = []
            #for v in oldV:
            #    newVs.append(self.vertices[v])
            newTs = []
            for t in oldT:
                newTs.append(self.texCoords[t])
            
            #self.vertices = array(newVs)
            self.texCoords = numpy.array(newTs)
            #self.normals = array([])
        
        if len(self.normals) > 0:
            usedsNs = {}
            for f in self.faces:
                usedNs[f[1][0]] = 1
                usedNs[f[1][1]] = 1
                usedNs[f[1][2]] = 1
            
            oldN = usedNs.keys()
            oldN.sort()
            
            for (i,n) in enumerate(oldN):
                usedNs[n] = i
            
            for i in xrange(len(self.faces)):
                self.faces[i][1][0] = usedNs[self.faces[i][1][0]]
                self.faces[i][1][1] = usedNs[self.faces[i][1][1]]
                self.faces[i][1][2] = usedNs[self.faces[i][1][2]]
            
            newNs = []
            for n in oldN:
                newNs.append(self.normals[n])
            self.normals = numpy.array(newNs)


if __name__ == '__main__':
    # # clock this sucker on many files
    # # one small: 43303
    # fsizes = [43303, 4222622, 7809958]
    # fnames = ['meshes/simple.obj', 'meshes/scan5.obj', 'meshes/mesh.obj']
    # tnames = ['meshes/texture.jpg', 'meshes/scan5.jpg', 'meshes/texture.jpg']
    # N = len(fsizes)
    # sizes = []
    # times = []
    # objs = []
    # assert(len(fsizes) == len(fnames) == len(tnames))
    # for s, f, t in zip(fsizes, fnames, tnames):
    #     loadTime = time.time()
    #     o = OBJ(f,t)
    #     loadTime = time.time() - loadTime
    #     objs.append(o)
    #     print "%s\t%i\t%f" % (f, s, loadTime)
    #     sizes.append(s)
    #     times.append(loadTime)
    # pylab.plot(sizes,times)
    # pylab.xlabel('Filesize(bytes)')
    # pylab.ylabel('LoadTime(seconds)')
    # pylab.show()
    obj = OBJ()
    obj.load('meshes/simple.obj', 'meshes/textures.jpg')
    u = 2022./3875.
    v = 1. - (1590./2592.)
    inFaces = obj.find_uv(u, v)
    pylab.figure(1)
    def plot_face(obj, faceIndex):
        t = obj.faces[i][2]
        xs = numpy.array([obj.texCoords[t[0]][0],
                obj.texCoords[t[1]][0],
                obj.texCoords[t[2]][0],
                obj.texCoords[t[0]][0]])
        ys = numpy.array([obj.texCoords[t[0]][1],
                obj.texCoords[t[1]][1],
                obj.texCoords[t[2]][1],
                obj.texCoords[t[0]][1]])
        pylab.plot(xs, ys, c='b')
        
        pylab.text(numpy.mean(xs), numpy.mean(ys), "%i" % faceIndex)
    for i in inFaces:
        plot_face(obj, i)
    pylab.scatter([u], [v], c='r')
    
    from mpl_toolkits.mplot3d import Axes3D
    f = pylab.figure(2)
    ax = Axes3D(f)
    normals = obj.get_normals(u, v, inFaces)
    positions = obj.get_positions(u, v, inFaces)
    
    for i in xrange(len(inFaces)):
        # plot face
        f = obj.faces[inFaces[i]]
        p1 = obj.vertices[f[0][0]]
        p2 = obj.vertices[f[0][1]]
        p3 = obj.vertices[f[0][2]]
        ax.scatter([p1[0], p2[0], p3[0]], [p1[1], p2[1], p3[1]], [p1[2], p2[2], p3[2]], c='b')
        ax.plot([p1[0], p2[0], p3[0], p1[0]], [p1[1], p2[1], p3[1], p1[1]], [p1[2], p2[2], p3[2], p1[2]], c='b')
        
        # plot normal
        #m = numpy.mean([p1,p2,p3], 0)
        p = positions[i]
        n = normals[i]
        print "position:", p
        print "normal:", n
        #print n
        n += p
        ax.scatter([p[0]], [p[1]], [p[2]], c='r')
        ax.plot([p[0], n[0]], [p[1], n[1]], [p[2], n[2]], c='r')
    
    #f = pylab.figure(3)
    #ax = Axes3D(f)
    position = positions[0]
    avgPos = obj.get_average_position(position, 1.)
    avgNorm = obj.get_average_normal(position, 1.)
    ax.scatter([avgPos[0]], [avgPos[1]], [avgPos[2]], c='g')
    n = avgPos + avgNorm
    ax.plot([avgPos[0], n[0]], [avgPos[1], n[1]], [avgPos[2], n[2]], c='g')
    
    pylab.show()
    
