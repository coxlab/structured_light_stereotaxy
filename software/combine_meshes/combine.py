#!/usr/bin/env python

import os, sys

from pylab import *
import PIL.Image as Image

from bjg.obj import OBJ
from bjg.vector import make_homogeneous

baseDir = 'data/H7'
#meshFiles = ['%s/skullInSkull.obj' % baseDir, '%s/hatInSkull.obj' % baseDir]
meshFiles = ['%s/skullInSkull_cropped.obj' % baseDir, '%s/hatInSkull_cropped.obj' % baseDir, '%s/finalInSkull_cropped.obj' % baseDir]
#meshFiles = ['%s/%s' % (baseDir, f) for f in os.listdir(baseDir) if '.obj' in f]
#textureFiles = ['%s/skullInSkull.png' % baseDir, '%s/hatInSkull.png' % baseDir]
textureFiles = ['%s/skullInSkull.png' % baseDir, '%s/hatInSkull.png' % baseDir, '%s/finalInSkull.png' % baseDir]
#textureFiles = ['%s/%s' % (baseDir, f) for f in os.listdir(baseDir) if '.png' in f]

combinedMeshname = '%s/%s' % (baseDir, 'combined.obj')
combinedTexturename = '%s/%s' % (baseDir, 'combined.png')

# -- find the tallest texture, that will be the height of the final texture
textures = [Image.open(f) for f in textureFiles]
heights = [t.size[1] for t in textures]
widths = [t.size[0] for t in textures]
#print widths, heights
maxHeight = max(heights)

# -- calculate the total width of all the textures combined
totalWidth = sum(widths)
textureSize = (totalWidth, maxHeight)

# -- generate a mapping for each texture from old coordinates to new coordinate (offset, scale)
textureMappings = []
currentX = 0
for (w,h) in zip(widths,heights):
    xoffset = currentX / float(totalWidth)
    xscale = w / float(totalWidth)
    yoffset = 0.
    yscale = h / float(maxHeight)
    textureMappings.append([xoffset, xscale, yoffset, yscale])
    currentX += w

# -- write out combined texture
combinedTexture = Image.new(textures[0].mode, (totalWidth, maxHeight))
currentX = 0
for t in textures:
    combinedTexture.paste(t.crop((0,0,t.size[0],t.size[1])), (currentX, maxHeight-t.size[1], currentX+t.size[0], maxHeight))
    currentX += t.size[0]
combinedTexture.save(combinedTexturename)

# -- open objs, fix texture coordinates, and combine
combinedMesh = OBJ()
nPoints = 0 # we're assuming that len(texCoords) == len(vertices)
for (meshFile, textureMapping) in zip(meshFiles,textureMappings):
    mesh = OBJ()
    mesh.load(meshFile)
    if len(mesh.texCoords) != len(mesh.vertices):
        print "len(texCoords) != len(vertices) for mesh: %s" % meshFile
        raise Exception, "len(texCoords) != len(vertices) for mesh: %s" % meshFile
    combinedMesh.vertices = vstack((combinedMesh.vertices, mesh.vertices))
    combinedMesh.normals = vstack((combinedMesh.normals, mesh.normals))
    combinedMesh.faces = vstack((combinedMesh.faces, mesh.faces + nPoints)) # accounting for previous vertices and texCoords
    xoffset, xscale, yoffset, yscale = textureMapping
    newTexCoords = make_homogeneous(mesh.texCoords) * matrix([ [xscale, 0, 0], [0, yscale, 0], [xoffset, yoffset, 1] ])
    newTexCoords = array(newTexCoords[:,:2]) # convert from matrix to array
    combinedMesh.texCoords = vstack((combinedMesh.texCoords, newTexCoords))
    nPoints += newTexCoords.shape[0]
    del mesh
combinedMesh.save(combinedMeshname)
